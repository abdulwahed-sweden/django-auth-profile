from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import Profile, phone_validator
from .forms import RegisterForm, ProfileForm, UserUpdateForm


class ProfileSignalTests(TestCase):
    """Test that a Profile is auto-created when a User is created."""

    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profile_str(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        self.assertEqual(str(user.profile), "testuser's profile")


class ProfileModelTests(TestCase):
    """Test Profile model methods and properties."""

    def test_avatar_initial_from_first_name(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        user.first_name = 'Alice'
        user.save()
        self.assertEqual(user.profile.avatar_initial, 'A')

    def test_avatar_initial_from_username(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        self.assertEqual(user.profile.avatar_initial, 'T')


class RegisterFormTests(TestCase):
    """Test the registration form."""

    def test_valid_registration(self):
        form = RegisterForm(data={
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertTrue(form.is_valid())

    def test_duplicate_email_rejected(self):
        User.objects.create_user('existing', 'taken@example.com', 'TestPass123!')
        form = RegisterForm(data={
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'taken@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class UserUpdateFormTests(TestCase):
    """Test the user update form."""

    def test_own_email_allowed(self):
        user = User.objects.create_user('testuser', 'me@example.com', 'TestPass123!')
        form = UserUpdateForm(
            data={'first_name': 'Test', 'last_name': 'User', 'email': 'me@example.com'},
            instance=user,
        )
        self.assertTrue(form.is_valid())

    def test_duplicate_email_rejected(self):
        User.objects.create_user('other', 'taken@example.com', 'TestPass123!')
        user = User.objects.create_user('testuser', 'me@example.com', 'TestPass123!')
        form = UserUpdateForm(
            data={'first_name': 'Test', 'last_name': 'User', 'email': 'taken@example.com'},
            instance=user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class AuthViewTests(TestCase):
    """Test authentication views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')

    def test_home_page_accessible(self):
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_accessible(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_accessible(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_accessible_when_logged_in(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)

    def test_register_creates_user(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class APIPermissionTests(TestCase):
    """Test API permissions."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user('user1', 'u1@example.com', 'TestPass123!')
        self.user2 = User.objects.create_user('user2', 'u2@example.com', 'TestPass123!')
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'AdminPass123!')

    def test_unauthenticated_access_denied(self):
        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_list_profiles(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_update_own_profile(self):
        self.client.force_authenticate(user=self.user1)
        profile = self.user1.profile
        response = self.client.patch(f'/api/profiles/{profile.id}/', {'bio': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_update_profile(self):
        self.client.force_authenticate(user=self.user2)
        profile = self.user1.profile
        response = self.client.patch(f'/api/profiles/{profile.id}/', {'bio': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_sees_email_in_user_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')
        data = response.json()
        self.assertIn('email', data['results'][0])

    def test_regular_user_no_email_in_user_list(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/users/')
        data = response.json()
        self.assertNotIn('email', data['results'][0])

    def test_api_pagination(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/profiles/')
        data = response.json()
        self.assertIn('results', data)
        self.assertIn('count', data)


class PhoneValidatorTests(TestCase):
    """Test the phone number validator."""

    def test_valid_phone_numbers(self):
        for number in ['+46701234567', '0701234567', '1234567']:
            phone_validator(number)  # should not raise

    def test_invalid_phone_numbers(self):
        for number in ['abc', '123', '+46-70-123', '']:
            if number:  # empty is handled by blank=True, not the validator
                with self.assertRaises(ValidationError):
                    phone_validator(number)


class ProfileFormTests(TestCase):
    """Test the profile form."""

    def test_valid_profile_form(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        form = ProfileForm(data={
            'bio': 'Hello world',
            'location': 'Stockholm',
            'phone': '+46701234567',
            'avatar_url': '',
        }, instance=user.profile)
        self.assertTrue(form.is_valid())

    def test_invalid_phone_rejected(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        form = ProfileForm(data={
            'bio': '',
            'location': '',
            'phone': 'not-a-phone',
            'avatar_url': '',
        }, instance=user.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_blank_fields_allowed(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        form = ProfileForm(data={
            'bio': '',
            'location': '',
            'phone': '',
            'avatar_url': '',
        }, instance=user.profile)
        self.assertTrue(form.is_valid())


class StaticPageViewTests(TestCase):
    """Test public static pages."""

    def test_about_page(self):
        response = self.client.get(reverse('accounts:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About')

    def test_help_page(self):
        response = self.client.get(reverse('accounts:help'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Help')

    def test_api_docs_page(self):
        response = self.client.get(reverse('accounts:api_docs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API')


class ProfileViewTests(TestCase):
    """Test profile edit view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        self.user.first_name = 'Test'
        self.user.last_name = 'User'
        self.user.save()
        self.client.login(username='testuser', password='TestPass123!')

    def test_profile_page_loads(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_update(self):
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'test@example.com',
            'bio': 'New bio',
            'location': 'Stockholm',
            'phone': '+46701234567',
            'avatar_url': '',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'New bio')


class PasswordViewTests(TestCase):
    """Test password change and reset views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')

    def test_password_change_requires_login(self):
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 302)

    def test_password_change_page_loads(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_page_loads(self):
        response = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_post(self):
        response = self.client.post(reverse('accounts:password_reset'), {
            'email': 'test@example.com',
        })
        self.assertEqual(response.status_code, 302)


class LogoutViewTests(TestCase):
    """Test logout."""

    def test_logout_redirects(self):
        self.client.login(
            username=User.objects.create_user('testuser', 'test@example.com', 'TestPass123!').username,
            password='TestPass123!',
        )
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)


class APICrudTests(TestCase):
    """Test full CRUD on profiles API."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123!')
        self.client.force_authenticate(user=self.user)
        self.profile = self.user.profile

    def test_retrieve_own_profile(self):
        response = self.client.get(f'/api/profiles/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_own_profile(self):
        response = self.client.put(f'/api/profiles/{self.profile.id}/', {
            'bio': 'Full update',
            'location': 'Malmö',
            'phone': '+46701234567',
            'avatar_url': '',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.location, 'Malmö')

    def test_partial_update_own_profile(self):
        response = self.client.patch(f'/api/profiles/{self.profile.id}/', {
            'location': 'Uppsala',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.location, 'Uppsala')

    def test_delete_own_profile(self):
        response = self.client.delete(f'/api/profiles/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Profile.objects.filter(id=self.profile.id).exists())

    def test_list_users(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_user(self):
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')


class APISearchTests(TestCase):
    """Test API search and ordering."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user('alice', 'alice@example.com', 'TestPass123!')
        self.user1.profile.location = 'Stockholm'
        self.user1.profile.bio = 'Developer'
        self.user1.profile.save()
        self.user2 = User.objects.create_user('bob', 'bob@example.com', 'TestPass123!')
        self.user2.profile.location = 'Gothenburg'
        self.user2.profile.bio = 'Designer'
        self.user2.profile.save()
        self.client.force_authenticate(user=self.user1)

    def test_search_by_location(self):
        response = self.client.get('/api/profiles/', {'search': 'Stockholm'})
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], 'alice')

    def test_search_by_username(self):
        response = self.client.get('/api/profiles/', {'search': 'bob'})
        self.assertEqual(response.data['count'], 1)

    def test_ordering(self):
        response = self.client.get('/api/profiles/', {'ordering': 'created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APISchemaTests(TestCase):
    """Test API documentation endpoints."""

    def test_schema_endpoint(self):
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)

    def test_swagger_ui(self):
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, 200)

    def test_redoc(self):
        response = self.client.get('/api/redoc/')
        self.assertEqual(response.status_code, 200)


class SeedCommandTests(TestCase):
    """Test the seed_users management command."""

    def test_seed_creates_users(self):
        out = StringIO()
        call_command('seed_users', stdout=out)
        self.assertTrue(User.objects.filter(username='admin').exists())
        self.assertTrue(User.objects.filter(username='erik.lindberg').exists())
        self.assertEqual(User.objects.count(), 6)

    def test_seed_is_idempotent(self):
        call_command('seed_users', stdout=StringIO())
        call_command('seed_users', stdout=StringIO())
        self.assertEqual(User.objects.filter(username='admin').count(), 1)
