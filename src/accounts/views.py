from django.shortcuts import render
from django.http import JsonResponse
import logging
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from rest_framework import (viewsets, permissions, serializers, status)
from rest_framework.decorators import action
from rest_framework.response import Response
from .custom_validators import RequestQueryValidator, validate_search
from .serializers import (AccountStockDataSerializer)
from .models import AccountStockData
from .custom_permissions import AccessPermissions
from django.db.models import Q
from email_service.email import SendEmail
from django_q.tasks import async_task, result

# Get an instance of a logger
logger = logging.getLogger('django')

class AccountStockDataViewSet(viewsets.ModelViewSet):
    """
    API endpoints for StockData
    """

    """
    Includes by default the ListCreateAPIView & RetrieveUpdateDestroyAPIView
    i.e. provides stockdata-list and stockdata-detail views, accessed by path, & path/<id>)
    """
    queryset = AccountStockData.objects.all()
    serializer_class = AccountStockDataSerializer
    permission_classes = (AccessPermissions,)

    """
    Note on permissions:
    Access control is dealt with in 2 places: here (views.py) and serializers.py.
    
        - views.py: basic 1st hurdle checks, performed before input validation, 
        including whether requester user level has access to models, and whether has ability to 
        preform actions on model objects. This is via permission_classes 
        (may call access permissions classes from ./custom_permissions.py or default access permission 
        classes from DRF.
        
        - serializers.py: 2nd hurdle checks - more complicated checks performed after input validation 
        but before changes committed to the model. E.g. ensuring only certain user levels are able 
        to update specific fields in certain ways.    
    """

    def get_queryset(self):
        records = []
        try:
            """
            - only return records for the current user account
            - order queryset using request query (or 'id' by default if no order_by query)
            """
            records = self.queryset.filter(owner=self.request.user).order_by(RequestQueryValidator.validate(
                RequestQueryValidator.order_by, self.request.query_params.get(
                    'order_by', None)
            ))
            # set username of requester to user attr of serializer to allow return admin status in response
            self.serializer_class.user = self.request.user
            # if searching for a product by description
            try:
                if 'desc' in self.request.query_params and self.request.query_params.get('desc', None):
                    search_query = validate_search(
                        self.request.query_params.get('desc'))
                    records = records.filter(Q(desc__icontains=search_query) | Q(sku__icontains=search_query)
                                             if search_query else None)
            except ValidationError as e:
                # if invalid search char, don't return error response, just return empty
                logger.info(f'Returning no results in response because: {e}')
        except Exception as e:
            logger.error(f'An error occurred whilst getting the queryset: {e}')
        return records  # return everything

    # """
    # Custom actions
    # """

    @staticmethod
    def serialize_model_instance(instance=None):
        return {
            'id': instance.id,
            'record_created': instance.record_created,
            'record_updated': instance.record_updated,
            'sku': instance.sku,
            'desc': instance.desc,
            'units_total': instance.units_total,
            'xfer_price': instance.xfer_price,
            'selling_price': instance.selling_price,
            'opening_stock': instance.opening_stock,
            'closing_stock': instance.closing_stock,
        } if instance else None

    def take_stock(self, request):
        """
        method to perform the stock taking functions
        """
        stock_data = self.get_queryset().filter(owner=request.user).values_list('running_total_xfer_value', flat=True)
        async_task(stock_taker, stock_data=stock_data)
        return JsonResponse({'success': True}, status=status.HTTP_200_OK)

    @staticmethod
    def stock_taker(stock_data:queryset) -> bool:
        logger.info(f'Taking stock!')
        return True

    @action(methods=['patch'], detail=True)
    def perform_single_update(self, request, pk):
        """
        Use a custom action rather than call perform_update direct, to allow data to be
        nicely formatted to pass to email method
        """
        err = []
        record = request.data
        updated_record = {}
        user_is_admin = request.user.groups.filter(name='administrators').exists()
        try:
            instance = self.get_queryset().get(id=pk)
            """Control what staff are allowed to update.
            By default, administrators (e.g. warehouse admins) allowed to update everything, staff (e.g.
            store managers) only what's in staff_allowed_to_update list
            """
            for k in list(record.keys()):
                if k not in AccountStockData.STAFF_ALLOWED_TO_UPDATE and not user_is_admin:
                    raise serializers.ValidationError(
                        detail=f'Record update denied for this user level')
                    # del validated_data[k]  # OR, rather than throw error, simply delete keys from update if unauthorized
            serializer = self.get_serializer(
                data=record, instance=instance, partial=True)
            serializer.is_valid(raise_exception=True)
            saved = serializer.save()
            updated_record = self.serialize_model_instance(instance=saved)
        except AccountStockData.DoesNotExist as e:
            err.append(str(e))
        except serializers.ValidationError as e:
            err.append(e.detail)
        except KeyError as e:
            err.append('Request data list was empty! Perhaps the record id was incorrect or missing.')
        except Exception as e:
            err.append(f'An unspecified error occurred whilst attempting to update: {str(e)}')
        if not err:
            result = {'success': True, 'error': None, 'user_is_admin': user_is_admin,
                      'data': updated_record}  # return updated data
        else:
            result = {'success': False, 'error': err, 'user_is_admin': user_is_admin,
                      'data': record}  # return original data
        try:
            self.dispatch_email(records=[result], user=request.user)  # dispatch email
        except Exception as e:
            logger.error(f'An error occurred whilst attempting to send email: {e}')
        return Response(result, status=status.HTTP_400_BAD_REQUEST if not result['success'] else status.HTTP_200_OK)

    @action(methods=['patch'], detail=True)
    def perform_bulk_partial_update(self, request):
        """
        Custom method to receive & process stock updates in bulk.
        Route: /api/v1/stock/ (with no id in path, as is the case for updates on single items)
        """
        data = request.data.get('records') if 'records' in request.data else []
        result = []
        updated_record = None
        user_is_admin = request.user.groups.filter(name='administrators').exists()
        for record in data:
            err = []
            try:  # get the existing record from StockRecord model
                instance = self.get_queryset().get(id=record['id'])
            except (AccountStockData.DoesNotExist, Exception) as e:  # if the record did not exist
                instance = None
                err.append(str(e))
                result.append({'success': False, 'error': err, 'data': {}})
            if instance:  # if the existing record instance did exist in the StockRecord model
                try:
                    """Control what staff are allowed to update.
                    By default, administrators (e.g. warehouse admins) allowed to update everything, staff (e.g.
                    store managers) only what's in staff_allowed_to_update list
                    """
                    for k in list(record.keys()):
                        if k not in AccountStockData.STAFF_ALLOWED_TO_UPDATE and not user_is_admin:
                            # raise serializers.ValidationError(
                            #     detail=f'Record update denied for this user level')
                            del record[k]  # OR, rather than throw error, simply delete keys from update if unauthorized
                    serializer = self.get_serializer(data=record, instance=instance, partial=True)
                    serializer.is_valid(raise_exception=True)
                    saved = serializer.save()
                    updated_record = self.serialize_model_instance(instance=saved)
                except serializers.ValidationError as e:
                    err.append(e.detail)
                except KeyError as e:
                    err.append('Request data list was empty! Perhaps the record id was incorrect or missing.')
                except Exception as e:
                    err.append(f'An unspecified error occurred whilst attempting to update: {str(e)}')
                if not err:
                    result.append({'success': True, 'error': None, 'data': updated_record})
                else:
                    record = {'id': instance.id,
                              'record_created': instance.record_created,
                              'record_updated': instance.record_updated,
                              'sku': instance.sku,
                              'desc': instance.desc,
                              'units_total': instance.units_total,
                              'xfer_price': instance.xfer_price,
                              'selling_price': instance.selling_price,
                              'opening_stock': instance.opening_stock}
                    result.append({'success': False, 'error': err, 'data': record})
                del instance  # delete the instance
        if data:  # if data was submitted, dispatch transaction confirmation email
            try:
                self.dispatch_email(records=result, user=request.user)
            except Exception as e:
                logger.error(f'An error occurred whilst attempting to send email: {e}')
        return Response(result, status=status.HTTP_400_BAD_REQUEST if not data else status.HTTP_200_OK)

    @staticmethod
    def dispatch_email(records=None, user=None):
        """
        method to dispatch email on successful update
        """
        email_notify = (records and len(records) > 0)  # only notify if updated records exist
        if email_notify:
            SendEmail().compose(records=records,
                                user=user, notification_type=SendEmail.EmailType.ACCOUNT_STOCK_UPDATE)
