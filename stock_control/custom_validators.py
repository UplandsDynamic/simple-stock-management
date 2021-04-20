__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_alphanumplus(value):
    if not re.match('^[A-Za-z0-9_.\- ]*$', value):
        raise ValidationError(
            _(f'{value} contains invalid characters!')
        )


def validate_search(value):
    if not re.match('^[A-Za-z0-9_.\- ]*$', value):
        raise ValidationError(
            _(f'{value} contains invalid characters!')
        )
    return value


def validate_unit_price(value):
    # note: not currently required as using DecimalField rather than FloatField
    if not re.match('^[\d]*[\.]?[\d]{2}$', str(value)):
        raise ValidationError(
            _(f'{value} is not a valid price!')
        )


def validate_passwords_different(value):
    if isinstance(value, list) and len(value) == 2 and value[0]:
        if value[0] == value[1]:
            raise ValidationError(
                _(f'Old and new passwords are identical!')
            )
    else:
        raise ValidationError(
            _(f'Credentials were not supplied for validation.')
        )
    return value


def validate_password_correct(user, value):
    if not user.check_password(value):
        raise ValidationError(
            _(f'Your old credentials were incorrect. Please try again.')
        )


class RequestQueryValidator:
    page = 'validation of page limit param'
    results = 'validation of results limit param'
    order_by = 'validation of order_by param'
    valid_order_by_values = ['id', 'sku', 'desc', 'units_total', 'unit_price', 'record_updated',
                             '-id', '-sku', '-desc', '-units_total', '-unit_price', '-record_updated']

    @staticmethod
    def validate(query_type, value):
        if query_type == RequestQueryValidator.page:
            # return value if a valid integer, else 1 as default
            try:
                return int(value)
            except ValueError as v:
                return 1
        elif query_type == RequestQueryValidator.results:
            # return value if a valid integer, else 5 as default
            try:
                return int(value)
            except ValueError as v:
                return 5
        elif query_type == RequestQueryValidator.order_by:
            """
            Return value if valid order_by query, else 'id' as default
            To keep it simple, request query strings are same as model fieldnames
            so no need to substitute query for fieldname before running order_by on the queryset.
            """
            return value if value in RequestQueryValidator.valid_order_by_values else 'id'
