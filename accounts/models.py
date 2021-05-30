__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

from django.db import models
from rest_framework import serializers
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . import custom_validators
import logging
from django.db.models import F
from decimal import Decimal, ROUND_HALF_UP

# Get an instance of a logger
logger = logging.getLogger('django')


@receiver(pre_save)
def clean_on_update(sender, instance=None, created=False, **kwargs):
    logger.info('Running clean on update ...')
    instance.clean()


class AccountStockData(models.Model):
    record_created = models.DateTimeField(auto_now_add=True)
    record_updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        'auth.User', related_name='account_stock_data', on_delete=models.SET_NULL, null=True)
    sku = models.CharField(max_length=100, blank=False, null=False, unique=False,
                           validators=[custom_validators.validate_alphanumplus])
    desc = models.CharField(max_length=100, blank=True, null=False,
                            validators=[custom_validators.validate_alphanumplus])
    units_total = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    xferred_units = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    sold_units = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    shrinkage = models.PositiveIntegerField(blank=False, null=False, default=0)
    xfer_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    selling_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    opening_stock = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    running_total_xfer_value = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    running_total_sold_value = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    running_total_shrinkage_value = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    all_time_total_xfer_value = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)

    # fields that store_managers are allowed to update
    STAFF_ALLOWED_TO_UPDATE = ['units_total',
                               'selling_price', 'sold_units', 'shrinkage']

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


class AccountData(models.Model):
    record_created = models.DateTimeField(auto_now_add=True)
    record_updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        'auth.User', related_name='account_meta_data', on_delete=models.SET_NULL, null=True)
    all_time_total_xfer_value = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)

    class Meta:
        ordering = ('owner',)
        indexes = [
            models.Index(fields=['owner', 'all_time_total_xfer_value'])
        ]

    def __str__(self):
        return self.owner.username

    def clean(self):
        logger.info('Running clean on model')
        """
        clean method
        """
        """ Call clean """
        super(AccountData, self).clean()

    def save(self, *args, **kwargs):
        """
        Any custom methods, filters etc to run before saving ...
        """
        # nothing custom to do here, move along ...
        logger.info('Saving to model...')
        super(AccountData, self).save(*args, **kwargs)


class AccountStockTake(models.Model):
    record_created = models.DateTimeField(auto_now_add=True)
    record_updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        'auth.User', related_name='account_stock_take', on_delete=models.SET_NULL, null=True)
    grand_held_opening_stock = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    grand_held_closing_stock = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    grand_units_transferred_since_st = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    grand_units_recorded_sold_since_st = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    grand_units_recorded_shrunk_since_st = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    grand_units_unrecorded_hist_diff_since_st = models.IntegerField(
        blank=False, null=False, default=0)
    grand_total_value_recorded_sold_since_st = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    grand_total_value_recorded_shrunk_since_st = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    grand_total_value_unrecorded_current_xfer_price_since_st = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    grand_total_value_unrecorded_current_retail_price_since_st = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    grand_total_xferred_value_since_last_stock_take = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    grand_held_stock_value_at_current_xfer_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    grand_held_stock_value_at_present_retail_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    grand_all_time_total_at_actual_xfer_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)

    class Meta:
        ordering = ('owner',)
        indexes = [
            models.Index(fields=['owner'])
        ]

    def __str__(self):
        return self.record_created.strftime('%c')

    def clean(self):
        logger.info('Running clean on model')
        """
        clean method
        """
        """ Call clean """
        super(AccountStockTake, self).clean()

    def save(self, *args, **kwargs):
        """
        Any custom methods, filters etc to run before saving ...
        """
        # nothing custom to do here, move along ...
        logger.info('Saving to model...')
        super(AccountStockTake, self).save(*args, **kwargs)


class AccountStockTakeLines(models.Model):
    stock_take = models.ForeignKey('AccountStockTake', on_delete=models.CASCADE, related_name='stock_take',
                                   related_query_name='stock_take_lines')
    stock_line = models.CharField(max_length=100, blank=False, null=False, unique=False,
                                  validators=[custom_validators.validate_alphanumplus])
    stock_desc = models.CharField(max_length=100, blank=False, null=False, unique=False,
                                  validators=[custom_validators.validate_alphanumplus])
    xfer_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    retail_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    opening_stock = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    total_units = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    units_diff = models.IntegerField(blank=False, null=False, default=0)
    units_xferred = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    units_sold = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    units_shrunk = models.PositiveIntegerField(
        blank=False, null=False, default=0)
    unrecorded = models.IntegerField(blank=False, null=False, default=0)
    sold_value = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    shrinkage_value = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    xferred_value = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    unrecorded_xfer_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    unrecorded_retail_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    held_stock_current_xfer_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)
    held_stock_retail_price = models.DecimalField(
        blank=False, null=False, decimal_places=2, max_digits=50, default=0.00)

    class Meta:
        ordering = ('stock_take',)
        indexes = [
            models.Index(fields=['stock_line', 'stock_desc'])
        ]

    def __str__(self):
        return self.stock_line

    def clean(self):
        logger.info('Running clean on model')
        """
        clean method
        """
        """ Call clean """
        super(AccountStockTakeLines, self).clean()

    def save(self, *args, **kwargs):
        """
        Any custom methods, filters etc to run before saving ...
        """
        # nothing custom to do here, move along ...
        logger.info('Saving to model...')
        super(AccountStockTakeLines, self).save(*args, **kwargs)
