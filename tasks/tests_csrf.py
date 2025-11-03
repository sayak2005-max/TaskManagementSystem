from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser
from django.contrib.auth.models import Group


class RegisterCsrfTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_contains_csrf(self):
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # The template should render a csrf token hidden input
        self.assertIn('csrfmiddlewaretoken', content)

    def test_register_post_creates_user(self):
        # Ensure the Teacher group exists so registration can assign it
        Group.objects.get_or_create(name='Teacher')

        url = reverse('register')
        data = {
            'username': 'testteacher',
            'first_name': 'Test',
            'last_name': 'Teacher',
            'email': 'testteacher@example.com',
            'role': 'Teacher',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }

        # First GET to load CSRF cookie
        get_resp = self.client.get(url)
        self.assertEqual(get_resp.status_code, 200)

        post_resp = self.client.post(url, data, follow=True)
        # Expect redirect to login (or final success), not 403
        self.assertNotEqual(post_resp.status_code, 403, msg="CSRF still failing")

        # Check user created
        user_exists = CustomUser.objects.filter(username='testteacher').exists()
        self.assertTrue(user_exists, msg="User was not created by register POST")
        # Check group assignment
        user = CustomUser.objects.get(username='testteacher')
        self.assertTrue(user.groups.filter(name='Teacher').exists(), msg='New user not assigned to Teacher group')
