from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from rest_framework import serializers
from datetime import datetime
from .models import StockData
from django.contrib.auth.password_validation import validate_password
from . import custom_validators
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _


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
    """

    # return staff status of requester
    user = User  # user attr (User obj) set on request in views.py, get_queryset() method
    user_is_admin = serializers.SerializerMethodField(method_name='administrators_check')

    def administrators_check(self, obj):
        return self.user.groups.filter(name='administrators').exists()

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
                  'units_total', 'unit_price', 'user_is_admin',
                  'datetime_of_request')

    """
    Additional validations. 
    Data param is dict of unvalidated fields.
    Note, model validations are passed as validators to serializer validation, so
    most validation here is done on the model.
    """

    # def validate(self, data):
    #     # e.g below: if instance exists (thus updating) & new value for units_total different, raise error
    #     if self.instance and data.get('units_total', None) != self.instance.units_total:
    #         raise serializers.ValidationError('You are trying to update with a new value!')
    #     return data

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
                # raise serializers.ValidationError(detail=f'Record update denied for this user level')
                del validated_data[k]  # rather than throw error, simply delete keys from update if unauthorized
            # only allow superusers to INCREASE units_total
            if 'units_total' in validated_data and not self.administrators_check(self) and \
                    int(validated_data['units_total']) > instance.units_total:
                raise serializers.ValidationError(detail=f'Only administrators may increase stock!')
        # identify as update (not new record) for purpose of email generation in post_save signal
        instance.update = True
        # add request user to instance, to pass to post_save callback for email
        instance.user = self.user
        # pass transferred total for email
        instance.transferred = instance.units_total - int(validated_data['units_total'])
        if instance.transferred < instance.units_total:  # if not trying to transfer more than the remaining stock
            # call parent method to do the update
            super().update(instance, validated_data)
            # return the updated instance
            return instance
        else:
            raise serializers.ValidationError(detail=f'Stock levels must not fall below 0!')
