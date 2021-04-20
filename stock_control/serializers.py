__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

import logging
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from rest_framework import serializers
from datetime import datetime
from .models import StockData
from django.contrib.auth.password_validation import validate_password
from . import custom_validators
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

# Get an instance of a logger
logger = logging.getLogger('django')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    note: because StockData is a reverse relationship on the User model,
    it will not be included by default when using the ModelSerializer class,
    so we needed to add an explicit field for it.
    """
    stock_data = serializers.HyperlinkedRelatedField(
        many=True, view_name='stockdata-detail', read_only=True,
        lookup_field='pk')  # auto generated view_name is model name + '-detail'.

    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups', 'stock_data')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ChangePasswordSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for password change endpoint. Note: self.instance is the user object for the
    requester (ModelViewSet (in views.py) sets queryset as User model objects, and grabs
    the correct instance to update from the user ID passed as a URL path param.
    """

    """
    define the extra incoming "non-model" fields.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'old_password', 'new_password')

    """
    field validations (in the form validate_a_custom_field)
    """

    def validate_old_password(self, value):
        validate_password(value, user=self.instance)  # validate it is a real, acceptable pw
        return value

    def validate_new_password(self, value):
        validate_password(value, user=self.instance)
        return value

    """
    update method
    """

    def update(self, instance, validated_data):
        """
        overwrite update method if need to do extra stuff pre-save
        """

        """
        custom validations
        """
        try:
            custom_validators.validate_passwords_different(
                [validated_data['old_password'], validated_data['new_password']]
            )  # check old & new different

            custom_validators.validate_password_correct(user=instance,  # check old is valid
                                                        value=validated_data['old_password'])
        except ValidationError as e:
            raise serializers.ValidationError(f'Error: {e}')

        instance.set_password(validated_data['new_password'])
        instance.save()
        # remove password from instance, replaced with 'CHANGED' str (for client ref) & return the instance as response
        instance.password = 'CHANGED'
        return instance


class StockDataSerializer(serializers.HyperlinkedModelSerializer):
    """
    Stock data serializer
    """

    """
    Any special attributes to add to fields (e.g. if want to make it read-only)
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    id = serializers.ReadOnlyField()

    """
    Any custom fields (non-model)
    FYI, details of how to process a non-model field in the request, here: https://stackoverflow.com/a/37718821
    """

    # return staff status of requester
    user_is_admin = serializers.SerializerMethodField(method_name='administrators_check')

    def administrators_check(self, obj):
        return self.context['request'].user.groups.filter(name='administrators').exists()

    # receive non-model field in request POST/PATCH that represents the number of units to transfer
    units_to_transfer = serializers.CharField(required=False)
    # allow non-model field for requesting user (already added as attribute of instance in views.py, read_only as non-model field)
    requester = serializers.CharField(read_only=True)

    # def superuser_check(self, obj):
    #     return self.user.is_superuser

    # return request datetime
    datetime_of_request = serializers.SerializerMethodField(method_name='create_request_time')

    def create_request_time(self, obj):
        # return datetime.utcnow().strftime('%d %b %Y, %H:%M:%S UTC')
        return datetime.utcnow()

    class Meta:
        model = StockData
        fields = ('id', 'record_updated', 'owner', 'sku', 'desc',
                  'units_total', 'unit_price', 'user_is_admin', 'requester',
                  'datetime_of_request', 'units_to_transfer')

    """
    Additional validations. 
    Data param is dict of unvalidated fields.
    Note, model validations are passed as validators to serializer validation, so
    most validation here is done on the model.
    Non-model fields may be validated here.
    """

    # def validate(self, data):
    #     # e.g below: if instance exists (thus updating) & new value for units_total different, raise error
    #     if self.instance and data.get('units_total', None) != self.instance.units_total:
    #         raise serializers.ValidationError('You are trying to update with a new value!')
    #     return data

    def validate(self, data):
        logger.info('Running clean on serializer')
        """
        validate units_to_transfer (a non-model field), on update (hence test for self.instance), if it's present
        """
        if self.instance and 'units_to_transfer' in data:
            try:
                int(data.get('units_to_transfer'))
            except ValueError as e:
                raise serializers.ValidationError(f'Error: units_to_transfer was not a valid number!')
        return data

    """
    create or update
    """

    def create(self, validated_data):
        """
        overwrite create method if need to do extra stuff pre-save
        """

        """
        Only superusers are allowed to create new objects
        """
        if not self.administrators_check(self):
            raise serializers.ValidationError(detail=f'Record creation denied for this user level')
        # remove units_to_transfer write_only (non-model) field for the create() method (only for updates)
        if 'units_to_transfer' in validated_data:
            del validated_data['units_to_transfer']
        try:
            super().create(validated_data)  # now call parent method to do the save
            return self.validated_data
        except IntegrityError as i:
            raise serializers.ValidationError(detail=f'{i}')

    def update(self, instance, validated_data):
        """
        overwrite update method if need to do extra stuff pre-save
        """
        """
        Control what superusers and staff are allowed to update.
        By default, administrators (e.g. warehouse admins) allowed to update everything, staff (e.g.
        store managers) only what's in staff_allowed_to_update list
        """
        for k in list(validated_data.keys()):
            if k not in StockData.STAFF_ALLOWED_TO_UPDATE and not self.administrators_check(self):
                raise serializers.ValidationError(detail=f'Record update denied for this user level')
                # del validated_data[k]  # OR, rather than throw error, simply delete keys from update if unauthorized
            # allow only superusers to INCREASE units_total
            if 'units_total' in validated_data and not self.administrators_check(self) and \
                    int(validated_data['units_total']) > instance.units_total:
                raise serializers.ValidationError(detail=f'Only administrators may increase stock!')
        if 'units_to_transfer' in validated_data:
            transfer = int(validated_data['units_to_transfer'])  # how many to transfer
            # if transferring stock, calculate the new number and also ensure it doesn't fall below 0
            if transfer <= instance.units_total:
                """calculate & set the remaining stock on the instance 
                (needs to be done manually, as units_to_transfer wasn't a model field)"""
                instance.units_total -= transfer
            else:
                raise serializers.ValidationError(detail=f'Stock levels must not fall below 0!')
        # call parent method to do the update
        super().update(instance, validated_data)
        # return the updated instance
        return instance
