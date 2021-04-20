__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

from django.db import models
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . import custom_validators
import logging
from accounts.models import AccountStockData
from django.db.models import F
from decimal import Decimal, ROUND_HALF_UP

# Get an instance of a logger
logger = logging.getLogger('django')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Signal receiver to automatically create auth token for new users.
    Placed here as needs to be imported and run by Django on startup,
    and all model.py modules are.
    """
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender='stock_control.StockData')
def transfer_to_account(sender, instance=None, created=False, **kwargs):
    """
    Signal receiver to update accounts.model with the data for the user
    """
    # transfer to transfer's store account if a shop manager (i.e. units_to_transfer exists & not an administrator)
    sterling = Decimal('0.01')
    try:
        if hasattr(instance, 'units_to_transfer') \
                and not instance.requester.groups.filter(name='administrators').exists():
            record, created = AccountStockData.objects.update_or_create(
                owner=instance.requester,
                sku=instance.sku,
                defaults={
                    'desc': instance.desc,
                    'xfer_price': instance.unit_price,
                }
            )
            """annoyingly, F filters only work on updates, not update_or_create, so need 
            do things like to increment units_total with a 2nd database hit
            """
            AccountStockData.objects.filter(id=record.id).update(
                units_total=F('units_total') + int(instance.units_to_transfer),
                xferred_units=F('xferred_units') + (int(instance.units_to_transfer)),
                running_total_xfer_value=F('running_total_xfer_value')
                + Decimal(int(instance.units_to_transfer) * instance.unit_price).quantize(sterling, ROUND_HALF_UP),
                all_time_total_xfer_value=F('all_time_total_xfer_value')
                + Decimal(int(instance.units_to_transfer) * instance.unit_price).quantize(sterling, ROUND_HALF_UP)
            )
    except Exception as e:
        logger.error(f'Error in saving to the account stock database: {e}')
        raise


@receiver(pre_save)
def clean_on_update(sender, instance=None, created=False, **kwargs):
    """
    if updating, run clean (not called by default if save() method invoked directly,
    such as when updating.
    Note: full_clean runs validation on model fields AND then also calls custom
    validations defined in clean(). To ONLY run custom validations, use
    instance.clean() instead on instance.full_clean().
    """
    instance.clean()


class StockData(models.Model):
    record_created = models.DateTimeField(auto_now_add=True)
    record_updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        'auth.User', related_name='stock_data', on_delete=models.SET_NULL, null=True)
    sku = models.CharField(max_length=100, blank=False, null=False, unique=True,
                           validators=[custom_validators.validate_alphanumplus])
    desc = models.CharField(max_length=100, blank=True, null=False,
                            validators=[custom_validators.validate_alphanumplus])
    units_total = models.PositiveIntegerField(blank=False, null=False, default=0)
    unit_price = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=9, default=0.00)

    STAFF_ALLOWED_TO_UPDATE = ['units_to_transfer']  # fields that store_managers are allowed to update

    class Meta:
        ordering = ('id',)
        indexes = [
            models.Index(fields=['desc']),
            models.Index(fields=['sku'])
        ]

    def __str__(self):
        return self.desc

    def clean(self):
        logger.info('Running clean on model')
        """
        clean method
        """
        """ Validate stock does not go negative """
        if self.units_total < 0:
            raise serializers.ValidationError(
                f'Your request is to transfer {-int(self.units_total)} too many of {self.desc}, '
                f'as that would exceed the number we currently have in the warehouse. Sorry!'
            )

        """ Call clean """
        super(StockData, self).clean()

    def save(self, *args, **kwargs):
        """
        Any custom methods, filters etc to run before saving ...
        """
        # nothing custom to do here, move along ...
        super(StockData, self).save(*args, **kwargs)


"""
Dispatch email on save (note: commented out now, as this moved to views.perform_update()
"""
# @receiver(post_save, sender=StockData)
# def email(sender, instance, **kwargs):
#     if hasattr(instance, 'update'):  # only send email if an update (not following new model creation)
#         SendEmail().compose(instance=instance, notification_type=SendEmail.EmailType.STOCK_TRANSFER)
