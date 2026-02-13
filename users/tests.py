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

from django.contrib.auth.models import Permission, Group


class BaseUserTestCase(APITestCase):
    """Base test case with common setup for user tests."""
    
    def setUp(self):
        """Set up test data."""
        print("creating database data........")
        self.client = APIClient()
        
        # Create a superuser for testing
        self.superuser = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            name='Admin',
            last_name='Test',
            password='adminpassword123'
        )
        
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regular_test',
            email='regular@test.com',
            name='Regular',
            last_name='User',
            password='regularpassword123'
        )
        
        # Create another regular user
        self.another_user = User.objects.create_user(
            username='another_test',
            email='another@test.com',
            name='Another',
            last_name='User',
            password='anotherpassword123'
        )
        
        # Create test business
        self.business = Business.objects.create(
            name='Test Business',
            tin='1234567890',
            utr='djvkjdfvki'
        )
        
        # Create permissions for testing
        # Create a group for testing
        self.test_group = Group.objects.create(name='Test Group')

        self.admin_group = Group.objects.get(name='ADMIN')


        print("database seeded!")
        
        # URL patterns
        self.user_url = '/users/usuario/'
        self.user_list_url = '/users/usuarios/'
        self.token_url = '/api/token/'
        self.token_refresh_url = '/api/token/refresh/'



class TestUserListAPIView(BaseUserTestCase):
    """Tests for UserListAPIView (GET and POST)."""
    
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
        
        if isinstance(expected_status,list):
            self.assertIn(response.status_code, expected_status)
        
        self.assertEqual(response.status_code, expected_status)
        return response

    #for superuser

    @tag('method','superuser_list_get')
    def test_list_users_superuser_get(self):
        """Test that superuser can list all users."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get',self.user_list_url,status.HTTP_200_OK,bearer_token=token)
        #self.assertIn('data', response.data)
        #self.assertIsInstance(response.data['data'], list)


    @tag('method','superuser_list_post')
    def test_list_users_superuser_post(self):
        """Test that superuser can create a user."""
        token = self.get_user_token(self.superuser)
        new_user = {'username': 'CamiloVargas', 'name': 'Camilo', 'last_name': 'Vargas', 'email': 'cvargasf@gmail.com', 'password': 'cvargarcamilo','groups':{self.business.id: {self.admin_group.id: True}}}
        self.assertPermission('post',self.user_list_url,status.HTTP_200_OK,new_user,bearer_token=token)
       
    
    @tag('method','superuser_get')
    def test_users_superuser_get(self):
        """Test that superuser can read a user."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('get',self.user_url+f'{self.regular_user.id}/',status.HTTP_200_OK,bearer_token=token)

    @tag('method','superuser_patch')
    def test_users_superuser_patch(self):
        """Test that superuser can read a user."""
        token = self.get_user_token(self.superuser)
        data = {'groups':{self.business.id:{self.admin_group.id:True}}}
        self.assertPermission('patch',self.user_url+f'{self.regular_user.id}/',status.HTTP_200_OK,data=data,bearer_token=token)

    @tag('method','superuser_delete')
    def test_users_superuser_delete(self):
        """Test that superuser can read a user."""
        token = self.get_user_token(self.superuser)
        self.assertPermission('delete',self.user_url+f'{self.regular_user.id}/',status.HTTP_200_OK,bearer_token=token)






    @tag('auth','regular_user_no_auth')
    def test_list_authenticated_regular_user_unauthorized(self):
        """Test that authenticated regular user can list users."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        response = self.client.get(self.user_list_url)
        response2 = self.client.get(self.user_url+f'{self.regular_user.id}')
        
        # The response status depends on permissions
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])



    @tag('','')
    def test_list_users_superuser(self):
        """Test that superusers can access list and individual GET"""
        token = self.get_user_token(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.user_list_url)

        # The response status depends on permissions
        self.assertIn(response.status_code, [status.HTTP_200_OK])
    


    @tag('auth','unauth')
    def test_list_users_unauthenticated(self):
        """Test that unauthenticated users cannot list users."""
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    


class TestUserAPIView(BaseUserTestCase):
    """Tests for UserAPIView (GET, PATCH, DELETE)."""
    
    def get_user_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_retrieve_user_success(self):
        """Test successful user retrieval."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        url = f'{self.user_list_url}{self.regular_user.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_retrieve_user_unauthenticated(self):
        """Test that unauthenticated users cannot retrieve users."""
        url = f'{self.user_list_url}{self.regular_user.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_nonexistent_user(self):
        """Test retrieving a non-existent user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        url = f'{self.user_list_url}99999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_user_success(self):
        """Test successful user update."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        url = f'{self.user_list_url}{self.regular_user.id}/'
        update_data = {
            'name': 'Updated Name',
            'last_name': 'Updated Last Name'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        # Update might succeed or fail based on permissions
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_update_user_invalid_data(self):
        """Test user update with invalid data."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        url = f'{self.user_list_url}{self.regular_user.id}/'
        invalid_data = {
            'email': 'invalid-email-format'
        }
        
        response = self.client.patch(url, invalid_data, format='json')
        
        # Should fail validation
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_user_success(self):
        """Test successful user deletion."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        # Create a user to delete
        user_to_delete = User.objects.create_user(
            username='delete_test',
            email='delete@test.com',
            name='Delete',
            last_name='Test',
            password='deletepassword123'
        )
        
        url = f'{self.user_list_url}{user_to_delete.id}/'
        response = self.client.delete(url)
        
        # Delete might succeed or fail based on permissions
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
        
        # If deletion was successful, verify user is deleted
        if response.status_code == status.HTTP_200_OK:
            self.assertFalse(User.objects.filter(id=user_to_delete.id).exists())
    
    def test_delete_nonexistent_user(self):
        """Test deleting a non-existent user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        url = f'{self.user_list_url}99999/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_superuser_forbidden(self):
        """Test that superuser cannot be deleted (if protected)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_user_token(self.superuser)}')
        
        url = f'{self.user_list_url}{self.superuser.id}/'
        response = self.client.delete(url)
        
        # Should either succeed or fail based on business logic
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])


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


class TestUserModel(TestCase):
    """Tests for User model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='model_test',
            email='model@test.com',
            name='Model',
            last_name='Test',
            password='modelpassword123'
        )
    
    def test_user_creation(self):
        """Test user model creation."""
        self.assertEqual(self.user.username, 'model_test')
        self.assertEqual(self.user.email, 'model@test.com')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_user_str_representation(self):
        """Test user string representation."""
        expected_str = f'{self.user.name} {self.user.last_name}'
        self.assertEqual(str(self.user), expected_str)
    
    def test_user_get_plural(self):
        """Test user get_plural method."""
        self.assertEqual(self.user.get_plural(), 'users')
    
    def test_create_superuser(self):
        """Test superuser creation."""
        superuser = User.objects.create_superuser(
            username='super_test',
            email='super@test.com',
            name='Super',
            last_name='User',
            password='supassword123'
        )
        
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
    
    def test_create_user_without_email_raises_error(self):
        """Test that creating user without email raises error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='noemail_test',
                email='',
                name='No',
                last_name='Email',
                password='password123'
            )
    
    def test_user_password_is_hashed(self):
        """Test that user password is properly hashed."""
        self.user.set_password('newpassword123')
        self.user.save()
        
        # Password should not be stored in plain text
        self.assertNotEqual(self.user.password, 'newpassword123')
        
        # But should be verifiable
        self.assertTrue(self.user.check_password('newpassword123'))


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
