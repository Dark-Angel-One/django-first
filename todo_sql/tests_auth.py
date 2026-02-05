from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')

    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_view_post_success(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='newuser').pk)

    def test_register_view_post_email_duplicate(self):
        User.objects.create_user(username='old', email='dup@example.com', password='p')
        data = {
            'username': 'newuser2',
            'email': 'dup@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'], ["Этот email уже используется."])

    def test_login_flow(self):
        user = User.objects.create_user(username='loginuser', password='StrongPass123!')
        data = {
            'username': 'loginuser',
            'password': 'StrongPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
