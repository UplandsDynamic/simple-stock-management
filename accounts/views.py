__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

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
from decimal import Decimal, ROUND_HALF_UP
from django_q.tasks import async_task, result
from django.db.models import Q
from .stock_taker import stock_taker

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
    sterling = Decimal('0.01')

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
            records = self.queryset.order_by(RequestQueryValidator.validate(
                RequestQueryValidator.order_by, self.request.query_params.get(
                    'order_by', None)
            ))
            # only return results for user's account
            records = records.filter(owner=self.request.user)
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

    # Default create, update, delete actions

    def perform_create(self, serializer_class):
        """
        override perform_create to save the user as the owner of the record
        """
        serializer_class.save(owner=self.request.user)

    # def perform_update(self, serializer):
    #     """
    #     override perform_update to perform any additional filtering, modification, etc
    #     """
    #     super().perform_update(serializer)  # call to parent method to save the update

    def perform_destroy(self, instance):
        # only allow admins to delete objects
        if self.request.user.groups.filter(name='administrators').exists():
            super().perform_destroy(instance)
        else:
            raise serializers.ValidationError(
                detail='You are not authorized to delete account stock lines!')

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
            'selling_price': instance.selling_price,
            'xfer_price': instance.xfer_price,
            'xferred_units': instance.xferred_units,
            'sold_units': instance.sold_units,
            'shrinkage': instance.shrinkage,
            'opening_stock': instance.opening_stock,
            'running_total_xfer_value': instance.running_total_xfer_value,
            'running_total_sold_value': instance.running_total_sold_value,
            'running_total_shrinkage_value': instance.running_total_shrinkage_value,
            'all_time_total_xfer_value': instance.all_time_total_xfer_value
        } if instance else None

    def take_stock(self, request):
        """
        method to perform the stock taking functions
        """
        stock_data = self.get_queryset().filter(owner=request.user)
        if stock_data:
            # lock user until stock take process is complete
            User.objects.filter(id=request.user.id).update(is_active=False)
            async_task(stock_taker, stock_data=stock_data,
                       hook=AccountStockDataViewSet.take_stock_callback)
            return JsonResponse({'success': True}, status=status.HTTP_200_OK)
        return JsonResponse({'success': False}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @staticmethod
    def take_stock_callback(task):
        if task.result['success'] and task.result['user']:
            User.objects.filter(
                id=task.result['user'].id).update(is_active=True)
        else:
            logger.error(f'User account locked due to failed stock take.')

    @action(methods=['patch'], detail=True)
    def perform_single_update(self, request, pk):
        """
        Use a custom action rather than call perform_update direct, to allow data to be
        nicely formatted to pass to email method
        """
        err = []
        record = request.data
        updated_record = {}
        user_is_admin = request.user.groups.filter(
            name='administrators').exists()
        try:
            instance = self.get_queryset().get(id=pk)
            """Control what staff are allowed to update.
            By default, administrators (e.g. warehouse admins) allowed to update everything, staff (e.g.
            store managers) only what's in staff_allowed_to_update list
            """
            # do initial validation of incoming data
            serializer = self.get_serializer(data=record, instance=instance, partial=True)
            serializer.is_valid(raise_exception=True)
            # ensure user has authorization to update fields
            for k in list(serializer.validated_data.keys()):
                if k not in AccountStockData.STAFF_ALLOWED_TO_UPDATE and not user_is_admin:
                    # raise serializers.ValidationError(
                    #     detail=f'Record update denied for this user level')
                    # OR, rather than throw error, simply delete keys from update if unauthorized
                    del serializer.validated_data[k]
            # adjust units & running totals for units recorded sold (if any)
            if 'sold_units' in serializer.validated_data:
                sold_units = int(serializer.validated_data['sold_units'])
                # increment sold units rather than just overwrite with latest request
                serializer.validated_data['sold_units'] = instance.sold_units + sold_units
                # decrement units_total accordingly
                serializer.validated_data['units_total'] -= sold_units
                serializer.validated_data['running_total_sold_value'] = instance.running_total_sold_value + Decimal(
                    sold_units * instance.selling_price).quantize(self.sterling, ROUND_HALF_UP)  # add to running sold total
            # adjust units & running totals for units recorded shrunk (if any)
            if 'shrinkage' in serializer.validated_data:
                shrinkage = int(serializer.validated_data['shrinkage'])
                # increment sold units rather than just overwrite with latest request
                serializer.validated_data['shrinkage'] = shrinkage + instance.shrinkage
                # decrement units_total accordingly
                serializer.validated_data['units_total'] -= shrinkage
                # update running total value
                serializer.validated_data['running_total_shrinkage_value'] = instance.running_total_shrinkage_value + Decimal(
                    shrinkage * instance.selling_price).quantize(self.sterling, ROUND_HALF_UP)  # add to running sold total
            # ensure still valid following data changes
            serializer.is_valid(raise_exception=True)
            saved = serializer.save()
            updated_record = self.serialize_model_instance(instance=saved)
        except AccountStockData.DoesNotExist as e:
            err.append(str(e))
        except serializers.ValidationError as e:
            err.append(e.detail)
        except KeyError as e:
            err.append(
                'Request data list was empty! Perhaps the record id was incorrect or missing.')
        except Exception as e:
            err.append(
                f'An unspecified error occurred whilst attempting to update: {str(e)}')
        if not err:
            result = {'success': True, 'error': None, 'user_is_admin': user_is_admin,
                      'data': updated_record}  # return updated data
        else:
            result = {'success': False, 'error': err, 'user_is_admin': user_is_admin,
                      'data': record}  # return original data
        return Response(result, status=status.HTTP_400_BAD_REQUEST if not result['success'] else status.HTTP_200_OK)
