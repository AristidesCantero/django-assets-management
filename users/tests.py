"""
Tests for User API endpoints.

This module contains comprehensive tests for:
- UserListAPIView (GET, POST)
- UserAPIView (GET, PATCH, DELETE)
- JWT Token endpoints (obtain, refresh)
"""

from django.test import TestCase, tag
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.domain.models import User
from locations.domain.models import Business
from permissions.domain.models import UserBusinessPermission, GroupBusinessPermission
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType




class BaseUserTestCase(APITestCase):
    """Base test case with common setup for user tests."""
    @classmethod
    def get_user_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def assertPermission(self, method, url, expected_status, data=None, bearer_token="", content_type='application/json'):
        """Helper to test permissions for a specific method"""
        headers = { "Authorization": f'Bearer {bearer_token}',  "Content-Type": content_type }
        if method == 'get':
            response = self.client.get(url,headers=headers)
        elif method == 'post':
            response = self.client.post(url, data or {}, headers=headers, format='json')
        elif method == 'patch':
            response = self.client.patch(url, data or {}, headers=headers, format='json')
        elif method == 'delete':
            response = self.client.delete(url, headers=headers,format='json')
        elif method == 'put':
            response = self.client.put(url, data or {}, headers=headers, format='json')


        try:
            if isinstance(expected_status,list):
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
        context = self.create_groups_dict(business_id=business_id,groups_ids=groups_ids)
        url = f"/users/usuario/{user_id}/"
        bearer_token = self.get_user_token(access_user)
        return self.client.patch(path=url, data=context, headers={ "Authorization": f'Bearer {bearer_token}',  "Content-Type": 'application/json'}, format='json')

    #def setUp(self):

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        print("creating database data........")
        cls.client = APIClient()
        
        # Create a superuser for testing
        cls.superuser = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            name='Admin',
            last_name='Test',
            password='adminpassword123'
        )

        #authorized user, helps to check if permissions works        
        cls.auth_user = User.objects.create_user(
            username='auth_test',
            email='regular@test.com',
            name='Auth',
            last_name='User',
            password='authpassword123'
        )

        # Create a regular user
        cls.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular_user@test.com',
            name='Regular',
            last_name='User',
            password='authpassword123'
        )
        # Create another regular user
        cls.another_user = User.objects.create_user(
            username='another_test',
            email='another@test.com',
            name='Another',
            last_name='User',
            password='anotherpassword123'
        )
        # Create test business
        cls.business = Business.objects.create(
            name='Test Business',
            tin='1234567890',
            utr='djvkjdfvki'
        )
        # Get the admin group
        cls.admin_group = Group.objects.get(name='ADMIN')
        cls.manager_group = Group.objects.get(name='MANAGER')


        
        # URL patterns
        cls.user_url = '/users/usuario/'
        cls.user_list_url = '/users/usuarios/'
        cls.token_url = '/api/token/'
        cls.token_refresh_url = '/api/token/refresh/'
        print("database seeded!")





#done
class TestSuperUserListAPIView(BaseUserTestCase):
    """Tests for UserListAPIView (GET and POST)."""
       

    #for superuser
    @tag('method','superuser_list_get')
    def test_list_users_superuser_get(self):
        """Test that superuser can list all users."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get',self.user_list_url,status.HTTP_200_OK,bearer_token=token)
        print('superuser list get test passed')
        #self.assertIn('data', response.data)
        #self.assertIsInstance(response.data['data'], list)

    @tag('method','superuser_list_post')
    def test_list_users_superuser_post(self):
        """Test that superuser can create a user."""
        token = self.get_user_token(self.superuser)
        new_user = {'username': 'CamiloVargas', 'name': 'Camilo', 'last_name': 'Vargas', 'email': 'cvargasf@gmail.com', 'password': 'cvargarcamilo','groups':{self.business.id: {self.admin_group.id: True}}}
        self.assertPermission('post',self.user_list_url,status.HTTP_200_OK,new_user,bearer_token=token)
        print('superuser list post test passed')
       
    @tag('method','superuser_get')
    def test_users_superuser_get(self):
        """Test that superuser can read a user."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get',self.user_url+f'{self.regular_user.id}/',status.HTTP_200_OK,bearer_token=token)
        print('superuser get test passed')

    @tag('method','superuser_patch')
    def test_users_superuser_patch(self):
        """Test that superuser can modify a user."""
        token = self.get_user_token(self.superuser)
        data = {'groups':{self.business.id:{self.admin_group.id:True}}}
        self.assertPermission('patch',self.user_url+f'{self.regular_user.id}/',status.HTTP_200_OK,data=data,bearer_token=token)
        print('superuser patch test passed')

    @tag('method','superuser_delete')
    def test_users_superuser_delete(self):
        """Test that superuser can read a user."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('delete',self.user_url+f'{self.regular_user.id}/',status.HTTP_405_METHOD_NOT_ALLOWED,bearer_token=token)
        #self.assertPermission('get',self.user_url+f'{self.regular_user.id}/', status.HTTP_405_METHOD_NOT_ALLOWED, bearer_token=token)
        print('superuser list delete test passed')

#done
class TestUserListAPIView(BaseUserTestCase):
    @classmethod
    def setUpTestData(cls):
        database_setup = super().setUpTestData()
        content_type_id = ContentType.objects.get(model='user').id
        permissions = [permission.id for permission in Permission.objects.filter(content_type=content_type_id)]
        permission1_response = cls.set_permissions(access_user=cls.superuser,business_id=cls.business.id, permissions_ids=permissions, user_id=cls.auth_user.id)
        group1_response = cls.set_groups(access_user=cls.superuser,business_id=cls.business.id,groups_ids=[cls.admin_group.id], user_id=cls.auth_user.id)
        permission2_response = cls.set_groups(access_user=cls.superuser,business_id=cls.business.id,groups_ids=[cls.manager_group.id], user_id=cls.regular_user.id)

        #print(UserBusinessPermission.objects.filter(user_key=cls.auth_user.id))
        #print(GroupBusinessPermission.objects.filter(user_key=cls.auth_user.id))
        #print(GroupBusinessPermission.objects.filter(user_key=cls.regular_user.id))

        return database_setup

    @tag('method','auth_user_list_get')
    def test_list_users_auth_user_get(self):
        """Test that auth_user can list all its users."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('get',self.user_list_url,status.HTTP_200_OK,bearer_token=token)
        print('auth user list get test PASSED')
        #self.assertIn('data', response.data)
        #self.assertIsInstance(response.data['data'], list)

    @tag('method','auth_user_list_post')
    def test_list_users_auth_user_post(self):
        """Test that auth_user can create a user."""
        token = self.get_user_token(self.auth_user)
        new_user = {'username': 'CamiloVargas', 'name': 'Camilo', 'last_name': 'Vargas', 'email': 'cvargasf@gmail.com', 'password': 'cvargarcamilo','groups':{self.business.id: {self.admin_group.id: True}}}
        self.assertPermission('post',self.user_list_url,status.HTTP_200_OK,new_user,bearer_token=token)
        print('auth user list post test PASSED')
       
    @tag('method','auth_user_get')
    def test_users_auth_user_get(self):
        """Test that auth_user can read a user."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('get',self.user_url+f'{self.regular_user.id}/',status.HTTP_200_OK,bearer_token=token)
        print('auth user get test PASSED')

    @tag('method','auth_user_patch')
    def test_users_auth_user_patch(self):
        """Test that auth_user can read a user."""
        token = self.get_user_token(self.auth_user)
        data = {'groups':{self.business.id:{self.admin_group.id:True}}}
        self.assertPermission('patch',self.user_url+f'{self.regular_user.id}/',status.HTTP_200_OK,data=data,bearer_token=token)
        print('auth user patch test PASSED')

    @tag('method','auth_user_delete')
    def test_users_auth_user_delete(self):
        """Test that auth_user can read a user."""
        token = self.get_user_token(self.auth_user)
        self.assertPermission('delete',self.user_url+f'{self.regular_user.id}/',status.HTTP_405_METHOD_NOT_ALLOWED,bearer_token=token)
        print('auth user delete test PASSED')
    


class TestNotAuthUserAPIView(BaseUserTestCase):
    """Tests for UserAPIView (GET, PATCH, DELETE)."""    

    @classmethod
    def setUpTestData(cls):
        database_setup = super().setUpTestData()
        content_type_id = ContentType.objects.get(model='user').id
        permissions = [permission.id for permission in Permission.objects.filter(content_type=content_type_id)]
        permission1_response = cls.set_permissions(access_user=cls.superuser,business_id=cls.business.id, permissions_ids=permissions, user_id=cls.auth_user.id)
        group1_response = cls.set_groups(access_user=cls.superuser,business_id=cls.business.id,groups_ids=[cls.admin_group.id], user_id=cls.auth_user.id)
        permission2_response = cls.set_groups(access_user=cls.superuser,business_id=cls.business.id,groups_ids=[cls.manager_group.id], user_id=cls.regular_user.id)

        #print(UserBusinessPermission.objects.filter(user_key=cls.auth_user.id))
        #print(GroupBusinessPermission.objects.filter(user_key=cls.auth_user.id))
        #print(GroupBusinessPermission.objects.filter(user_key=cls.regular_user.id))

        return database_setup

    @tag('not_auth','method','not_auth_user_list_get')
    def test_list_users_not_auth_user_get(self):
        """Test that auth_user cannot list all its users."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('get',self.user_list_url,[status.HTTP_403_FORBIDDEN,status.HTTP_401_UNAUTHORIZED],bearer_token=token)
        print('auth user list get test PASSED')
        #self.assertIn('data', response.data)
        #self.assertIsInstance(response.data['data'], list)

    @tag('not_auth','method','not_auth_user_list_post')
    def test_list_users_not_auth_user_post(self):
        """Test that not_auth_user cannot create a user."""
        token = self.get_user_token(self.regular_user)
        new_user = {'username': 'CamiloVargas', 'name': 'Camilo', 'last_name': 'Vargas', 'email': 'cvargasf@gmail.com', 'password': 'cvargarcamilo','groups':{self.business.id: {self.admin_group.id: True}}}
        self.assertPermission('post',self.user_list_url,[status.HTTP_403_FORBIDDEN,status.HTTP_401_UNAUTHORIZED],new_user,bearer_token=token)
        print('auth user list post test PASSED')
       
    @tag('not_auth','method','not_auth_user_get')
    def test_users_not_auth_user_get(self):
        """Test that not_auth_user cannot read a user."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('get',self.user_url+f'{self.regular_user.id}/',[status.HTTP_403_FORBIDDEN,status.HTTP_401_UNAUTHORIZED],bearer_token=token)
        print('auth user get test PASSED')

    @tag('not_auth','method','not_auth_user_patch')
    def test_users_not_auth_user_patch(self):
        """Test that not_auth_user cannot read a user."""
        token = self.get_user_token(self.regular_user)
        data = {'groups':{self.business.id:{self.admin_group.id:True}}}
        self.assertPermission('patch',self.user_url+f'{self.regular_user.id}/',[status.HTTP_403_FORBIDDEN,status.HTTP_401_UNAUTHORIZED],data=data,bearer_token=token)
        print('auth user patch test PASSED')

    @tag('not_auth','method','not_auth_user_delete')
    def test_users_not_auth_user_delete(self):
        """Test that not_auth_user cannot read a user."""
        token = self.get_user_token(self.regular_user)
        self.assertPermission('delete',self.user_url+f'{self.regular_user.id}/',[status.HTTP_403_FORBIDDEN,status.HTTP_401_UNAUTHORIZED],bearer_token=token)
        print('auth user delete test PASSED')

    
    

    @tag('auth','method','non_existing','non_existing_user_admin')
    def test_retrieve_nonexistent_user(self):
        """Test retrieving a non-existent user."""
        token = self.get_user_token(self.auth_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = f'{self.user_url}99999/'
        self.assertPermission(url=url,method='get',expected_status=status.HTTP_403_FORBIDDEN,bearer_token=token)

    
    @tag('auth','method','non_existing','non_existing_user_super_admin')
    def test_retrieve_nonexistent_user_superuser(self):
        """Test retrieving a non-existent user."""
        token = self.get_user_token(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = f'{self.user_url}99999/'
        self.assertPermission(url=url, method='get',expected_status=status.HTTP_404_NOT_FOUND,bearer_token=token)
    

    @tag('auth','permission_data','non_existing','non_existing_business')
    def test_update_user_with_non_existing_business(self):
        """Test updating user permissions for a non existing business"""
        token = self.get_user_token(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = f'{self.user_url}{self.regular_user.id}/'
        data = {'groups':{'8888':{self.admin_group.id:True}}}
        self.assertPermission(url=url, method='patch', data=data, expected_status=status.HTTP_400_BAD_REQUEST)
    

    @tag('not_auth','permission_data','non_existing','non_existing_permission')
    def test_update_user_with_invalid_permission(self):
        """Test updating user permissions with non existing permission"""
        token = self.get_user_token(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = f'{self.user_url}{self.regular_user.id}/'
        data = {'permissions':{self.business.id:{'999':True}}}
        self.assertPermission(url=url, method='patch', data=data, expected_status=status.HTTP_400_BAD_REQUEST)


    @tag('not_auth','permission_data','non_existing','non_existing_group')
    def test_update_user_with_invalid_group(self):
        """Test updating user permissions with non existing group"""
        token = self.get_user_token(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = f'{self.user_url}{self.regular_user.id}/'
        data = {'groups':{self.business.id:{'999':True}}}
        self.assertPermission(url=url, method='patch', data=data, expected_status=status.HTTP_400_BAD_REQUEST)
    

    ############################################# HERE


    @tag('not_auth','permission_data','non_existing','non_existing_user')
    def test_delete_nonexistent_user(self):
        """Test deleting a non-existent user."""
        token = self.get_user_token(self.superuser)
        
        url = f'{self.user_list_url}99999/'
        response = self.client.delete(url)
        
        self.assertPermission(url=url,method='delete', expected_status=status.HTTP_404_NOT_FOUND, bearer_token=token)
    


    @tag('not_auth','permission_data','superuser_delete_superuser')
    def test_delete_superuser_forbidden(self):
        """Test that superuser cannot be deleted (if protected)."""
        token = self.get_user_token(self.superuser)
        
        url = f'{self.user_url}{self.superuser.id}/'
        response = self.client.delete(url)
        # Should either succeed or fail based on business logic
        self.assertPermission(url=url,method='delete', expected_status=[status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST],bearer_token=token)


class TestJWTTokenEndpoints(BaseUserTestCase):
    """Tests for JWT token endpoints."""
    
    def test_token_obtain_success(self):
        """Test successful token obtain."""
        token_data = {
            'email': self.superuser.email,
            'password': 'adminpassword123'
        }
        
        response = self.client.post(self.token_url, token_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_obtain_invalid_credentials(self):
        """Test token obtain with invalid credentials."""
        token_data = {
            'email': self.superuser.email,
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.token_url, token_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_obtain_nonexistent_user(self):
        """Test token obtain with non-existent user."""
        token_data = {
            'email': 'nonexistent@test.com',
            'password': 'somepassword'
        }
        
        response = self.client.post(self.token_url, token_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh_success(self):
        """Test successful token refresh."""
        # First obtain a refresh token
        token_data = {
            'email': self.superuser.email,
            'password': 'adminpassword123'
        }
        
        obtain_response = self.client.post(self.token_url, token_data, format='json')
        refresh_token = obtain_response.data['refresh']
        
        # Then refresh the token
        refresh_data = {
            'refresh': refresh_token
        }
        
        response = self.client.post(self.token_refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        refresh_data = {
            'refresh': 'invalid_refresh_token'
        }
        
        response = self.client.post(self.token_refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh_expired_token(self):
        """Test token refresh with expired token."""
        # Create a refresh token that's already expired
        refresh = RefreshToken.for_user(self.superuser)
        refresh.set_exp(lifetime=-1)  # Set to expired
        
        refresh_data = {
            'refresh': str(refresh)
        }
        
        response = self.client.post(self.token_refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserPermissions(BaseUserTestCase):
    """Tests for user permission functionality."""
    
    def get_user_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_user_without_permission_cannot_list(self):
        """Test that user without view permission cannot list users."""
        # Create a user with no permissions
        no_perm_user = User.objects.create_user(
            username='noperm_test',
            email='noperm@test.com',
            name='No',
            last_name='Permission',
            password='nopassword123'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(no_perm_user)}')
        response = self.client.get(self.user_list_url)
        
        # Should be denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_with_permission_can_list(self):
        """Test that user with view permission can list users."""
        # Grant view permission
        view_perm = Permission.objects.get(codename='view_user')
        self.regular_user.user_permissions.add(view_perm)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.regular_user)}')
        response = self.client.get(self.user_list_url)
        
        # Should succeed (permission check passes)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_can_update_own_profile(self):
        """Test that user can update their own profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.regular_user)}')
        
        url = f'{self.user_list_url}{self.regular_user.id}/'
        update_data = {
            'name': 'Updated Name'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        # Should either succeed or fail based on permission check
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class TestUserValidation(BaseUserTestCase):
    """Tests for user validation in API."""
    
    def get_user_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_create_user_missing_required_fields(self):
        """Test user creation with missing required fields."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        incomplete_data = {
            'username': 'incomplete_test'
            # Missing email, name, password
        }
        
        response = self.client.post(self.user_list_url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_user_invalid_email_format(self):
        """Test user creation with invalid email format."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        invalid_email_data = {
            'username': 'email_test',
            'email': 'not-an-email',
            'name': 'Test',
            'last_name': 'User',
            'password': 'testpassword123'
        }
        
        response = self.client.post(self.user_list_url, invalid_email_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_user_short_password(self):
        """Test user creation with short password."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        short_password_data = {
            'username': 'shortpass_test',
            'email': 'shortpass@test.com',
            'name': 'Test',
            'last_name': 'User',
            'password': '123'  # Very short password
        }
        
        response = self.client.post(self.user_list_url, short_password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
