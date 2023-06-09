from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core import signing, mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.files.uploadedfile import SimpleUploadedFile

from typing import Generator
from ast import literal_eval

from django_registration.backends.activation.views import REGISTRATION_SALT

from media_app.models import Media, MediaTags, MediaDownload, MediaRating

User = get_user_model()


def get_next_user_id_generator() -> Generator[int, None, None]:

    base_new_user_id = User.objects.order_by('-id').first().id

    while True:
        yield base_new_user_id + 1


next_user_id_generator = get_next_user_id_generator()


class CommonTestCase(TestCase):

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

        cls.user = User.objects.create_user(**cls.user_credentials)

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


class ProfileTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.client = Client()

        user_credentials = {
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test_email_1@mail.com',
            'role': 1,
        }
        second_user_credentials = {
            'username': 'test_user_2',
            'password': 'test_password',
            'email': 'test_email_2@mail.com',
            'role': 1,
        }

        cls.user = User.objects.create_user(**user_credentials)
        cls.second_user = User.objects.create_user(**second_user_credentials)

        test_file = SimpleUploadedFile('test_file.pdf', b'file_content', content_type='application/pdf')

        test_tag_1 = MediaTags.objects.create(
            name_en_us='test tag 1',
            help_text_en_us='test tag 1 help text',
            name_ru='test tag 1 ru',
            help_text_ru='test tag 1 help text ru',
            user_who_added=cls.user,
        )
        test_tag_2 = MediaTags.objects.create(
            name_en_us='test tag 2',
            help_text_en_us='test tag 2 help text',
            name_ru='test tag 2 ru',
            help_text_ru='test tag 2 help text ru',
            user_who_added=cls.user,
        )

        test_tags = (test_tag_1, test_tag_2)

        cls.media_data = {
            'title': 'test_title',
            'description': 'test_description',
            'author': 'test_author',
            'user_who_added': cls.user,
            'file': test_file,
            'active': 1,
        }
        cls.not_active_media_data = {
            'title': 'test_title 2',
            'description': 'test_description 2',
            'author': 'test_author',
            'user_who_added': cls.user,
            'file': test_file,
            'active': 0,
        }
        cls.second_user_media_data = {
            'title': 'test_title 3',
            'description': 'test_description 3',
            'author': 'test_author',
            'user_who_added': cls.second_user,
            'file': test_file,
            'active': 1,
        }

        cls.media = Media.objects.create(**cls.media_data)
        cls.not_active_media = Media.objects.create(**cls.not_active_media_data)
        cls.second_user_media = Media.objects.create(**cls.second_user_media_data)

        cls.media.tags.set(test_tags)
        cls.not_active_media.tags.set(test_tags)
        cls.second_user_media.tags.set(test_tags)

        cls.media_download_data = {
            'media': cls.media,
            'user_who_added': cls.user,
            'download': MediaDownload.DOWNLOADED,
        }
        cls.second_user_media_download_by_user_data = {
            'media': cls.second_user_media,
            'user_who_added': cls.user,
            'download': MediaDownload.DOWNLOADED,
        }
        cls.media_download_by_second_user_data = {
            'media': cls.media,
            'user_who_added': cls.second_user,
            'download': MediaDownload.DOWNLOADED,
        }

    def test_get_without_login(self):

        response = self.client.get(reverse('profile'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_get_media_added_by_user(self):

        self.client.force_login(self.user)

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/profile.html')

        page_should_contain = [
            self.media_data['title'],
            self.not_active_media_data['title'],
            f"{dict(Media.active_choices)[self.media_data['active']]}",
            f"{dict(Media.active_choices)[self.not_active_media_data['active']]}",
            # link to the update media page
            f"{reverse('update_media', kwargs={'media_id': self.media.id})}",
        ]

        page_should_not_contain = [
            self.second_user_media_data['title'],
            # link to the update media page
            f"{reverse('update_media', kwargs={'media_id': self.not_active_media.id})}",
            f"{reverse('update_media', kwargs={'media_id': self.second_user_media.id})}",
        ]

        for value in page_should_contain:
            self.assertContains(response, value)

        for value in page_should_not_contain:
            self.assertNotContains(response, value)

        self.client.logout()

    def test_get_user_downloads(self):

        self.client.force_login(self.user)

        media_download = MediaDownload.objects.create(**self.media_download_data)
        second_user_media_download_by_user = \
            MediaDownload.objects.create(**self.second_user_media_download_by_user_data)
        media_download_by_second_user = MediaDownload.objects.create(**self.media_download_by_second_user_data)

        self.media.user_who_added = self.second_user
        self.media.save()
        self.not_active_media.user_who_added = self.second_user
        self.not_active_media.save()

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/profile.html')

        page_should_contain = [
            self.media_data['title'],
            self.second_user_media_data['title'],
            # link to the view media page
            f"{reverse('view_media', kwargs={'media_id': self.media.id})}",
            f"{reverse('view_media', kwargs={'media_id': self.second_user_media.id})}",
        ]

        page_should_not_contain = [
            self.not_active_media_data['title'],
            # link to the view media page
            f"{reverse('view_media', kwargs={'media_id': self.not_active_media.id})}",
        ]

        for value in page_should_contain:
            self.assertContains(response, value)

        for value in page_should_not_contain:
            self.assertNotContains(response, value)

        self.media.user_who_added = self.media_data['user_who_added']
        self.media.save()
        self.not_active_media.user_who_added = self.not_active_media_data['user_who_added']
        self.not_active_media.save()

        media_download.delete()
        second_user_media_download_by_user.delete()
        media_download_by_second_user.delete()

        self.client.logout()

    def test_post_without_login(self):

        response = self.client.post(
            reverse('profile'),
            {
                'request_type': 'update_media_rating',
                'media_id': f'{self.media.id}',
                'new_rating': '4',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_post_not_exist_media(self):

        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile'),
            {
                'request_type': 'update_media_rating',
                'media_id': '0',  # 0 - not exist media id
                'new_rating': '4',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
            follow=True,
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed('errors/404.html')

        self.client.logout()

    def test_post_not_active_media(self):

        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile'),
            {
                'request_type': 'update_media_rating',
                'media_id': f'{self.not_active_media.id}',
                'new_rating': '4',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
            follow=True,
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed('errors/404.html')

        self.client.logout()

    def test_post_rating_bad_choice(self):

        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile'),
            {
                'request_type': 'update_media_rating',
                'media_id': f'{self.media.id}',
                'new_rating': '0',  # valid choices are: 1, 2, 3, 4, 5
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        self.assertFalse(literal_eval(response.content.decode('utf-8'))['result_rating'])

        response = self.client.post(
            reverse('profile'),
            {
                'request_type': 'update_media_rating',
                'media_id': f'{self.media.id}',
                'new_rating': '6',  # valid choices are: 1, 2, 3, 4, 5
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        self.assertFalse(literal_eval(response.content.decode('utf-8'))['result_rating'])

        self.client.logout()

    def test_post(self):

        self.client.force_login(self.user)

        post_data = {
            'request_type': 'update_media_rating',
            'media_id': f'{self.media.id}',
            'new_rating': '4',
        }

        response = self.client.post(reverse('profile'), post_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        self.assertEqual(literal_eval(response.content.decode('utf-8'))['result_rating'], int(post_data['new_rating']))

        self.assertEqual(
            MediaRating.objects.filter(
                media=self.media, user_who_added=self.user, rating=int(post_data['new_rating'])
            ).count(),
            1,  # 1 object at database
        )

        # check for duplicates and database object update

        self.client.post(reverse('profile'), post_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        new_new_rating_value = '3'

        post_data['new_rating'] = new_new_rating_value

        self.client.post(reverse('profile'), post_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        self.assertEqual(
            MediaRating.objects.filter(
                media=self.media, user_who_added=self.user, rating=int(new_new_rating_value)
            ).count(),
            1,  # 1 object at database
        )

        self.assertEqual(
            MediaRating.objects.filter(media=self.media, user_who_added=self.user).count(),
            1,  # 1 object at database
        )

        MediaRating.objects.filter(media=self.media, user_who_added=self.user).delete()

        self.client.logout()


class RegisterTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.client = Client()

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

        self.assertFalse(User.objects.filter(username=incorrect_sign_up_post_data['username']))

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
            'email': f'test_mail{next(next_user_id_generator)}@gmail.com',
        }

        response = self.client.post(reverse('django_registration_register'), correct_sign_up_post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_registration/registration_complete.html')

        self.assertFalse(User.objects.filter(username=correct_sign_up_post_data['username'])[0].is_active)

        # activate account:

        activation_key = signing.dumps(obj=correct_sign_up_post_data['username'], salt=REGISTRATION_SALT)

        response = self.client.get(
            reverse('django_registration_activate', kwargs={'activation_key': activation_key}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_registration/activation_complete.html')

        self.assertTrue(User.objects.get(username=correct_sign_up_post_data['username']).is_active)
        
    def test_register_post_duplicate_data(self):

        # create first account:

        sign_up_post_data = {
            'username': 'test_username_2',
            'password1': 'TeSt_pASSw00rd',
            'password2': 'TeSt_pASSw00rd',
            'email': f'test_mail_{next(next_user_id_generator)}@gmail.com',
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

        self.assertEqual(1, User.objects.filter(username=sign_up_post_data['username']).count())

        form_errors = {
            'username': 'A user with that username already exists.',
            'email': 'This email address is already in use. Please supply a different email address.',
        }

        for field, error in form_errors.items():
            self.assertFormError(response, 'form', field, error)


class PasswordChangeTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.client = Client()

        user_credentials = {
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test_email_1@mail.com',
            'role': 1,
        }

        cls.user = User.objects.create_user(**user_credentials)

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
            'email': f'test_email_{next(next_user_id_generator)}@mail.com',
            'role': 1,
        }

        user = User.objects.create_user(**user_credentials)

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
            'email': f'test_email_{next(next_user_id_generator)}@mail.com',
            'role': 1,
        }

        user = User.objects.create_user(**user_credentials)

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


class PasswordResetTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.client = Client()

        user_credentials = {
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test_email_1@mail.com',
            'role': 1,
        }

        cls.user = User.objects.create_user(**user_credentials)

    def get_reset_link_data(self):

        mails_before_request = len(mail.outbox)

        username = f"test_user_{next(next_user_id_generator)}"
        user_password = 'test_password_2'
        user_email = f"test_email_{next(next_user_id_generator)}@mail.com"

        user_credentials = {
            'username': username,
            'password': user_password,
            'email': user_email,
            'role': 1,
        }

        user = User.objects.create_user(**user_credentials)

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

        active_users_before_get = User.objects.filter(is_active=True).count()

        uidb64 = urlsafe_base64_encode(force_bytes(1))  # 1 - random primary key

        response = self.client.get(
            reverse('custom_password_reset_confirm', kwargs={'token': 'bad_token', 'uidb64': uidb64})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/password_reset_confirm.html')

        self.assertEqual(active_users_before_get, User.objects.filter(is_active=True).count())

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
