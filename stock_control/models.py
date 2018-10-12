from django.db import models
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . import custom_validators
from .email import SendEmail
import logging

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


@receiver(pre_save)
def clean_on_update(sender, instance=None, created=False, **kwargs):
    """
    if updating, run clean (not called by default if save() method invoked directly,
    such as when updating.
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

    STAFF_ALLOWED_TO_UPDATE = ['units_total']

    class Meta:
        ordering = ('id',)
        indexes = [
            models.Index(fields=['desc']),
            models.Index(fields=['sku'])
        ]

    def __str__(self):
        return self.desc

    def clean(self):
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


@receiver(post_save, sender=StockData)
def email(sender, instance, **kwargs):
    if hasattr(instance, 'update'):  # only send email if an update (not following new model creation)
        SendEmail().compose(instance=instance, notification_type=SendEmail.EmailType.STOCK_TRANSFER)
