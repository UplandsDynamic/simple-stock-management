import logging
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from rest_framework import (viewsets, permissions, serializers)
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
    permission_classes = (permissions.IsAdminUser,)  # overrides default perm level, set in settings.py


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
            RequestQueryValidator.order_by, self.request.query_params.get('order_by', None)
        ))
        # set username of requester to user attr of serializer to allow return admin status in response
        self.serializer_class.user = self.request.user
        # if searching for a product by description
        try:
            if 'desc' in self.request.query_params and self.request.query_params.get('desc', None):
                search_query = validate_search(self.request.query_params.get('desc'))
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
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        # only allow admins to delete objects
        if self.request.user.groups.filter(name='administrators').exists():
            super().perform_destroy(instance)
        else:
            raise serializers.ValidationError(detail='You are not authorized to delete stock lines!')

    @action(methods=['get'], detail=False)
    def latest(self, request):
        """
        example of a custom defined action, mapped to GET request. Defined in routes as /api/v1/latest/.
        This method returns the latest record added to the database.
        """
        latest = self.get_queryset().order_by('record_created').last()
        serializer = self.get_serializer_class()(latest, context={'request': request})
        return Response(serializer.data)
