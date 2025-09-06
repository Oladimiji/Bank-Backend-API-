from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User

class UserTestCase(TestCase):
    def test_user_creation(self):
        """Test that a user can be created successfully."""
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)