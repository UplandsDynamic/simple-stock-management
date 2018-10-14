import copy
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse
from rest_framework.utils import json
from .models import StockData
from django.contrib.auth.models import User, Group
from .custom_validators import RequestQueryValidator
from .email import SendEmail
from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from contextlib import contextmanager
from datetime import datetime
from django.conf import settings
from .views import PasswordUpdateViewSet, StockDataViewSet
from .serializers import ChangePasswordSerializer, StockDataSerializer
from rest_framework.test import APIClient, APITransactionTestCase, RequestsClient, APIRequestFactory, \
    force_authenticate, APITestCase
from rest_framework.authtoken.models import Token


@contextmanager
def as_admin(class_reference=None, user=None, group=None):
    """
    class_reference: 'self' of calling class method.
    create context manager to set/unset user as an administrator, using context manager ('with' statement).
    For example, see this psuedo code:
        with as_admin(self):
            if self.user.groups.filter(name='administrators').exists():
                print('This should be rendered, as user has been added to the administrator group!')
            else:
                print('This text should not be rendered ...')
        if self.user.groups.filter(name='administrators').exists():
            print('This text should not be rendered ...')
        else:
            print('This should be rendered, as user has been removed to the administrator group!')
    """
    if class_reference:
        class_reference.group.user_set.add(class_reference.class_instance.user)
        yield
        class_reference.group.user_set.remove(class_reference.class_instance.user)
    elif user and group:
        group.user_set.add(user)
        yield
        group.user_set.remove(user)


@contextmanager
def as_staff(user=None):
    """
    context manager to set user as staff
    """
    if user:
        user.is_staff = True
        user.save()
        yield
        user.is_staff = False
        user.save()


"""
tests for models.py
"""


class StockDataTestCase(TestCase):
    """
    test StockData model
    """

    stockLine_1 = user_1 = None

    def setUp(self):
        self.user_1 = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPassword1')
        self.stockLine_1 = StockData.objects.create(
            owner=User.objects.get(username='tester'),
            sku='001-001',
            desc='Test description',
            units_total=11,
            unit_price=11.23
        )

    def test_starting_conditions(self):
        self.assertIsInstance(self.stockLine_1, StockData)

    def test_clean(self):
        """
        test method that prevents stock units from going negative
        """
        self.stockLine_1.units_total = -1
        self.assertRaises(serializers.ValidationError, self.stockLine_1.clean)

    def test___str__(self):
        """
        test method that returns the model doc string
        """
        self.assertEqual(self.stockLine_1.desc, self.stockLine_1.__str__())

    """
    tests for custom_validators.py
    """


class RequestQueryValidatorTestCase(TestCase):
    """
    test RequestQueryValidator class
    """

    def setUp(self):
        self.query_type = [RequestQueryValidator.order_by, RequestQueryValidator.page, RequestQueryValidator.results]
        self.order_by_args = ['id', 'sku', 'desc', 'units_total', 'unit_price', 'record_updated',
                              '-id', '-sku', '-desc', '-units_total', '-unit_price', '-record_updated', 'NOT_VALID']
        self.order_by_arg_default = 'id'
        self.page_args = [27, 'NOT_VALID']
        self.page_arg_default = 1
        self.results_args = [11, 'NOT_VALID']
        self.results_arg_default = 5

    def test_validate(self):
        for query in self.query_type:
            if query == RequestQueryValidator.order_by:
                for order_by in self.order_by_args:
                    self.assertIn(RequestQueryValidator.validate(
                        RequestQueryValidator.order_by, order_by), [order_by, self.order_by_arg_default])
            if query == RequestQueryValidator.page:
                for page in self.page_args:
                    self.assertIn(RequestQueryValidator.validate(
                        RequestQueryValidator.page, page), [page, self.page_arg_default])
            if query == RequestQueryValidator.results:
                for result in self.results_args:
                    self.assertIn(RequestQueryValidator.validate(
                        RequestQueryValidator.results, result), [result, self.results_arg_default])

    """
    tests for serializers.py
    """


class ChangePasswordSerializerTestCase(TestCase):
    """
    test ChangePasswordSerializer class
    """

    def setUp(self):
        self.class_instance = ChangePasswordSerializer()  # create instance of class to test
        self.user_instance = User.objects.create_user('dan', 'dan@aninstanceofme.com', 'myPassword1')
        self.invalid_password = '123'
        self.validated_data = {'old_password': 'myPassword1', 'new_password': 'myNewPassword'}
        self.invalid_validated_data = {'old_password': 'myPassword1', 'new_password': 'myPassword1'}

    def test_validate_old_password(self):
        self.assertRaises(ValidationError, self.class_instance.validate_old_password, self.invalid_password)
        self.assertIs(self.class_instance.validate_old_password(self.validated_data['old_password']),
                      self.validated_data['old_password'])

    def test_validate_new_password(self):
        self.assertRaises(ValidationError, self.class_instance.validate_new_password, self.invalid_password)
        self.assertIs(self.class_instance.validate_new_password(self.validated_data['new_password']),
                      self.validated_data['new_password'])

    def test_update(self):
        # check fails if passwords are the same
        self.assertRaises(serializers.ValidationError, self.class_instance.update, self.user_instance,
                          self.invalid_validated_data)
        # check returns user instance with the new password set
        self.assertTrue(self.class_instance.update(self.user_instance, self.validated_data).check_password(
            self.validated_data['new_password']))


class StockDataSerializerTestCase(TransactionTestCase):
    """
    test StockDataSerializer class. Extends TransactionTestCase (rather than TestCase)
    for database transaction checking against things like Unique constraints. Using
    TestCase would break the test, as it would fail prematurely and throw an error due to all assertions being
    wrapped in one single transaction if using TestCase.
    """

    user = group = stockObject = None
    dummy_orig_stock_creation = {'sku': '001-001', 'desc': 'test description',
                                 'units_total': 100, 'unit_price': 17.27}
    dummy_new_stock_creation = {'sku': '001-002', 'desc': 'test new description',
                                'units_total': 111, 'unit_price': 127.26}

    def setUp(self):
        self.class_instance = StockDataSerializer(
            data=self.dummy_new_stock_creation)  # create instance of class to test
        self.class_instance.is_valid(raise_exception=True)  # run test data through validation
        self.group = Group.objects.create(name='administrators')  # create 'administrators' group
        self.class_instance.user = User.objects.create_user('dan', 'dan@aninstanceofme.com', 'myPassword1')  # set user
        self.stockObject = StockData.objects.create(**self.dummy_orig_stock_creation)  # create dummy stock object

    def set_stock_object(self):
        """
        set/reset stock obj to original values
        """
        StockData.objects.update_or_create({'id': self.stockObject.id, 'sku': '001-001', 'desc': 'test description',
                                            'units_total': 100, 'unit_price': 17.27})

    def test_administrators_check(self):
        """
        test function that determines whether user is an administrator
        """
        with as_admin(self):  # check true if user in administrators
            self.assertTrue(self.class_instance.administrators_check(None))
        self.assertFalse(self.class_instance.administrators_check(None))  # false if user not in administrators

    def test_create_request_time(self):
        """
        test function that creates a datetime object to return as the time of request
        """
        self.assertIsInstance(self.class_instance.create_request_time(None), datetime)

    def test_create(self):
        """
        test new object is created
        """
        # test non-admin user
        self.assertRaises(serializers.ValidationError, self.class_instance.create, self.dummy_new_stock_creation)
        with as_admin(self):  # test admin user
            # duplicate SKU must fail
            self.assertRaises(serializers.ValidationError, self.class_instance.create, self.dummy_orig_stock_creation)
            # updating by admin must succeed
            created = self.class_instance.create(self.dummy_new_stock_creation)
            self.assertIsInstance(StockData.objects.get(sku=created['sku']), StockData)

    def test_update(self):
        """
        test update of object for non-admin user
        """
        # update of description, SKU, and price must fail for non-admin user
        pre_update_stock_object = copy.deepcopy(self.stockObject)  # create separate copy of obj to compare against
        updated = self.class_instance.update(self.stockObject, {'sku': '001-002', 'desc': 'new description',
                                                                'units_total': 23, 'unit_price': 253.23})
        self.assertEqual(updated.desc, pre_update_stock_object.desc)  # desc should be the same, no change
        self.assertEqual(updated.sku, pre_update_stock_object.sku)  # sku should be the same, no change
        self.assertEqual(updated.unit_price, pre_update_stock_object.unit_price)  # unit_price should be the same
        # reducing stock unit level below 0 must fail
        self.assertRaises(serializers.ValidationError, self.class_instance.update, self.stockObject,
                          {'units_total': -150})
        # increase of stock units for non-admin user must fail
        self.assertRaises(serializers.ValidationError, self.class_instance.update, self.stockObject,
                          {'units_total': 25})
        # decreasing stock if level stays 0 or above must succeed
        units_before_update = self.stockObject.units_total
        updated = self.class_instance.update(self.stockObject, {'units_total': 10})
        self.assertNotEqual(updated.units_total, units_before_update)
        """
        test update of object for admin user
        """
        # update of description, SKU, and price must pass for admin user
        with as_admin(self):
            self.set_stock_object()  # reset stockObject to original values
            pre_update_stock_object = copy.deepcopy(self.stockObject)  # create separate copy of obj to compare against
            updated = self.class_instance.update(self.stockObject, {'sku': '001-002', 'desc': 'new description',
                                                                    'units_total': 200, 'unit_price': 253.23})
            self.assertNotEqual(updated.desc, pre_update_stock_object.desc)  # desc should change
            self.assertNotEqual(updated.sku, pre_update_stock_object.sku)  # sku should change
            self.assertNotEqual(updated.unit_price, pre_update_stock_object.unit_price)  # unit_price should change
            self.assertNotEqual(updated.units_total, pre_update_stock_object.units_total)  # units_total should increase
            # changing SKU to value that already exists must be ignored
            sku_before_update = updated.sku
            updated = self.class_instance.update(self.stockObject, {'sku': '001-002', 'desc': 'new description',
                                                                    'units_total': 210, 'unit_price': 253.23})
            self.assertEqual(sku_before_update, updated.sku)  # must remain equal
            # reducing stock unit level below 0 must fail
            self.assertRaises(serializers.ValidationError, self.class_instance.update, self.stockObject,
                              {'units_total': -150})
            # decreasing stock if level stays 0 or above must succeed
            units_before_update = self.stockObject.units_total
            updated = self.class_instance.update(self.stockObject, {'units_total': 10})
            self.assertNotEqual(updated.units_total, units_before_update)


"""
tests for email.py
"""


class SendEmailTestCase(TestCase):
    """
    test SendEmail class
    """

    def setUp(self):
        self.class_instance = SendEmail()
        self.body_plaintext = 'This is a test!'
        self.body_html = '<h1>This is a test!</h1>'
        self.subject = 'Test email'
        self.email_to = [settings.DEFAULT_FROM_EMAIL]
        self.email_from = settings.DEFAULT_FROM_EMAIL
        self.notification_type = self.class_instance.EmailType.STOCK_TRANSFER
        self.group = Group.objects.create(name='administrators')  # create 'administrators' group
        self.class_instance.user = User.objects.create_user('warehouse admin', settings.DEFAULT_FROM_EMAIL, 'myPwd8*e')
        self.class_instance.user2 = User.objects.create_user('shop manager', 's.m.test@aninstance.com', 'eekeJ839)lx*')
        self.stock_data = StockData.objects.create(
            owner=User.objects.get(username='warehouse admin'),
            sku='001-001',
            desc='Test description',
            units_total=11,
            unit_price=11.23
        )
        self.stock_data.user = self.class_instance.user2
        self.stock_data.transferred = 77

    def test_send(self):
        # test False (no email sent) if body, email_to or email_from are absent
        test_params = {'email_to': self.email_to, 'email_from': self.email_from, 'body_plaintext': self.body_plaintext,
                       'body_html': self.body_html, 'subject': self.subject}
        for k, v in test_params.items():
            self.assertFalse(self.class_instance.send(f'{k}={v}'))
        # test True (email sent) if params are present
        settings.STOCK_MANAGEMENT_OPTIONS['email']['notifications_on'] = True
        self.assertTrue(self.class_instance.send(**test_params))
        # test False if invalid email
        test_params['email_to'] = 'blah'
        self.assertFalse(self.class_instance.send(**test_params))
        # test false if params are in incorrect type
        test_params_corrupt = {'email_to': 77, 'email_from': 77, 'body_plaintext': 77, 'body_html': 77, 'subject': 77}
        self.assertFalse(self.class_instance.send(**test_params_corrupt))

    def test_compose(self):
        # test False if no stock instance or notification type
        self.assertFalse(self.class_instance.compose())
        with as_admin(self):
            # test True to confirm sending
            self.assertTrue(self.class_instance.compose(instance=self.stock_data,
                                                        notification_type=self.notification_type))
            # test invalid email return False
            self.stock_data.user.email = 'blah'
            self.assertFalse(self.class_instance.compose(instance=self.stock_data,
                                                         notification_type=self.notification_type))
            # test Attribute error returns False
            self.stock_data.user.email = 'valid_test@anistance.com'
            self.stock_data.desc = 77
            self.assertFalse(self.class_instance.compose(instance=self.stock_data,
                                                         notification_type=self.notification_type))


"""
tests for views.py
"""


class PasswordUpdateViewSetTestCase(APITransactionTestCase):
    """
    tests password reset functionality
    """

    def setUp(self):
        self.group = Group.objects.create(name='administrators')  # create 'administrators' group
        self.user = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPwd8ntGr8', is_staff=True)
        self.token = Token.objects.get(user__username='tester')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_perform_update(self):
        # test password change for non-admin user
        response = self.client.patch(f'/api/v1/change-password/{self.user.username}/',
                                     json.dumps({"old_password": "myPwd8ntGr8", "new_password": "ser*kenem"}
                                                ), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test password change for admin user
        with as_admin(user=self.user, group=self.group):
            response = self.client.patch(f'/api/v1/change-password/{self.user.username}/',
                                         json.dumps({"old_password": "ser*kenem", "new_password": "myPwd8ntGr8"}
                                                    ), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class StockDataViewSetTestCase(APITestCase):
    """
    tests the views in StockDataViewSet
    """

    @staticmethod
    def create_stock(number, user):
        units = []
        for c, unit in enumerate(range(number)):
            units.append(StockData.objects.create(
                owner=User.objects.get(username=user),
                sku=f'001-0{c}',
                desc=f'Test description {c}',
                units_total=45 + c,
                unit_price=14.22 + c
            ))
        return units

    def setUp(self):
        # common to all tests
        self.group = Group.objects.create(name='administrators')  # create 'administrators' group

    # """
    # Note 1: Mapping for actions (used in as_view), are:
    # {
    # 'get': 'retrieve'  # to retrieve one object, as spec by pk passed in url param, e.g. /stock/1
    # 'get': 'list' # to list all objects, e.g. /stock/
    # 'put': 'update',
    # 'patch': 'partial_update',
    # 'delete': 'destroy'
    # }
    #
    # Note 2: Permissions testing doesn't work with APIRequestFactory (used below) - need to use APIClient for that.
    # But, APIClient doesn't work with DRF router URLs.
    # """
    #
    # def test_get_queryset_apirequestfactory(self):
    #     """
    #     APIRequestFactory: tests (tests view, but not necessarily permissions, middleware, routing, etc)
    #     """
    #     # setup
    #     user = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPwd8ntGr8', is_staff=True)
    #     factory = APIRequestFactory()
    #     request = factory.get('/api/v1/stock/', {}, format='json')
    #     force_authenticate(request, user=user, token=user.auth_token)
    #     stock = StockDataViewSetTestCase.create_stock(number=25, user=user)  # list of 25 stock objects
    #     # test get list
    #     view = StockDataViewSet.as_view({'get': 'list'})
    #     response = view(request)
    #     # test returns http status 200
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # test results list contains at least one result
    #     self.assertGreater(len(response.data['results']), 0)
    #     """
    #     APIRequestFactory: test query string
    #     """
    #     request = factory.get('/api/v1/stock/?desc=test', {}, format='json')
    #     force_authenticate(request, user=user, token=user.auth_token)
    #     view = StockDataViewSet.as_view({'get': 'list'})
    #     response = view(request)
    #     # test returns http status 200
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # test results list contains at least one result
    #     self.assertGreater(len(response.data['results']), 0)
    #     """
    #     APIRequestFactory: test retrieve a specific record
    #     """
    #     request = factory.get('/api/v1/stock/11/', {}, format='json')
    #     force_authenticate(request, user=user, token=user.auth_token)
    #     view = StockDataViewSet.as_view({'get': 'retrieve'})
    #     response = view(request, pk=stock[10].pk)
    #     # test returns http status 200
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_queryset(self):
        """
        APIClient: tests entire gambit, including routing, middleware & permissions).
        Run in preference to APIRequestFactory tests, as that only tests view alone.
        """
        # setup
        user = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPwd8ntGr8', is_staff=False)
        token = Token.objects.get(user__username='tester')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        stock = StockDataViewSetTestCase.create_stock(number=25, user=user)  # list of 25 stock objects
        # test returns 403 if user not staff
        response = client.get(f'/api/v1/stock/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # test returns 200 if user is staff
        with as_staff(user):
            response = client.get(f'/api/v1/stock/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreater(len(response.data['results']), 0)
        # test list
        response = client.get(f'/api/v1/stock/{stock[10].pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        with as_staff(user):
            response = client.get(f'/api/v1/stock/{stock[10].pk}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_perform_create(self):
        pass
