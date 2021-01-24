from django.test import TestCase
from django.urls import reverse
from faker import Faker
from django.contrib.auth.models import User

fake = Faker()


def generate_user_form_params():
    password = fake.password()
    return {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'username': fake.user_name(),
        'password1': password,
        'password2': password,
    }


class UserCreateViewTests(TestCase):
    def test_open_user_create_form(self):
        response = self.client.get(reverse('users:create'))

        self.assertContains(response, "Register")
        self.assertEqual(response.status_code, 200)

    def test_create_user_with_valid_attributes(self):
        attributes = generate_user_form_params()

        response = self.client.post(reverse('users:create'), attributes)

        user = User.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.username, attributes['username'])

    def test_create_user_with_invalid_attributes(self):
        attributes = {'username': fake.user_name()}

        response = self.client.post(reverse('users:create'), attributes)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)


class UserUpdateViewTests(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.user = User.objects.first()
        self.client.login(username=self.user.username, password='123')

    def test_open_user_update_form(self):
        url = reverse('users:update', kwargs={'pk': self.user.pk})

        response = self.client.get(url)

        self.assertContains(response, "Update")
        self.assertEqual(response.status_code, 200)

    def test_update_user_with_valid_attributes(self):
        url = reverse('users:update', kwargs={'pk': self.user.pk})
        attributes = generate_user_form_params()

        response = self.client.post(url, attributes)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.username, attributes['username'])
        self.assertEqual(User.objects.count(), 1)

    def test_update_user_with_invalid_attributes(self):
        url = reverse('users:update', kwargs={'pk': self.user.pk})
        attributes = {'username': fake.user_name()}

        response = self.client.post(url, attributes)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.username, attributes['username'])
        self.assertEqual(User.objects.count(), 1)

    def test_update_other_user(self):
        other_user = User.objects.create_user(
            username=fake.user_name(),
            password='123',
        )
        url = reverse('users:update', kwargs={'pk': other_user.pk})
        attributes = generate_user_form_params()

        response = self.client.post(url, attributes)

        other_user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(other_user.username, attributes['username'])
        self.assertEqual(User.objects.count(), 2)

    def test_update_user_when_logged_out(self):
        self.client.logout()
        url = reverse('users:update', kwargs={'pk': self.user.pk})
        attributes = generate_user_form_params()

        response = self.client.post(url, attributes)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.user.username, attributes['username'])
        self.assertEqual(User.objects.count(), 1)
