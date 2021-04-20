import copy
from django.test import TestCase, TransactionTestCase
from rest_framework.utils import json
from .models import StockData
from django.contrib.auth.models import User, Group
from .custom_validators import *
from email_service.email import SendEmail
from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from contextlib import contextmanager
from datetime import datetime
from django.conf import settings
from .serializers import ChangePasswordSerializer, StockDataSerializer
from rest_framework.test import APIClient, APITransactionTestCase, APIRequestFactory, APITestCase
from rest_framework.authtoken.models import Token


@contextmanager
def as_admin(user=None, group=None):
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
    if user and group:
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

    def test_validate_alphanumplus(self):
        self.assertEqual(validate_alphanumplus(value='This is a test'), None)
        self.assertRaises(ValidationError, validate_alphanumplus, 'This is a test!!!')

    def test_validate_search(self):
        self.assertEqual(validate_search(value='This is a test'), 'This is a test')
        self.assertRaises(ValidationError, validate_search, 'This is a test!!!')

    def test_validate_unit_price(self):
        self.assertEqual(validate_unit_price('10.23'), None)
        self.assertEqual(validate_unit_price('10523.23'), None)
        self.assertEqual(validate_unit_price('10523'), None)
        self.assertRaises(ValidationError, validate_unit_price, '12.362')
        self.assertRaises(ValidationError, validate_unit_price, 'test')

    def test_validate_passwords_different(self):
        self.assertEqual(validate_passwords_different(value=['mYpa$sW0rD', 'mYpa$sW0rD2']),
                         ['mYpa$sW0rD', 'mYpa$sW0rD2']),
        self.assertRaises(ValidationError, validate_passwords_different, ['mYpa$sW0rD', 'mYpa$sW0rD'])
        self.assertRaises(ValidationError, validate_passwords_different, ['', 'mYpa$sW0rD'])
        self.assertRaises(ValidationError, validate_passwords_different, ['mYpa$sW0rD'])

    def test_validate_password_correct(self):
        user = User.objects.create_user('dan', 'test@uplandsdynamic.com', 'myPassword1')
        self.assertEqual(validate_password_correct(user=user, value='myPassword1'), None)
        self.assertRaises(ValidationError, validate_password_correct, user=user, value='InC0rREctPWd!')

    """
    tests for serializers.py
    """


class ChangePasswordSerializerTestCase(TestCase):
    """
    test ChangePasswordSerializer class
    """

    def setUp(self):
        self.class_instance = ChangePasswordSerializer()  # create instance of class to test
        self.user_instance = User.objects.create_user('dan', 'test@uplandsdynamic.com', 'myPassword1')
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
        # check returns user instance with the password element defined as 'CHANGED'
        self.assertEqual(self.class_instance.update(self.user_instance, self.validated_data).password, 'CHANGED')


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
                                'units_total': 100, 'unit_price': 127.26}

    def setUp(self):
        self.group = Group.objects.create(name='administrators')  # create 'administrators' group
        self.user = User.objects.create_user('dan', 'test@uplandsdynamic.com', 'myPassword1')  # set user

    def test_administrators_check(self):
        """
        test function that determines whether user is an administrator
        """
        request = APIRequestFactory().get('/api/v2/stock/')
        request.user = self.user
        serializer = StockDataSerializer(context={'request': request})
        with as_admin(user=self.user, group=self.group):  # check true if user in administrators
            self.assertTrue(serializer.administrators_check(None))
        self.assertFalse(serializer.administrators_check(None))  # false if user not in administrators

    def test_create_request_time(self):
        """
        test function that creates a datetime object to return as the time of request
        """
        request = APIRequestFactory().get('/api/v2/stock/')
        request.user = self.user
        serializer = StockDataSerializer(context={'request': request})
        self.assertIsInstance(serializer.create_request_time(None), datetime)

    def test_create(self):
        """
        test new object is created
        """
        stock_object = StockData.objects.create(**self.dummy_orig_stock_creation)  # create dummy stock object
        request = APIRequestFactory().get('/api/v2/stock/')
        request.user = self.user
        serializer = StockDataSerializer(context={'request': request}, data=stock_object)
        serializer.is_valid()
        # test non-admin user
        self.assertRaises(serializers.ValidationError, serializer.create, serializer.validated_data)
        with as_admin(user=self.user, group=self.group):  # test admin user
            # creation with admin must succeed
            self.assertEqual(serializer.create(serializer.validated_data), serializer.validated_data)
            # duplicate SKU must fail
            self.assertRaises(serializers.ValidationError, serializer.create, serializer.validated_data)

    def test_update(self):
        """
        test update of object for non-admin user
        """
        stock_object = StockData.objects.create(**self.dummy_orig_stock_creation)  # create dummy stock object
        request = APIRequestFactory().patch('/api/v2/stock/1/')
        request.user = self.user
        serializer = StockDataSerializer(context={'request': request}, data=stock_object)
        serializer.is_valid()
        """update of description, SKU, and price must fail for non-admin user"""
        # 1) if validation set to fail (comment out option 1 or 2)
        self.assertFalse(serializer.is_valid())
        # 2) Or, if validation set to pass, but just not update the illegal fields
        # updated = serializer.update(instance=stock_object, validated_data=self.dummy_new_stock_creation)
        # self.assertEqual(updated.desc, stock_object.desc)  # desc should be the same, no change
        # self.assertEqual(updated.sku, stock_object.sku)  # sku should be the same, no change
        # self.assertEqual(updated.unit_price, stock_object.unit_price)  # unit_price should be the same
        # reducing stock unit level below 0 must fail
        self.assertRaises(serializers.ValidationError, serializer.update, stock_object,
                          {'units_to_transfer': 150})
        # decreasing stock if level stays 0 or above must succeed
        units_before_update = stock_object.units_total
        # add requester as per view
        stock_object.requester = request.user
        # test update
        updated = serializer.update(instance=stock_object, validated_data={'units_to_transfer': 10})
        self.assertNotEqual(updated.units_total, units_before_update)
        """
        test update of object for admin user
        """
        # update of description, SKU, and price must pass for admin user
        with as_admin(user=self.user, group=self.group):
            pre_update_stock_object = copy.deepcopy(stock_object)
            updated = serializer.update(instance=stock_object,
                                        validated_data={'sku': '001-003', 'desc': 'new description',
                                                        'units_total': 200, 'unit_price': 253.23})
            self.assertNotEqual(updated.desc, pre_update_stock_object.desc)  # desc should change
            self.assertNotEqual(updated.sku, pre_update_stock_object.sku)  # sku should change
            self.assertNotEqual(updated.unit_price, pre_update_stock_object.unit_price)  # unit_price should change
            self.assertNotEqual(updated.units_total, pre_update_stock_object.units_total)  # units_total should increase
            # changing SKU to value that already exists must be ignored
            updated = serializer.update(instance=stock_object,
                                        validated_data={'sku': '001-001', 'desc': 'new description',
                                                        'units_total': 210, 'unit_price': 253.23})
            self.assertEqual(pre_update_stock_object.sku, updated.sku)  # must remain equal
            # reducing stock unit level below 0 must fail
            self.assertRaises(serializers.ValidationError, serializer.update, stock_object,
                              {'units_total': -500})
            # decreasing stock if level stays 0 or above must succeed
            stock_object = pre_update_stock_object  # reset stock obj
            units_before_update = stock_object.units_total
            updated = serializer.update(instance=stock_object, validated_data={'units_to_transfer': 10})
            self.assertNotEqual(updated.units_total, units_before_update)


"""
tests for email.py
"""


class SendEmailTestCase(TestCase):
    """
    test SendEmail class
    """

    def setUp(self):
        self.body_plaintext = 'This is a test!'
        self.body_html = '<h1>This is a test!</h1>'
        self.subject = 'Test email'
        self.email_to = [settings.DEFAULT_FROM_EMAIL]
        self.email_from = settings.DEFAULT_FROM_EMAIL
        self.notification_type = SendEmail.EmailType.STOCK_TRANSFER
        self.group = Group.objects.create(name='administrators')  # create 'administrators' group
        self.user = User.objects.create_user('warehouse admin', settings.DEFAULT_FROM_EMAIL, 'myPwd8*e')
        self.user2 = User.objects.create_user('shop manager', 's.m.test@uplandsdynamic.com', 'eekeJ839)lx*')
        self.stock_data = StockData.objects.create(
            owner=User.objects.get(username='warehouse admin'),
            sku='001-001',
            desc='Test description',
            units_total=11,
            unit_price=11.23
        )
        self.mock_serialized_model_instance = {"success": True, "error": None, "user_is_admin": False,
                                               "data": {"id": 1, "record_created": datetime.utcnow(),
                                                        "record_updated": datetime.utcnow(),
                                                        "sku": "NCC-1701-E", "desc": "USS Enterprise",
                                                        "units_total": 543, "unit_price": 23.9, "units_to_transfer": 1}}
        self.stock_data.user = self.user2
        self.stock_data.units_to_transfer = 77
        self.send_email = SendEmail()

    def test_send(self):
        # test False (no email sent) if body, email_to or email_from are absent
        test_params = {'email_to': self.email_to, 'email_from': self.email_from, 'body_plaintext': self.body_plaintext,
                       'body_html': self.body_html, 'subject': self.subject}
        for k, v in test_params.items():
            self.assertFalse(self.send_email.send(f'{k}={v}'))
        # test True (email sent) if params are present
        settings.STOCK_MANAGEMENT_OPTIONS['email']['notifications_on'] = True
        self.assertTrue(self.send_email.send(**test_params))
        # test False if invalid email
        test_params['email_to'] = 'blah'
        self.assertFalse(self.send_email.send(**test_params))
        # test false if params are in incorrect type
        test_params_corrupt = {'email_to': 77, 'email_from': 77, 'body_plaintext': 77, 'body_html': 77, 'subject': 77}
        self.assertFalse(self.send_email.send(**test_params_corrupt))

    def test_compose(self):
        # test False if no stock instance or notification type
        self.assertFalse(self.send_email.compose())
        with as_admin(user=self.user, group=self.group):
            # test True to confirm sending
            self.assertTrue(self.send_email.compose(records=[self.mock_serialized_model_instance],
                                                    user=self.user,
                                                    notification_type=self.notification_type))
            # test invalid email return False
            self.user.email= 'blah'
            self.assertFalse(self.send_email.compose(records=[self.mock_serialized_model_instance],
                                                     user=self.user,
                                                     notification_type=self.notification_type))
            # test Attribute error returns False
            self.stock_data.user.email = 'valid_test@anistance.com'
            self.stock_data.desc = 77
            self.assertFalse(self.send_email.compose(records=[self.mock_serialized_model_instance],
                                                     user=self.user,
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
        response = self.client.patch(f'/api/v2/change-password/{self.user.username}/',
                                     json.dumps({"old_password": "myPwd8ntGr8", "new_password": "ser*kenem"}
                                                ), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test password change for admin user
        with as_admin(user=self.user, group=self.group):
            response = self.client.patch(f'/api/v2/change-password/{self.user.username}/',
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
        pass

    # """
    # Note 1: Mapping for actions (used in as_view), are:
    # {
    # 'get': 'retrieve'  # to retrieve one object, as spec by pk passed in url param, e.g. /stock/1
    # 'get': 'list' # to list all objects, e.g. /stock/
    # 'post': 'create'
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
    #     request = factory.get('/api/v2/stock/', {}, format='json')
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
    #     request = factory.get('/api/v2/stock/?desc=test', {}, format='json')
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
    #     request = factory.get('/api/v2/stock/11/', {}, format='json')
    #     force_authenticate(request, user=user, token=user.auth_token)
    #     view = StockDataViewSet.as_view({'get': 'retrieve'})
    #     response = view(request, pk=stock[10].pk)
    #     # test returns http status 200
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_queryset(self):
        """
        APIClient: tests entire gambit, including routing, middleware & permissions).
        Run in preference to APIRequestFactory tests, as that only tests view alone.

        Test GET stock items
        """
        # setup
        user = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPwd8ntGr8', is_staff=False)
        token = Token.objects.get(user__username='tester')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        stock = StockDataViewSetTestCase.create_stock(number=25, user=user)  # list of 25 stock objects
        """
        if not staff
        """
        # test returns 403
        response = client.get(f'/api/v2/stock/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # test returns requested specific record
        response = client.get(f'/api/v2/stock/{stock[10].pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # test returns records in response to query on desc
        response = client.get(f'/api/v2/stock/?desc=tes')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = client.get(f'/api/v2/stock/?desc=tes_i_do_not_exist')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        """
        if staff
        """
        with as_staff(user):
            # test returns records
            response = client.get(f'/api/v2/stock/', format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreater(len(response.data['results']), 0)
            # test returns requested specific record
            response = client.get(f'/api/v2/stock/{stock[10].pk}/', format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['id'], stock[10].id)
            # test returns records in response to query on desc
            response = client.get(f'/api/v2/stock/?desc=Test%20description%2011', format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('Test description 11', response.data['results'][0]['desc'])
            # test returns empty results if invalid characters
            response = client.get(f'/api/v2/stock/?desc=Test%20description%20*(', format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 0)
            # test returns empty if query does not exist
            response = client.get(f'/api/v2/stock/?desc=Test%20description%2011_i_do_not_exist', format='json')
            self.assertEqual(response.data['count'], 0)
            # test order by id
            response = client.get(f'/api/v2/stock/?order_by=id', format='json')
            self.assertGreater(response.json()['results'][1]['id'], response.data['results'][0]['id'])
            # test order by SKU
            response = client.get(f'/api/v2/stock/?order_by=sku', format='json')
            sku_list = [r['sku'] for r in response.data['results']]
            self.assertEqual(sku_list, sorted(sku_list))
            # test order by desc
            desc_list = [r['desc'] for r in response.data['results']]
            self.assertEqual(desc_list, sorted(desc_list))
            # test order by units_total
            units_total_list = [r['units_total'] for r in response.data['results']]
            self.assertEqual(units_total_list, sorted(units_total_list))
            # test order by unit_price
            unit_price_list = [r['unit_price'] for r in response.data['results']]
            self.assertEqual(unit_price_list, sorted(unit_price_list))
            # test order by record_updated
            updated_list = [r['record_updated'] for r in response.data['results']]
            self.assertEqual(updated_list, sorted(updated_list))
            # test order by id negative
            response = client.get(f'/api/v2/stock/?order_by=-id', format='json')
            self.assertLess(response.data['results'][1]['id'], response.json()['results'][0]['id'])
            # test limit
            response = client.get(f'/api/v2/stock/?limit=5', format='json')
            self.assertEqual(len(response.data['results']), 5)
            # test offset
            response = client.get(f'/api/v2/stock/?limit=5&offset=1', format='json')
            self.assertEqual(response.data['results'][4]['id'], 6)

    def test_perform_create(self):
        """
        Test POST new stock item
        """
        # setup
        user = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPwd8ntGr8', is_staff=False)
        group = Group.objects.create(name='administrators')  # create 'administrators' group
        token = Token.objects.get(user__username='tester')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        # test returns 403 if user not staff
        response = client.post(f'/api/v2/stock/', {"units_total": "1", "unit_price": "5.36", "desc": "tester",
                                                   "sku": "008-952"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # test returns 400 if staff but not admin
        with as_staff(user):
            response = client.post(f'/api/v2/stock/', {
                "units_total": "1", "unit_price": "5.36", "desc": "tester",
                "sku": "008-952"}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # test returns 200 if staff and admin
        with as_staff(user):
            with as_admin(user=user, group=group):
                response = client.post(f'/api/v2/stock/', {"units_total": "1", "unit_price": "5.36", "desc": "tester",
                                                           "sku": "008-952"}, format='json')
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                # test response is correct
                self.assertEqual(response.data['units_total'], 1)
                self.assertEqual(response.data['sku'], '008-952')
                self.assertEqual(response.data['desc'], 'tester')
                self.assertEqual(response.data['unit_price'], '5.36')
                self.assertEqual(response.data['user_is_admin'], True)
                self.assertIsInstance(response.data['datetime_of_request'], datetime)

    def test_perform_update(self):
        # setup
        user = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPwd8ntGr8', is_staff=False)
        group = Group.objects.create(name='administrators')  # create 'administrators' group
        token = Token.objects.get(user__username='tester')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        stock = StockDataViewSetTestCase.create_stock(number=25, user=user)  # list of 25 stock objects
        # test returns 403 if user not staff
        response = client.patch(f'/api/v2/stock/{stock[0].pk}/', data={"units_total": 77}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        with as_staff(user):
            """test changing any other value than units_to_transfer fails if staff but not administrator
            and also that units_to_transfer is accepted"""
            orig_values = {"desc": stock[0].desc, "unit_price": stock[0].unit_price, "sku": stock[0].sku}
            new_values = {"desc": "A new description", "unit_price": "56.32", "sku": "896-528",
                          "units_to_transfer": "7"}
            for key, value in new_values.items():
                response = client.patch(f'/api/v2/stock/{stock[0].pk}/', data={key: value}, format='json')
                if key != 'units_to_transfer':
                    self.assertEqual(getattr(stock[0], key), orig_values[key])
                else:
                    self.assertEqual(response.data['data'][key], 7)
            with as_admin(user=user, group=group):
                # test increase stock succeeds if staff and if administrator
                response = client.patch(f'/api/v2/stock/{stock[0].pk}/', data={"units_total": 77}, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['data']['units_total'], 77)
                """test changing other values succeeds if staff and administrator"""
                # first delete units_to_transfer from test, as that wouldn't be changed as not part of model
                del new_values['units_to_transfer']
                # now run test
                for key, value in new_values.items():
                    response = client.patch(f'/api/v2/stock/{stock[0].pk}/', data={key: value}, format='json')
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertNotEqual(response.data['data'][key], str(orig_values[key]))

    def test_perform_destroy(self):
        # setup
        user = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPwd8ntGr8', is_staff=False)
        group = Group.objects.create(name='administrators')  # create 'administrators' group
        token = Token.objects.get(user__username='tester')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        stock = StockDataViewSetTestCase.create_stock(number=25, user=user)  # list of 25 stock objects
        # test returns 403 if not staff
        response = client.delete(f'/api/v2/stock/{stock[11].pk}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        with as_staff(user):
            # test returns 403 if staff but not administrator
            response = client.delete(f'/api/v2/stock/{stock[11].pk}/', format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data[0], 'You are not authorized to delete stock lines!')
            with as_admin(user=user, group=group):
                # test deletes stock item if staff and administrator
                response = client.delete(f'/api/v2/stock/{stock[11].pk}/', format='json')
                assert response.status_code == status.HTTP_204_NO_CONTENT
                verify_response = client.get(f'/api/v2/stock/{stock[11].pk}/', format='json')
                assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    def test_perform_bulk_partial_update(self):
        # setup
        user = User.objects.create_user('tester', settings.DEFAULT_FROM_EMAIL, 'myPwd8ntGr8', is_staff=False)
        group = Group.objects.create(name='administrators')  # create 'administrators' group
        token = Token.objects.get(user__username='tester')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        stock = StockDataViewSetTestCase.create_stock(number=25, user=user)  # list of 25 stock objects
        # test returns 403 if user not staff
        response = client.patch(f'/api/v2/stock/', data={"units_total": 77}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        with as_staff(user):
            """test changing any other value than units_to_transfer is ignored if staff but not administrator
            and also that units_to_transfer is accepted"""
            orig_values = {
                "records": [
                    {"id": stock[0].id, "desc": stock[0].desc, "units_total": stock[0].units_total,
                     "unit_price": stock[0].unit_price, "sku": stock[0].sku}]}
            new_values = {
                "records": [{"id": stock[0].id, "desc": "A new description", "unit_price": "56.32", "sku": "896-528",
                             "units_to_transfer": "7", "units_total": "777"}]}
            response = client.patch(f'/api/v2/stock/', data=new_values, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            for key, value in response.data[0]['data'].items():
                if key in new_values['records'][0]:
                    if key != 'units_to_transfer':
                        self.assertEqual(str(response.data[0]['data'][key]), str(orig_values['records'][0][key]))
                    else:
                        self.assertEqual(str(response.data[0]['data'][key]), "7")
            with as_admin(user=user, group=group):
                # test increase stock succeeds if staff and if administrator
                response = client.patch(f'/api/v2/stock/', data=new_values, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data[0]['data']['units_total'], 777)
                """test changing other values succeeds if staff and administrator"""
                # first delete units_to_transfer from test, as that wouldn't be changed as not part of model
                del new_values['records'][0]['units_to_transfer']
                # now run test
                for key, value in new_values['records'][0].items():
                    if key != 'id':  # id clearly will not change, so ignore that in test
                        response = client.patch(f'/api/v2/stock/', data=new_values, format='json')
                        self.assertEqual(response.status_code, status.HTTP_200_OK)
                        self.assertNotEqual(str(response.data[0]['data'][key]), str(orig_values['records'][0][key]))
