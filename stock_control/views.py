__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

import logging
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from rest_framework import (viewsets, permissions, serializers, status)
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .custom_validators import RequestQueryValidator, validate_search
from .serializers import (
    UserSerializer,
    GroupSerializer,
    StockDataSerializer,
    ChangePasswordSerializer
)
from .models import StockData
from .custom_permissions import AccessPermissions
from django.db.models import Q
from email_service.email import SendEmail

"""
Note about data object (database record):
Record referenced by URL param can be accessed in create & update methods through: self.get_object()

Note about permissions:
If viewset passed into class is ModelViewSet rather than a permission restricted one such as
ReadOnlyModelViewset, then permission classes can be set within the class,
via the 'permission_classes' class attribute.

Permissions classes include:
    Defaults: permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly, permissions.IsAdmin
    My custom: IsOwnerOrReadOnly

Need to be put in a set, e.g. permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly).
If only one, leave trailing comma e.g.(permissions.IsAuthentication,)
"""

# Get an instance of a logger
logger = logging.getLogger('django')


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoints for users
    """

    """
    Includes by default the ListCreateAPIView & RetrieveUpdateDestroyAPIView
    (i.e. provides users-list and users-detail views, accessed by path, & path/<id>).
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # overrides default perm level, set in settings.py
    permission_classes = (permissions.IsAdminUser,)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAdminUser,)


class PasswordUpdateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for updating password
    """
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = (AccessPermissions,)
    lookup_field = 'username'

    def perform_update(self, serializer):
        """
        override perform_update to perform any additional filtering, modification, etc
        """
        super().perform_update(serializer)


class Logout(APIView):
    def post(self, request, format=None):
        logger.info(request.user)
        try:
            # delete the token to force a login
            request.user.auth_token.delete()
            return Response({
                'success': True,
                'logged_in': False,
                'error': None,
                'user_is_admin': False},
                status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({
                'success': False,
                'logged_in': True,
                'error': str(e),
                'user_is_admin': False
            },
                status=status.HTTP_400_BAD_REQUEST)


class StockDataViewSet(viewsets.ModelViewSet):
    """
    API endpoints for StockData
    """

    """
    Includes by default the ListCreateAPIView & RetrieveUpdateDestroyAPIView
    i.e. provides stockdata-list and stockdata-detail views, accessed by path, & path/<id>)
    """
    queryset = StockData.objects.all()
    serializer_class = StockDataSerializer
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
        # order queryset using request query (or 'id' by default if no order_by query)
        records = self.queryset.order_by(RequestQueryValidator.validate(
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
            records = []
        return records  # return everything

    def perform_create(self, serializer_class):
        """
        override perform_create to save the user as the owner of the record
        """
        serializer_class.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        override perform_update to perform any additional filtering, modification, etc
        """
        super().perform_update(serializer)  # call to parent method to save the update

    def perform_destroy(self, instance):
        # only allow admins to delete objects
        if self.request.user.groups.filter(name='administrators').exists():
            super().perform_destroy(instance)
        else:
            raise serializers.ValidationError(
                detail='You are not authorized to delete stock lines!')

    """
    Custom actions
    """

    @staticmethod
    def serialize_model_instance(instance=None):
        return {
            'id': instance.id,
            'record_created': instance.record_created,
            'record_updated': instance.record_updated,
            'sku': instance.sku,
            'desc': instance.desc,
            'units_total': instance.units_total,
            'unit_price': instance.unit_price,
        } if instance else None

    @action(methods=['get'], detail=False)
    def latest(self, request):
        """
        example of a custom defined action, mapped to GET request. Defined in routes as /api/v1/latest/.
        This method returns the latest record added to the database.
        """
        latest = self.get_queryset().order_by('record_created').last()
        serializer = self.get_serializer_class()(
            latest, context={'request': request})
        return Response(serializer.data)

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
        transfer = False
        try:
            instance = self.get_queryset().get(id=pk)
            # add requester for post_save signal accounts db update
            instance.requester = request.user
            serializer = self.get_serializer(
                data=record, instance=instance, partial=True)
            # set this for dispatch_email()
            transfer = 'units_to_transfer' in serializer.initial_data
            serializer.is_valid(raise_exception=True)
            saved = serializer.save()
            updated_record = self.serialize_model_instance(instance=saved)
            updated_record['units_to_transfer'] = int(
                serializer.initial_data['units_to_transfer']) if transfer else 0
        except StockData.DoesNotExist as e:
            err.append(str(e))
        except serializers.ValidationError as e:
            err.append(e.detail[0])
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
        try:
            self.dispatch_email(
                records=[result], user=request.user, transfer=transfer)  # dispatch email
        except Exception as e:
            logger.error(
                f'An error occurred whilst attempting to send email: {e}')
        return Response(result, status=status.HTTP_400_BAD_REQUEST if not result['success'] else status.HTTP_200_OK)

    @action(methods=['patch'], detail=True)
    def perform_bulk_partial_update(self, request):
        """
        Custom method to receive & process stock unit updates in bulk.
        Route: /api/v1/stock/ (with no id in path, as is the case for updates on single items)
        """
        data = request.data.get('records') if 'records' in request.data else []
        result = []
        updated_record = None
        transfer = False
        units_to_transfer = 0
        for record in data:
            err = []
            try:  # get the existing record from StockRecord model
                instance = self.get_queryset().get(id=int(record['id']))
            except (StockData.DoesNotExist, Exception) as e:  # if the record did not exist
                instance = None
                err.append(str(e))
                result.append({'success': False, 'error': err, 'data': {}})
            if instance:  # if the existing record instance did exist in the StockRecord model
                try:
                    # add requester for post_save signal accounts db update
                    instance.requester = request.user
                    serializer = self.get_serializer(
                        data=record, instance=instance, partial=True)
                    if 'units_to_transfer' in serializer.initial_data:
                        # set these variables for dispatch_email()
                        transfer = True
                        units_to_transfer = int(
                            serializer.initial_data['units_to_transfer'])
                    serializer.is_valid(raise_exception=True)
                    saved = serializer.save()
                    # update record to return in http response
                    updated_record = self.serialize_model_instance(
                        instance=saved)
                    updated_record['units_to_transfer'] = int(
                        serializer.initial_data['units_to_transfer']) if transfer else 0
                except serializers.ValidationError as e:
                    err.append(e.detail[0])
                except KeyError as e:
                    err.append(
                        'Request data list was empty! Perhaps the record id was incorrect or missing.')
                except Exception as e:
                    err.append(
                        f'An unspecified error occurred whilst attempting to update: {str(e)}')
                if not err:
                    result.append(
                        {'success': True, 'error': None, 'data': updated_record})
                else:
                    record = {'id': instance.id, 'record_created': instance.record_created,
                              'record_updated': instance.record_updated, 'sku': instance.sku,
                              'desc': instance.desc, 'units_total': instance.units_total,
                              'unit_price': instance.unit_price, 'units_to_transfer': units_to_transfer}
                    result.append(
                        {'success': False, 'error': err, 'data': record})
                del instance  # delete the instance
        if data:  # if data was submitted, dispatch transaction confirmation email
            try:
                self.dispatch_email(
                    records=result, user=request.user, transfer=transfer)
            except Exception as e:
                logger.error(
                    f'An error occurred whilst attempting to send email: {e}')
        return Response(result, status=status.HTTP_400_BAD_REQUEST if not data else status.HTTP_200_OK)

    @staticmethod
    def dispatch_email(records=None, transfer=False, user=None):
        """
        method to dispatch email on successful update if transferring
        """
        email_notify_on_transfer = (records and len(records) > 0) and transfer
        if email_notify_on_transfer:
            SendEmail().compose(records=records,
                                user=user, notification_type=SendEmail.EmailType.STOCK_TRANSFER)
