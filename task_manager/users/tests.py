from http import HTTPStatus
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


class UserIndexViewTests(TestCase):
    fixtures = ['users.json']

    def test_open_users_page(self):
        response = self.client.get(reverse('users:index'))

        self.assertContains(response, "test_username1")
        self.assertContains(response, "test_username2")
        self.assertEqual(response.status_code, HTTPStatus.OK)


class UserCreateViewTests(TestCase):
    def test_open_user_create_form(self):
        response = self.client.get(reverse('users:create'))

        self.assertContains(response, "Register")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_user_with_valid_attributes(self):
        attributes = generate_user_form_params()

        response = self.client.post(reverse('users:create'), attributes)

        user = User.objects.first()
        self.assertRedirects(response, '/login/')
        self.assertEqual(user.username, attributes['username'])

    def test_create_user_with_invalid_attributes(self):
        response = self.client.post(reverse('users:create'), {})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.count(), 0)


class UserUpdateViewTests(TestCase):
    fixtures = ['user.json']

    def setUp(self):
        self.user = User.objects.first()
        self.client.force_login(self.user)

    def test_open_user_update_form(self):
        url = reverse('users:update', kwargs={'pk': self.user.pk})

        response = self.client.get(url)

        self.assertContains(response, "User update")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_update_user_with_valid_attributes(self):
        url = reverse('users:update', kwargs={'pk': self.user.pk})
        attributes = generate_user_form_params()

        response = self.client.post(url, attributes)

        self.user.refresh_from_db()
        self.assertRedirects(response, '/users/')
        self.assertEqual(self.user.username, attributes['username'])

    def test_update_user_with_invalid_attributes(self):
        url = reverse('users:update', kwargs={'pk': self.user.pk})
        attributes = {'username': fake.user_name()}

        response = self.client.post(url, attributes)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(self.user.username, attributes['username'])

    def test_update_other_user(self):
        other_user = User.objects.create_user(
            username=fake.user_name(),
            password=fake.password(),
        )
        url = reverse('users:update', kwargs={'pk': other_user.pk})
        attributes = generate_user_form_params()

        response = self.client.post(url, attributes)

        other_user.refresh_from_db()
        self.assertRedirects(response, '/users/')
        self.assertNotEqual(other_user.username, attributes['username'])

    def test_update_user_when_logged_out(self):
        self.client.logout()
        pk = self.user.pk
        url = reverse('users:update', kwargs={'pk': pk})
        attributes = generate_user_form_params()

        response = self.client.post(url, attributes)

        self.user.refresh_from_db()
        self.assertRedirects(response, f'/login/?next=/users/{pk}/update/')
        self.assertNotEqual(self.user.username, attributes['username'])


class UserDeleteViewTests(TestCase):
    fixtures = ['user.json']

    def setUp(self):
        self.user = User.objects.first()
        self.client.force_login(self.user)

    def test_open_user_delete_form(self):
        url = reverse('users:delete', kwargs={'pk': self.user.pk})

        response = self.client.get(url)

        self.assertContains(response, "User deletion")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_delete_user(self):
        url = reverse('users:delete', kwargs={'pk': self.user.pk})

        response = self.client.post(url)

        self.assertRedirects(response, '/users/')
        self.assertEqual(User.objects.count(), 0)

    def test_delete_other_user(self):
        other_user = User.objects.create_user(
            username=fake.user_name(),
            password=fake.password(),
        )
        url = reverse('users:delete', kwargs={'pk': other_user.pk})

        response = self.client.post(url)

        self.assertRedirects(response, '/users/')
        self.assertEqual(User.objects.count(), 2)

    def test_delete_user_when_logged_out(self):
        self.client.logout()
        pk = self.user.pk
        url = reverse('users:delete', kwargs={'pk': pk})

        response = self.client.post(url)

        self.assertRedirects(response, f'/login/?next=/users/{pk}/delete/')
        self.assertEqual(User.objects.count(), 1)
