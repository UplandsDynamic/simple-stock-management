from django.db import models
from rest_framework import serializers
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . import custom_validators
import logging

# Get an instance of a logger
logger = logging.getLogger('django')

class AccountStockData(models.Model):
    record_created = models.DateTimeField(auto_now_add=True)
    record_updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        'auth.User', related_name='account_stock_data', on_delete=models.SET_NULL, null=True)
    sku = models.CharField(max_length=100, blank=False, null=False, unique=False,
                           validators=[custom_validators.validate_alphanumplus])
    desc = models.CharField(max_length=100, blank=True, null=False,
                            validators=[custom_validators.validate_alphanumplus])
    units_total = models.PositiveIntegerField(blank=False, null=False, default=0)
    xfer_price = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=9, default=0.00)
    selling_price = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=9, default=0.00)
    opening_stock = models.PositiveIntegerField(blank=False, null=False, default=0)
    closing_stock = models.PositiveIntegerField(blank=False, null=False, default=0)
    running_total_xfer_value = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=9, default=0.00)
    running_total_selling_value = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=9, default=0.00)

    STAFF_ALLOWED_TO_UPDATE = ['units_total', 'selling_price']  # fields that store_managers are allowed to update

    class Meta:
        # unique_together makes combo of price & sku a unique entry. Allows for multi xfers of unique lines @ different prices
        unique_together = ('sku', 'owner')
        ordering = ('id',)
        indexes = [
            models.Index(fields=['owner', 'desc', 'sku'])
        ]

    def __str__(self):
        return self.owner.username

    def clean(self):
        logger.info('Running clean on model')
        """
        clean method
        """
        """ Validate stock does not go negative """
        # if self.units_total < 0:
        #     raise serializers.ValidationError(
        #         f'Your request is to transfer {-int(self.units_total)} too many of {self.desc}, '
        #         f'as that would exceed the number we currently have in the warehouse. Sorry!'
        #     )

        """ Call clean """
        super(AccountStockData, self).clean()

    def save(self, *args, **kwargs):
        """
        Any custom methods, filters etc to run before saving ...
        """
        # nothing custom to do here, move along ...
        super(AccountStockData, self).save(*args, **kwargs)
