from django.test import TestCase, override_settings
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core import signing, mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from django_registration.backends.activation.views import REGISTRATION_SALT

user_model = get_user_model()


def next_user_id():
    return user_model.objects.order_by('-id').first().id + 1


@override_settings(LANGUAGE_CODE='en-us')
class AccountsAppTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.client = Client()

        cls.user_credentials = {
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test_email_1@mail.com',
            'role': 1,
        }

        cls.user = user_model.objects.create_user(**cls.user_credentials)

    def get_reset_link_data(self):

        mails_before_request = len(mail.outbox)

        username = f"test_user_{next_user_id()}"
        user_password = 'test_password_2'
        user_email = f"test_email_{next_user_id()}@mail.com"

        user_credentials = {
            'username': username,
            'password': user_password,
            'email': user_email,
            'role': 1,
        }

        user = user_model.objects.create_user(**user_credentials)

        password_reset_post_data = {
            'email': user_credentials['email'],
        }

        response = self.client.post(reverse('password_reset'), password_reset_post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset_successful.html')

        self.assertEqual(mails_before_request + 1, len(mail.outbox))  # "+ 1" - because new email should be sent

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))

        return user, user_password, token, uidb64

    def test_profile(self):

        # without login:

        response = self.client.get(reverse('profile'), follow=True)

        self.assertEqual(response.status_code, 200)
        # login.html, because without login --> redirect to login.html
        self.assertTemplateUsed(response, 'accounts_app/login.html')

        # with login:

        self.client.force_login(self.user)

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/profile.html')

        self.client.logout()

    def test_login(self):

        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

        # correct login data:

        response = self.client.post(reverse('login'), self.user_credentials, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/profile.html')

        self.assertTrue(response.context['user'].is_authenticated)

        self.client.logout()

        # incorrect login data:

        response = self.client.post(reverse('login'), {'username': 'bad_username', 'password': 'bad_password'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_logout(self):

        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/logout_successful.html')
        self.assertFalse(response.context['user'].is_authenticated)

    def test_register_get(self):

        response = self.client.get(reverse('django_registration_register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_registration/registration_form.html')

    def test_register_post_incorrect_data(self):

        incorrect_sign_up_post_data = {
            'username': '',
            'password1': 'TeSt_pASSw00rd',
            'password2': 'TeSt_pASSw00rddddd',
            'email': 'bad_mail'
        }

        response = self.client.post(reverse('django_registration_register'), incorrect_sign_up_post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_registration/registration_form.html')

        self.assertFalse(user_model.objects.filter(username=incorrect_sign_up_post_data['username']))

        form_errors = {
            'username': 'This field is required.',
            'password2': 'The two password fields didn’t match.',
            # twice because django-registration uses two validators
            'email': ['Enter a valid email address.', 'Enter a valid email address.'],
        }

        for field, error in form_errors.items():
            self.assertFormError(response, 'form', field, error)

    def test_register_post_correct_data(self):

        # create account:

        correct_sign_up_post_data = {
            'username': 'test_username',
            'password1': 'TeSt_pASSw00rd',
            'password2': 'TeSt_pASSw00rd',
            'email': f'test_mail{next_user_id()}@gmail.com',
        }

        response = self.client.post(reverse('django_registration_register'), correct_sign_up_post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_registration/registration_complete.html')

        self.assertFalse(user_model.objects.filter(username=correct_sign_up_post_data['username'])[0].is_active)

        # activate account:

        activation_key = signing.dumps(obj=correct_sign_up_post_data['username'], salt=REGISTRATION_SALT)

        response = self.client.get(
            reverse('django_registration_activate', kwargs={'activation_key': activation_key}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_registration/activation_complete.html')

        self.assertTrue(user_model.objects.get(username=correct_sign_up_post_data['username']).is_active)
        
    def test_register_post_duplicate_data(self):

        # create first account:

        sign_up_post_data = {
            'username': 'test_username_2',
            'password1': 'TeSt_pASSw00rd',
            'password2': 'TeSt_pASSw00rd',
            'email': f'test_mail_{next_user_id()}@gmail.com',
        }

        self.client.post(reverse('django_registration_register'), sign_up_post_data, follow=True)

        # activate first account:

        activation_key = signing.dumps(obj=sign_up_post_data['username'], salt=REGISTRATION_SALT)

        self.client.get(
            reverse('django_registration_activate', kwargs={'activation_key': activation_key}),
            follow=True,
        )

        # create second account(duplicate):

        response = self.client.post(reverse('django_registration_register'), sign_up_post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_registration/registration_form.html')

        self.assertEqual(1, user_model.objects.filter(username=sign_up_post_data['username']).count())

        form_errors = {
            'username': 'A user with that username already exists.',
            'email': 'This email address is already in use. Please supply a different email address.',
        }

        for field, error in form_errors.items():
            self.assertFormError(response, 'form', field, error)

    def test_password_change_get(self):

        self.client.force_login(self.user)

        mails_before_request = len(mail.outbox)

        response = self.client.get(reverse('password_change'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_change.html')

        self.assertEqual(mails_before_request, len(mail.outbox))

        self.client.logout()

    def test_password_change_post_incorrect_data(self):

        user_credentials = {
            'username': 'test_user_2',
            'password': 'test_password_2',
            'email': f'test_email_{next_user_id()}@mail.com',
            'role': 1,
        }

        user = user_model.objects.create_user(**user_credentials)

        self.client.force_login(user)

        password_change_post_incorrect_data = {
            'old_password': 'incorrect_old_password',
            'new_password1': 'test_new_password',
            'new_password2': 'test_new_passworddddd',
        }

        response = self.client.post(reverse('password_change'), password_change_post_incorrect_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_change.html')

        user.refresh_from_db()

        self.assertFalse(user.check_password(password_change_post_incorrect_data['new_password2']))

        form_errors = {
            'old_password': 'Your old password was entered incorrectly. Please enter it again.',
            'new_password2': 'The two password fields didn’t match.',
        }

        for field, error in form_errors.items():
            self.assertFormError(response, 'form', field, error)

        self.client.logout()

    def test_password_change_post_correct_data(self):

        user_credentials = {
            'username': 'test_user_2',
            'password': 'test_password_2',
            'email': f'test_email_{next_user_id()}@mail.com',
            'role': 1,
        }

        user = user_model.objects.create_user(**user_credentials)

        self.client.force_login(user)

        password_change_post_correct_data = {
            'old_password': user_credentials['password'],
            'new_password1': 'test_new_password',
            'new_password2': 'test_new_password',
        }

        response = self.client.post(reverse('password_change'), password_change_post_correct_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_change_successful.html')

        user.refresh_from_db()

        self.assertTrue(user.check_password(password_change_post_correct_data['new_password2']))

        self.client.logout()

    def test_password_reset_form_get(self):

        mails_before_request = len(mail.outbox)

        response = self.client.get(reverse('password_reset'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset.html')

        self.assertEqual(mails_before_request, len(mail.outbox))

    def test_password_reset_form_post_incorrect_data(self):

        mails_before_request = len(mail.outbox)

        password_reset_incorrect_post_data = {'email': 'not_exist_user_mail@gmail.com'}

        response = self.client.post(reverse('password_reset'), password_reset_incorrect_post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset_successful.html')

        self.assertEqual(mails_before_request, len(mail.outbox))

    def test_password_reset_form_post_correct_data(self):

        mails_before_request = len(mail.outbox)

        password_reset_correct_post_data = {'email': self.user.email}

        response = self.client.post(reverse('password_reset'), password_reset_correct_post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset_successful.html')

        self.assertEqual(mails_before_request + 1, len(mail.outbox))

    def test_password_reset_confirm_get_incorrect_data(self):

        user, user_password, _, uidb64 = self.get_reset_link_data()  # "_" - because the user password is not needed

        response = self.client.get(
            reverse('custom_password_reset_confirm', kwargs={'token': 'bad-token', 'uidb64': uidb64}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset_confirm.html')

        self.assertContains(response, 'The password reset link was invalid, possibly because it has already been '
                                      'used. Please request a new password reset.')

        user.refresh_from_db()

        self.assertTrue(user.check_password(user_password))

    def test_password_reset_confirm_get_correct_data(self):

        user, user_password, token, uidb64 = self.get_reset_link_data()

        self.client.get(
            reverse('custom_password_reset_confirm', kwargs={'token': token, 'uidb64': uidb64}),
            follow=True,
        )
        response = self.client.get(
            # "set-password" - default django reset url token
            reverse('custom_password_reset_confirm', kwargs={'token': 'set-password', 'uidb64': uidb64}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset_confirm.html')

        self.assertNotContains(response, 'The password reset link was invalid, possibly because it has already been '
                                         'used. Please request a new password reset.')

        user.refresh_from_db()

        self.assertTrue(user.check_password(user_password))

    def test_password_reset_confirm_post_incorrect_data(self):

        active_users_before_get = user_model.objects.filter(is_active=True).count()

        uidb64 = urlsafe_base64_encode(force_bytes(1))  # 1 - random primary key

        response = self.client.get(
            reverse('custom_password_reset_confirm', kwargs={'token': 'bad_token', 'uidb64': uidb64})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset_confirm.html')

        self.assertEqual(active_users_before_get, user_model.objects.filter(is_active=True).count())

        self.assertContains(response, 'The password reset link was invalid, possibly because it has already been used. '
                                      'Please request a new password reset.')

    def test_password_reset_confirm_post_correct_data(self):

        user, _, token, uidb64 = self.get_reset_link_data()  # "_" - because the user password is not needed

        password_reset_confirm_post_data = {
            'new_password1': 'test_new_password',
            'new_password2': 'test_new_password',
        }

        self.client.get(
            reverse('custom_password_reset_confirm', kwargs={'token': token, 'uidb64': uidb64}),
            follow=True,
        )
        response = self.client.post(
            # "set-password" - default django reset url token
            reverse('custom_password_reset_confirm', kwargs={'token': 'set-password', 'uidb64': uidb64}),
            password_reset_confirm_post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset_complete.html')

        self.assertNotContains(response, 'The password reset link was invalid, possibly because it has already been '
                                         'used. Please request a new password reset.')

        user.refresh_from_db()

        self.assertTrue(user.check_password(password_reset_confirm_post_data['new_password1']))
