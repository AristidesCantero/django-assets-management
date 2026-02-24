"""
Tests for Location API endpoints (Business, Headquarter, InternalLocation).

This module contains comprehensive tests for:
- Business API (list, create, retrieve, update, delete)
- Headquarter API (list, create, retrieve, update)
- InternalLocation API (list, create, retrieve, update, delete)
"""

from django.test import TestCase, tag
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.domain.models import User
from locations.domain.models import Business, Headquarters, InternalLocation
from permissions.domain.models import UserBusinessPermission, GroupBusinessPermission
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType


class BaseLocationTestCase(APITestCase):
    """Base test case with common setup for location tests."""
    
    @classmethod
    def get_user_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def assertPermission(self, method, url, expected_status, data=None, bearer_token="", content_type='application/json'):
        """Helper to test permissions for a specific method"""
        headers = { "Authorization": f'Bearer {bearer_token}',  "Content-Type": content_type }
        if method == 'get':
            response = self.client.get(url, headers=headers)
        elif method == 'post':
            response = self.client.post(url, data or {}, headers=headers, format='json')
        elif method == 'patch':
            response = self.client.patch(url, data or {}, headers=headers, format='json')
        elif method == 'delete':
            response = self.client.delete(url, headers=headers, format='json')
        elif method == 'put':
            response = self.client.put(url, data or {}, headers=headers, format='json')

        try:
            if isinstance(expected_status, list):
                self.assertIn(response.status_code, expected_status)
                return response
            
            self.assertEqual(response.status_code, expected_status)
            return response
        except AssertionError:
            print(AssertionError)
            print(response.json())
            raise 

    @classmethod        
    def create_permissions_dict(self, business_id, permissions_ids):
        context = { 'permissions': {business_id : {
                            permission_id : True for permission_id in permissions_ids
                        } }}
        return context
    
    @classmethod
    def create_groups_dict(self, business_id, groups_ids):
        context = { 'groups': { business_id : {
                    group_id : True for group_id in groups_ids
        }  }}
        return context
    
    @classmethod
    def set_permissions(self, access_user, business_id: str, permissions_ids : list[str], user_id = str):
        if not isinstance(access_user, User):
            raise TypeError(f'access_user expected as User type, recieved {type(access_user)}')

        if not isinstance(user_id,str) and not isinstance(user_id,int):
            raise TypeError(f'user_id expected to be str or int, recieved {type(user_id)}')
        
        if not isinstance(permissions_ids,list):
            raise TypeError(f'permissions_ids expected list, recieved {type(permissions_ids)}')

        context = self.create_permissions_dict(business_id=business_id, permissions_ids=permissions_ids)
        url = f"/users/usuario/{user_id}/"
        bearer_token = self.get_user_token(user=access_user)

        return self.client.patch(path=url, data=context, headers={ "Authorization": f'Bearer {bearer_token}',  "Content-Type": 'application/json'}, format='json')
    
    @classmethod
    def set_groups(self, access_user, business_id: str, groups_ids: list[str], user_id: str):
        context = self.create_groups_dict(business_id=business_id, groups_ids=groups_ids)
        url = f"/users/usuario/{user_id}/"
        bearer_token = self.get_user_token(access_user)
        return self.client.patch(path=url, data=context, headers={ "Authorization": f'Bearer {bearer_token}',  "Content-Type": 'application/json'}, format='json')

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        print("creating database data for locations tests........")
        cls.client = APIClient()
        
        # Create a superuser for testing
        cls.superuser = User.objects.create_superuser(
            username='admin_location_test',
            email='admin_location@test.com',
            name='Admin',
            last_name='Location',
            password='adminpassword123'
        )

        # Authorized user with permissions        
        cls.auth_user = User.objects.create_user(
            username='auth_location_test',
            email='regular_location@test.com',
            name='Auth',
            last_name='Location',
            password='authpassword123'
        )

        # Create a regular user without permissions
        cls.regular_user = User.objects.create_user(
            username='regular_location_user',
            email='regular_location_user@test.com',
            name='Regular',
            last_name='Location',
            password='authpassword123'
        )
        
        # Create another regular user
        cls.another_user = User.objects.create_user(
            username='another_location_test',
            email='another_location@test.com',
            name='Another',
            last_name='Location',
            password='anotherpassword123'
        )
        
        # Create test business
        cls.business = Business.objects.create(
            name='Test Business Location',
            tin='1234567890',
            utr='djvkjdfvki'
        )
        
        # Create second test business
        cls.business2 = Business.objects.create(
            name='Test Business Location 2',
            tin='098765432-1',
            utr='QWERTYUIOPA'
        )
        
        # Create test headquarters
        cls.headquarter = Headquarters.objects.create(
            name='Test Headquarter',
            address='Test Address 123',
            phone='3014567890',
            business_key=cls.business
        )
        
        # Create test internal location
        cls.internal_location = InternalLocation.objects.create(
            name='Test Internal Location',
            floor='1',
            room_number='101',
            headquarters_key=cls.headquarter
        )
        
        # Get the admin group
        cls.admin_group = Group.objects.get(name='ADMIN')
        cls.manager_group = Group.objects.get(name='MANAGER')
        
        # URL patterns for locations
        cls.business_list_url = '/locations/businesses/'
        cls.business_detail_url = '/locations/business/'
        cls.headquarter_list_url = '/locations/headquarters/'
        cls.headquarter_detail_url = '/locations/headquarter/'
        cls.internal_location_list_url = '/locations/internallocations/'
        cls.internal_location_detail_url = '/locations/internallocation/'
        
        print("locations database seeded!")


# ============================================================================
# BUSINESS TESTS
# ============================================================================

class TestSuperUserBusinessAPIView(BaseLocationTestCase):
    """Tests for Business API with superuser access."""
       
    @tag('business', 'superuser', 'business_list_get_superuser')
    def test_list_business_superuser_get(self):
        """Test that superuser can list all businesses."""
        token = self.get_user_token(self.superuser)
        self.assertPermission(method='get', url=self.business_list_url, expected_status=status.HTTP_200_OK, bearer_token=token)
        print('superuser business list get test passed')

    @tag('business', 'superuser', 'business_list_post_superuser')
    def test_list_business_superuser_post(self):
        """Test that superuser can create a business."""
        token = self.get_user_token(self.superuser)
        new_business = {
            'name': 'New Test Business',
            'tin': '987654321-0',
            'utr': 'newutr1234'
        }
        self.assertPermission('post', self.business_list_url, status.HTTP_201_CREATED, new_business, bearer_token=token)
        print('superuser business list post test passed')

    @tag('business', 'superuser', 'business_detail_get_superuser')
    def test_business_superuser_get(self):
        """Test that superuser can retrieve a business."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get', f'{self.business_detail_url}{self.business.id}/', status.HTTP_200_OK, bearer_token=token)
        print('superuser business get test passed')

    @tag('business', 'superuser', 'business_detail_patch_superuser')
    def test_business_superuser_patch(self):
        """Test that superuser can update a business."""
        token = self.get_user_token(self.superuser)
        data = {'name': 'Updated Business Name'}
        self.assertPermission('patch', f'{self.business_detail_url}{self.business.id}/', status.HTTP_200_OK, data=data, bearer_token=token)
        print('superuser business patch test passed')

    @tag('business', 'superuser', 'business_detail_delete_superuser')
    def test_business_superuser_delete(self):
        """Test that superuser can delete a business."""
        token = self.get_user_token(self.superuser)
        # Create a business to delete
        business_to_delete = Business.objects.create(
            name='Business To Delete',
            tin='555555555-5',
            utr='deleteme12'
        )
        self.assertPermission('delete', f'{self.business_detail_url}{business_to_delete.id}/', status.HTTP_200_OK, bearer_token=token)
        print('superuser business delete test passed')


class TestAuthorizedUnauthorizedBusinessAPIView(BaseLocationTestCase):
    """Tests for Business API with authorized and unauthorized users."""
    
    @classmethod
    def setUpTestData(cls):
        database_setup = super().setUpTestData()
        # Setup permissions for authorized user
        content_type_id = ContentType.objects.get(model='business').id
        permissions = [permission.id for permission in Permission.objects.filter(content_type=content_type_id)]
        cls.set_permissions(access_user=cls.superuser, business_id=cls.business.id, permissions_ids=permissions, user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.admin_group.id], user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.manager_group.id], user_id=cls.regular_user.id)
        return database_setup

    @tag('business', 'auth', 'business_list_get_authorized')
    def test_list_business_auth_user_get(self):
        """Test that authorized user can list businesses."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('get', self.business_list_url, status.HTTP_200_OK, bearer_token=token)
        print('auth user business list get test passed')

    @tag('business', 'auth', 'business_list_post_authorized')
    def test_list_business_auth_user_post(self):
        """Test that authorized user can create a business."""
        token = self.get_user_token(self.auth_user)
        new_business = {
            'name': 'Auth User Business',
            'tin': '111111111-1',
            'utr': 'authuser12'
        }
        self.assertPermission('post', self.business_list_url, status.HTTP_201_CREATED, new_business, bearer_token=token)
        print('auth user business list post test passed')

    @tag('business', 'auth', 'business_detail_get_authorized')
    def test_business_auth_user_get(self):
        """Test that authorized user can retrieve a business."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('get', f'{self.business_detail_url}{self.business.id}/', status.HTTP_200_OK, bearer_token=token)
        print('auth user business get test passed')

    @tag('business', 'auth', 'business_detail_patch_authorized')
    def test_business_auth_user_patch(self):
        """Test that authorized user can update a business."""
        token = self.get_user_token(self.auth_user)
        data = {'name': 'Auth Updated Business'}
        self.assertPermission('patch', f'{self.business_detail_url}{self.business.id}/', status.HTTP_200_OK, data=data, bearer_token=token)
        print('auth user business patch test passed')

    @tag('business', 'not_auth', 'business_list_get_unauth')
    def test_list_business_not_auth_user_get(self):
        """Test that unauthorized user cannot list businesses."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('get', self.business_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token=token)
        print('not auth user business list get test passed')

    @tag('business', 'not_auth', 'business_list_post_unauth')
    def test_list_business_not_auth_user_post(self):
        """Test that unauthorized user cannot create a business."""
        token = self.get_user_token(self.regular_user)
        new_business = {
            'name': 'Unauthorized Business',
            'tin': '222222222-2',
            'utr': 'unauth123'
        }
        self.assertPermission('post', self.business_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], new_business, bearer_token=token)
        print('not auth user business list post test passed')

    @tag('business', 'not_auth', 'business_detail_get_unauth')
    def test_business_not_auth_user_get(self):
        """Test that unauthorized user cannot retrieve a business."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('get', f'{self.business_detail_url}{self.business.id}/', [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token=token)
        print('not auth user business get test passed')

    @tag('business', 'not_auth', 'business_detail_patch_unauth')
    def test_business_not_auth_user_patch(self):
        """Test that unauthorized user cannot update a business."""
        token = self.get_user_token(self.regular_user)
        data = {'name': 'Unauthorized Update'}
        self.assertPermission('patch', f'{self.business_detail_url}{self.business.id}/', [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], data=data, bearer_token=token)
        print('not auth user business patch test passed')

    @tag('business', 'not_auth', 'business_detail_no_token')
    def test_business_no_token_get(self):
        """Test that unauthenticated request is rejected."""
        self.assertPermission('get', self.business_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token='')
        print('no token business get test passed')


class TestBusinessIncorrectAPICalls(BaseLocationTestCase):
    """Tests for incorrect API calls on Business endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        database_setup = super().setUpTestData()
        # Setup permissions for authorized user
        content_type_id = ContentType.objects.get(model='business').id
        permissions = [permission.id for permission in Permission.objects.filter(content_type=content_type_id)]
        cls.set_permissions(access_user=cls.superuser, business_id=cls.business.id, permissions_ids=permissions, user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.admin_group.id], user_id=cls.auth_user.id)
        return database_setup

    @tag('business', 'incorrect', 'business_non_existing_business')
    def test_retrieve_nonexistent_business(self):
        """Test retrieving a non-existent business."""
        token = self.get_user_token(self.superuser)
        url = f'{self.business_detail_url}99999/'
        self.assertPermission(url=url, method='get', expected_status=status.HTTP_404_NOT_FOUND, bearer_token=token)
        print('retrieve non-existent business test passed')

    @tag('business', 'incorrect', 'business_invalid_data')
    def test_create_business_invalid_data(self):
        """Test creating a business with invalid data."""
        token = self.get_user_token(self.superuser)
        invalid_data = {
            'name': '',  # Invalid: empty name
            'tin': '',   # Invalid: empty tin
            'utr': ''    # Invalid: empty utr
        }
        self.assertPermission('post', self.business_list_url, status.HTTP_400_BAD_REQUEST, invalid_data, bearer_token=token)
        print('create business with invalid data test passed')

    @tag('business', 'incorrect', 'business_duplicate_tin')
    def test_create_business_duplicate_tin(self):
        """Test creating a business with duplicate TIN."""
        token = self.get_user_token(self.superuser)
        duplicate_data = {
            'name': 'Another Business',
            'tin': '1234567890',  # Already exists
            'utr': 'newutr12345'
        }
        self.assertPermission('post', self.business_list_url, status.HTTP_400_BAD_REQUEST, duplicate_data, bearer_token=token)
        print('create business with duplicate tin test passed')

    @tag('business', 'incorrect', 'business_update_non_existing')
    def test_update_nonexistent_business(self):
        """Test updating a non-existent business."""
        token = self.get_user_token(self.superuser)
        url = f'{self.business_detail_url}99999/'
        data = {'name': 'Updated Name'}
        self.assertPermission('patch', url, status.HTTP_404_NOT_FOUND, data=data, bearer_token=token)
        print('update non-existent business test passed')

    @tag('business', 'incorrect', 'business_delete_non_existing')
    def test_delete_nonexistent_business(self):
        """Test deleting a non-existent business."""
        token = self.get_user_token(self.superuser)
        url = f'{self.business_detail_url}99999/'
        self.assertPermission('delete', url, status.HTTP_404_NOT_FOUND, bearer_token=token)
        print('delete non-existent business test passed')

    @tag('business', 'incorrect', 'business_invalid_business_id')
    def test_get_business_invalid_id_format(self):
        """Test getting a business with invalid ID format."""
        token = self.get_user_token(self.superuser)
        url = f'{self.business_detail_url}abc/'
        self.assertPermission('get', url, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST], bearer_token=token)
        print('get business with invalid id format test passed')


# ============================================================================
# HEADQUARTER TESTS
# ============================================================================

class TestSuperUserHeadquarterAPIView(BaseLocationTestCase):
    """Tests for Headquarter API with superuser access."""
       
    @tag('headquarter', 'superuser', 'list_get')
    def test_list_headquarter_superuser_get(self):
        """Test that superuser can list all headquarters."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get', self.headquarter_list_url, status.HTTP_200_OK, bearer_token=token)
        print('superuser headquarter list get test passed')

    @tag('headquarter', 'superuser', 'list_post')
    def test_list_headquarter_superuser_post(self):
        """Test that superuser can create a headquarter."""
        token = self.get_user_token(self.superuser)
        new_headquarter = {
            'name': 'New Test Headquarter',
            'address': 'New Address 456',
            'phone': '+9876543210',
            'business_key': self.business.id
        }
        self.assertPermission('post', self.headquarter_list_url, status.HTTP_201_CREATED, new_headquarter, bearer_token=token)
        print('superuser headquarter list post test passed')

    @tag('headquarter', 'superuser', 'detail_get')
    def test_headquarter_superuser_get(self):
        """Test that superuser can retrieve a headquarter."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get', f'{self.headquarter_detail_url}{self.headquarter.id}/', status.HTTP_200_OK, bearer_token=token)
        print('superuser headquarter get test passed')

    @tag('headquarter', 'superuser', 'detail_patch')
    def test_headquarter_superuser_patch(self):
        """Test that superuser can update a headquarter."""
        token = self.get_user_token(self.superuser)
        data = {'name': 'Updated Headquarter Name'}
        self.assertPermission('patch', f'{self.headquarter_detail_url}{self.headquarter.id}/', status.HTTP_200_OK, data=data, bearer_token=token)
        print('superuser headquarter patch test passed')


class TestAuthorizedUnauthorizedHeadquarterAPIView(BaseLocationTestCase):
    """Tests for Headquarter API with authorized and unauthorized users."""
    
    @classmethod
    def setUpTestData(cls):
        database_setup = super().setUpTestData()
        # Setup permissions for authorized user
        content_type_id = ContentType.objects.get(model='headquarters').id
        permissions = [permission.id for permission in Permission.objects.filter(content_type=content_type_id)]
        cls.set_permissions(access_user=cls.superuser, business_id=cls.business.id, permissions_ids=permissions, user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.admin_group.id], user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.manager_group.id], user_id=cls.regular_user.id)
        return database_setup

    @tag('headquarter', 'auth', 'list_get')
    def test_list_headquarter_auth_user_get(self):
        """Test that authorized user can list headquarters."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('get', self.headquarter_list_url, status.HTTP_200_OK, bearer_token=token)
        print('auth user headquarter list get test passed')

    @tag('headquarter', 'auth', 'list_post')
    def test_list_headquarter_auth_user_post(self):
        """Test that authorized user can create a headquarter."""
        token = self.get_user_token(self.auth_user)
        new_headquarter = {
            'name': 'Auth User Headquarter',
            'address': 'Auth Address 789',
            'phone': '+1111111111',
            'business_key': self.business.id
        }
        self.assertPermission('post', self.headquarter_list_url, status.HTTP_201_CREATED, new_headquarter, bearer_token=token)
        print('auth user headquarter list post test passed')

    @tag('headquarter', 'auth', 'detail_get')
    def test_headquarter_auth_user_get(self):
        """Test that authorized user can retrieve a headquarter."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('get', f'{self.headquarter_detail_url}{self.headquarter.id}/', status.HTTP_200_OK, bearer_token=token)
        print('auth user headquarter get test passed')

    @tag('headquarter', 'auth', 'detail_patch')
    def test_headquarter_auth_user_patch(self):
        """Test that authorized user can update a headquarter."""
        token = self.get_user_token(self.auth_user)
        data = {'name': 'Auth Updated Headquarter'}
        self.assertPermission('patch', f'{self.headquarter_detail_url}{self.headquarter.id}/', status.HTTP_200_OK, data=data, bearer_token=token)
        print('auth user headquarter patch test passed')

    @tag('headquarter', 'not_auth', 'list_get')
    def test_list_headquarter_not_auth_user_get(self):
        """Test that unauthorized user cannot list headquarters."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('get', self.headquarter_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token=token)
        print('not auth user headquarter list get test passed')

    @tag('headquarter', 'not_auth', 'list_post')
    def test_list_headquarter_not_auth_user_post(self):
        """Test that unauthorized user cannot create a headquarter."""
        token = self.get_user_token(self.regular_user)
        new_headquarter = {
            'name': 'Unauthorized Headquarter',
            'address': 'Unauthorized Address',
            'phone': '+2222222222',
            'business_key': self.business.id
        }
        self.assertPermission('post', self.headquarter_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], new_headquarter, bearer_token=token)
        print('not auth user headquarter list post test passed')

    @tag('headquarter', 'not_auth', 'detail_get')
    def test_headquarter_not_auth_user_get(self):
        """Test that unauthorized user cannot retrieve a headquarter."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('get', f'{self.headquarter_detail_url}{self.headquarter.id}/', [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token=token)
        print('not auth user headquarter get test passed')

    @tag('headquarter', 'not_auth', 'no_token')
    def test_headquarter_no_token_get(self):
        """Test that unauthenticated request is rejected."""
        self.assertPermission('get', self.headquarter_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token='')
        print('no token headquarter get test passed')


class TestHeadquarterIncorrectAPICalls(BaseLocationTestCase):
    """Tests for incorrect API calls on Headquarter endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        database_setup = super().setUpTestData()
        # Setup permissions for authorized user
        content_type_id = ContentType.objects.get(model='headquarters').id
        permissions = [permission.id for permission in Permission.objects.filter(content_type=content_type_id)]
        cls.set_permissions(access_user=cls.superuser, business_id=cls.business.id, permissions_ids=permissions, user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.admin_group.id], user_id=cls.auth_user.id)
        return database_setup

    @tag('headquarter', 'incorrect', 'non_existing')
    def test_retrieve_nonexistent_headquarter(self):
        """Test retrieving a non-existent headquarter."""
        token = self.get_user_token(self.superuser)
        url = f'{self.headquarter_detail_url}99999/'
        self.assertPermission(url=url, method='get', expected_status=status.HTTP_404_NOT_FOUND, bearer_token=token)
        print('retrieve non-existent headquarter test passed')

    @tag('headquarter', 'incorrect', 'invalid_data')
    def test_create_headquarter_invalid_data(self):
        """Test creating a headquarter with invalid data."""
        token = self.get_user_token(self.superuser)
        invalid_data = {
            'name': '',  # Invalid: empty name
            'address': '',  # Invalid: empty address
            'phone': '',  # Invalid: empty phone
            'business_key': None  # Invalid: no business
        }
        self.assertPermission('post', self.headquarter_list_url, status.HTTP_400_BAD_REQUEST, invalid_data, bearer_token=token)
        print('create headquarter with invalid data test passed')

    @tag('headquarter', 'incorrect', 'invalid_business')
    def test_create_headquarter_invalid_business(self):
        """Test creating a headquarter with non-existent business."""
        token = self.get_user_token(self.superuser)
        invalid_data = {
            'name': 'Test Headquarter',
            'address': 'Test Address',
            'phone': '+1234567890',
            'business_key': 99999  # Non-existent business
        }
        self.assertPermission('post', self.headquarter_list_url, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND], invalid_data, bearer_token=token)
        print('create headquarter with invalid business test passed')

    @tag('headquarter', 'incorrect', 'update_non_existing')
    def test_update_nonexistent_headquarter(self):
        """Test updating a non-existent headquarter."""
        token = self.get_user_token(self.superuser)
        url = f'{self.headquarter_detail_url}99999/'
        data = {'name': 'Updated Name'}
        self.assertPermission('patch', url, status.HTTP_404_NOT_FOUND, data=data, bearer_token=token)
        print('update non-existent headquarter test passed')

    @tag('headquarter', 'incorrect', 'invalid_id_format')
    def test_get_headquarter_invalid_id_format(self):
        """Test getting a headquarter with invalid ID format."""
        token = self.get_user_token(self.superuser)
        url = f'{self.headquarter_detail_url}abc/'
        self.assertPermission('get', url, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST], bearer_token=token)
        print('get headquarter with invalid id format test passed')


# ============================================================================
# INTERNAL LOCATION TESTS
# ============================================================================

class TestSuperUserInternalLocationAPIView(BaseLocationTestCase):
    """Tests for InternalLocation API with superuser access."""
       
    @tag('internal_location', 'superuser', 'list_get')
    def test_list_internal_location_superuser_get(self):
        """Test that superuser can list all internal locations."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get', self.internal_location_list_url, status.HTTP_200_OK, bearer_token=token)
        print('superuser internal location list get test passed')

    @tag('internal_location', 'superuser', 'list_post')
    def test_list_internal_location_superuser_post(self):
        """Test that superuser can create an internal location."""
        token = self.get_user_token(self.superuser)
        new_internal_location = {
            'name': 'New Test Internal Location',
            'floor': '2',
            'room_number': '202',
            'headquarters_key': self.headquarter.id
        }
        self.assertPermission('post', self.internal_location_list_url, status.HTTP_201_CREATED, new_internal_location, bearer_token=token)
        print('superuser internal location list post test passed')

    @tag('internal_location', 'superuser', 'detail_get')
    def test_internal_location_superuser_get(self):
        """Test that superuser can retrieve an internal location."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get', f'{self.internal_location_detail_url}{self.internal_location.id}/', status.HTTP_200_OK, bearer_token=token)
        print('superuser internal location get test passed')

    @tag('internal_location', 'superuser', 'detail_patch')
    def test_internal_location_superuser_patch(self):
        """Test that superuser can update an internal location."""
        token = self.get_user_token(self.superuser)
        data = {'name': 'Updated Internal Location Name'}
        self.assertPermission('patch', f'{self.internal_location_detail_url}{self.internal_location.id}/', status.HTTP_200_OK, data=data, bearer_token=token)
        print('superuser internal location patch test passed')

    @tag('internal_location', 'superuser', 'detail_delete')
    def test_internal_location_superuser_delete(self):
        """Test that superuser can delete an internal location."""
        token = self.get_user_token(self.superuser)
        # Create an internal location to delete
        internal_location_to_delete = InternalLocation.objects.create(
            name='Internal Location To Delete',
            floor='5',
            room_number='505',
            headquarters_key=self.headquarter
        )
        self.assertPermission('delete', f'{self.internal_location_detail_url}{internal_location_to_delete.id}/', status.HTTP_204_NO_CONTENT, bearer_token=token)
        print('superuser internal location delete test passed')


class TestAuthorizedUnauthorizedInternalLocationAPIView(BaseLocationTestCase):
    """Tests for InternalLocation API with authorized and unauthorized users."""
    
    @classmethod
    def setUpTestData(cls):
        database_setup = super().setUpTestData()
        # Setup permissions for authorized user
        content_type_id = ContentType.objects.get(model='internallocation').id
        permissions = [permission.id for permission in Permission.objects.filter(content_type=content_type_id)]
        cls.set_permissions(access_user=cls.superuser, business_id=cls.business.id, permissions_ids=permissions, user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.admin_group.id], user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.manager_group.id], user_id=cls.regular_user.id)
        return database_setup

    @tag('internal_location', 'auth', 'list_get')
    def test_list_internal_location_auth_user_get(self):
        """Test that authorized user can list internal locations."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('get', self.internal_location_list_url, status.HTTP_200_OK, bearer_token=token)
        print('auth user internal location list get test passed')

    @tag('internal_location', 'auth', 'list_post')
    def test_list_internal_location_auth_user_post(self):
        """Test that authorized user can create an internal location."""
        token = self.get_user_token(self.auth_user)
        new_internal_location = {
            'name': 'Auth User Internal Location',
            'floor': '3',
            'room_number': '303',
            'headquarters_key': self.headquarter.id
        }
        self.assertPermission('post', self.internal_location_list_url, status.HTTP_201_CREATED, new_internal_location, bearer_token=token)
        print('auth user internal location list post test passed')

    @tag('internal_location', 'auth', 'detail_get')
    def test_internal_location_auth_user_get(self):
        """Test that authorized user can retrieve an internal location."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('get', f'{self.internal_location_detail_url}{self.internal_location.id}/', status.HTTP_200_OK, bearer_token=token)
        print('auth user internal location get test passed')

    @tag('internal_location', 'auth', 'detail_patch')
    def test_internal_location_auth_user_patch(self):
        """Test that authorized user can update an internal location."""
        token = self.get_user_token(self.auth_user)
        data = {'name': 'Auth Updated Internal Location'}
        self.assertPermission('patch', f'{self.internal_location_detail_url}{self.internal_location.id}/', status.HTTP_200_OK, data=data, bearer_token=token)
        print('auth user internal location patch test passed')

    @tag('internal_location', 'not_auth', 'list_get')
    def test_list_internal_location_not_auth_user_get(self):
        """Test that unauthorized user cannot list internal locations."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('get', self.internal_location_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token=token)
        print('not auth user internal location list get test passed')

    @tag('internal_location', 'not_auth', 'list_post')
    def test_list_internal_location_not_auth_user_post(self):
        """Test that unauthorized user cannot create an internal location."""
        token = self.get_user_token(self.regular_user)
        new_internal_location = {
            'name': 'Unauthorized Internal Location',
            'floor': '4',
            'room_number': '404',
            'headquarters_key': self.headquarter.id
        }
        self.assertPermission('post', self.internal_location_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], new_internal_location, bearer_token=token)
        print('not auth user internal location list post test passed')

    @tag('internal_location', 'not_auth', 'detail_get')
    def test_internal_location_not_auth_user_get(self):
        """Test that unauthorized user cannot retrieve an internal location."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('get', f'{self.internal_location_detail_url}{self.internal_location.id}/', [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token=token)
        print('not auth user internal location get test passed')

    @tag('internal_location', 'not_auth', 'no_token')
    def test_internal_location_no_token_get(self):
        """Test that unauthenticated request is rejected."""
        self.assertPermission('get', self.internal_location_list_url, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED], bearer_token='')
        print('no token internal location get test passed')


class TestInternalLocationIncorrectAPICalls(BaseLocationTestCase):
    """Tests for incorrect API calls on InternalLocation endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        database_setup = super().setUpTestData()
        # Setup permissions for authorized user
        content_type_id = ContentType.objects.get(model='internallocation').id
        permissions = [permission.id for permission in Permission.objects.filter(content_type=content_type_id)]
        cls.set_permissions(access_user=cls.superuser, business_id=cls.business.id, permissions_ids=permissions, user_id=cls.auth_user.id)
        cls.set_groups(access_user=cls.superuser, business_id=cls.business.id, groups_ids=[cls.admin_group.id], user_id=cls.auth_user.id)
        return database_setup

    @tag('internal_location', 'incorrect', 'non_existing')
    def test_retrieve_nonexistent_internal_location(self):
        """Test retrieving a non-existent internal location."""
        token = self.get_user_token(self.superuser)
        url = f'{self.internal_location_detail_url}99999/'
        self.assertPermission(url=url, method='get', expected_status=status.HTTP_404_NOT_FOUND, bearer_token=token)
        print('retrieve non-existent internal location test passed')

    @tag('internal_location', 'incorrect', 'invalid_data')
    def test_create_internal_location_invalid_data(self):
        """Test creating an internal location with invalid data."""
        token = self.get_user_token(self.superuser)
        invalid_data = {
            'name': '',  # Invalid: empty name
            'floor': '',  # Invalid: empty floor
            'room_number': '',  # Invalid: empty room number
            'headquarters_key': None  # Invalid: no headquarter
        }
        self.assertPermission('post', self.internal_location_list_url, status.HTTP_400_BAD_REQUEST, invalid_data, bearer_token=token)
        print('create internal location with invalid data test passed')

    @tag('internal_location', 'incorrect', 'invalid_headquarter')
    def test_create_internal_location_invalid_headquarter(self):
        """Test creating an internal location with non-existent headquarter."""
        token = self.get_user_token(self.superuser)
        invalid_data = {
            'name': 'Test Internal Location',
            'floor': '1',
            'room_number': '101',
            'headquarters_key': 99999  # Non-existent headquarter
        }
        self.assertPermission('post', self.internal_location_list_url, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND], invalid_data, bearer_token=token)
        print('create internal location with invalid headquarter test passed')

    @tag('internal_location', 'incorrect', 'update_non_existing')
    def test_update_nonexistent_internal_location(self):
        """Test updating a non-existent internal location."""
        token = self.get_user_token(self.superuser)
        url = f'{self.internal_location_detail_url}99999/'
        data = {'name': 'Updated Name'}
        self.assertPermission('patch', url, status.HTTP_404_NOT_FOUND, data=data, bearer_token=token)
        print('update non-existent internal location test passed')

    @tag('internal_location', 'incorrect', 'delete_non_existing')
    def test_delete_nonexistent_internal_location(self):
        """Test deleting a non-existent internal location."""
        token = self.get_user_token(self.superuser)
        url = f'{self.internal_location_detail_url}99999/'
        self.assertPermission('delete', url, status.HTTP_404_NOT_FOUND, bearer_token=token)
        print('delete non-existent internal location test passed')

    @tag('internal_location', 'incorrect', 'invalid_id_format')
    def test_get_internal_location_invalid_id_format(self):
        """Test getting an internal location with invalid ID format."""
        token = self.get_user_token(self.superuser)
        url = f'{self.internal_location_detail_url}abc/'
        self.assertPermission('get', url, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST], bearer_token=token)
        print('get internal location with invalid id format test passed')
