from django.test import TestCase, override_settings
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from datetime import datetime, timedelta
from ast import literal_eval
from shutil import rmtree

from media_app.models import Media
from staff_app.models import ModeratorTask


User = get_user_model()

TEST_MEDIA_DIR_NAME = 'media_for_tests'

TEST_MEDIA_ROOT = settings.BASE_DIR.joinpath(TEST_MEDIA_DIR_NAME)


class ModeratorPageTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.client = Client()

        visitor_user_credentials = {
            'username': 'test_user_visitor',
            'password': 'test_password',
            'email': 'test_email_1@mail.com',
            'role': 1,
        }
        moderator_user_credentials = {
            'username': 'test_user_moderator',
            'password': 'test_password',
            'email': 'test_email_2@mail.com',
            'role': 2,
        }

        cls.visitor_user = User.objects.create(**visitor_user_credentials)
        cls.moderator_user = User.objects.create(**moderator_user_credentials)

        not_active_media_now_date_data = {
            'title': 'not_active_media_now_date_title',
            'description': 'test_description_1',
            'author': 'test_author',
            'user_who_added': cls.visitor_user,
            'active': Media.INACTIVE,
        }
        not_active_media_yesterday_date_data = {
            'title': 'not_active_media_yesterday_date_title',
            'description': 'test_description_2',
            'author': 'test_author',
            'user_who_added': cls.visitor_user,
            'active': Media.INACTIVE,
        }
        active_media_data = {
            'title': 'active_media_title',
            'description': 'test_description_3',
            'author': 'test_author',
            'user_who_added': cls.visitor_user,
            'active': Media.ACTIVE,
        }
        not_valid_media_data = {
            'title': 'not_valid_media_title',
            'description': 'test_description_4',
            'author': 'test_author',
            'user_who_added': cls.visitor_user,
            'active': Media.NOT_VALID,
        }

        cls.active_media = Media.objects.create(**active_media_data)
        cls.not_valid_media = Media.objects.create(**not_valid_media_data)
        cls.not_active_media_now_date = Media.objects.create(**not_active_media_now_date_data)

        cls.not_active_media_yesterday_date = Media.objects.create(**not_active_media_yesterday_date_data)

        # Set yesterday date:
        cls.not_active_media_yesterday_date.pub_date = datetime.today() - timedelta(days=1)

        cls.not_active_media_yesterday_date.save()

    def test_get_without_login(self):

        moderator_page_reverse_kwargs = {'get_next_task': 'false', 'from_view_media_page': 'false'}

        response = self.client.get(reverse('moderator_page', kwargs=moderator_page_reverse_kwargs), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_get_with_visitor_login(self):

        self.client.force_login(self.visitor_user)

        moderator_page_reverse_kwargs = {'get_next_task': 'false', 'from_view_media_page': 'false'}

        response = self.client.get(reverse('moderator_page', kwargs=moderator_page_reverse_kwargs), follow=True)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    def test_get(self):

        self.client.force_login(self.moderator_user)

        moderator_page_reverse_kwargs = {'get_next_task': 'false', 'from_view_media_page': 'false'}

        response = self.client.get(reverse('moderator_page', kwargs=moderator_page_reverse_kwargs))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_app/moderator_page.html')

        self.client.logout()

    def test_get_moderator_task_exists(self):

        media = self.not_active_media_now_date

        ModeratorTask.objects.create(
            user_who_added=self.moderator_user,
            media=media,
        )

        self.client.force_login(self.moderator_user)

        moderator_page_reverse_kwargs = {'get_next_task': 'false', 'from_view_media_page': 'false'}

        response = self.client.get(reverse('moderator_page', kwargs=moderator_page_reverse_kwargs))

        self.assertTemplateUsed(response, 'staff_app/moderator_page.html')

        moderator_task_link_a_tag: str = \
            f'<a href="{reverse("view_media", kwargs={"media_id": media.id})}" class="h4 font-italic">{media.title}</a>'
        moderator_task_link_section_tag: str = \
            f'<section id="moderator_task_link">{moderator_task_link_a_tag}</section>'

        self.assertContains(response, moderator_task_link_section_tag)

        self.client.logout()

    def test_get_moderator_task_not_exists(self):

        self.client.force_login(self.moderator_user)

        moderator_page_reverse_kwargs = {'get_next_task': 'false', 'from_view_media_page': 'false'}

        response = self.client.get(reverse('moderator_page', kwargs=moderator_page_reverse_kwargs))

        self.assertTemplateUsed(response, 'staff_app/moderator_page.html')

        get_new_moderator_task_button_tag: str = \
            f'<button type="submit" class="btn btn-primary mt-1" id="receive_task_button">Receive task</button>'

        self.assertContains(response, get_new_moderator_task_button_tag)

        self.client.logout()

    def test_post_without_login(self):

        response = self.client.post(
            reverse('moderator_page', kwargs={'get_next_task': 'false', 'from_view_media_page': 'false'}),
            follow=True,
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_post_with_visitor_login(self):

        self.client.force_login(self.visitor_user)

        response = self.client.post(
            reverse('moderator_page', kwargs={'get_next_task': 'false', 'from_view_media_page': 'false'}),
            follow=True,
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    @staticmethod
    def _change_media_pub_dates_to_earlier(func):

        def wrapper(*args):

            self = args[0]

            self.active_media.pub_date = self.active_media.pub_date - timedelta(days=2)
            self.not_valid_media.pub_date = self.not_valid_media.pub_date - timedelta(days=2)

            self.active_media.save()
            self.not_valid_media.save()

            func(*args)

            self.active_media.pub_date = self.active_media.pub_date + timedelta(days=2)
            self.not_valid_media.pub_date = self.not_valid_media.pub_date + timedelta(days=2)

            self.active_media.save()
            self.not_valid_media.save()

        return wrapper

    @_change_media_pub_dates_to_earlier
    def test_post_with_exist_not_active_media(self):

        self.client.force_login(self.moderator_user)

        response = self.client.post(
            reverse('moderator_page', kwargs={'get_next_task': 'false', 'from_view_media_page': 'false'}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)

        media = self.not_active_media_yesterday_date

        moderator_task_link_a_tag: str = \
            f'<a href="{reverse("view_media", kwargs={"media_id": media.id})}" class="h4 font-italic">{media.title}</a>'

        self.assertEqual(literal_eval(response.content.decode('utf-8'))['moderator_task'], moderator_task_link_a_tag)

        self.client.logout()

    @staticmethod
    def _change_media_actives_to_not_valid(func):

        def wrapper(*args):

            self = args[0]

            self.not_active_media_now_date.active = Media.NOT_VALID
            self.not_active_media_yesterday_date.active = Media.NOT_VALID

            self.not_active_media_now_date.save()
            self.not_active_media_yesterday_date.save()

            func(*args)

            self.not_active_media_now_date.active = Media.INACTIVE
            self.not_active_media_yesterday_date.active = Media.INACTIVE

            self.not_active_media_now_date.save()
            self.not_active_media_yesterday_date.save()

        return wrapper

    @_change_media_actives_to_not_valid
    def test_post_without_exist_not_active_media(self):

        self.client.force_login(self.moderator_user)

        response = self.client.post(
            reverse('moderator_page', kwargs={'get_next_task': 'false', 'from_view_media_page': 'false'}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.content.decode('utf-8'), '{"moderator_task": null}')

        self.client.logout()

    def test_get_redirect_to_moderator_page_without_login(self):

        response = self.client.get(reverse('redirect_to_moderator_page'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_get_redirect_to_moderator_page_with_visitor_login(self):

        self.client.force_login(self.visitor_user)

        response = self.client.get(reverse('redirect_to_moderator_page'), follow=True)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    def test_get_redirect_to_moderator_page(self):

        self.client.force_login(self.moderator_user)

        response = self.client.get(reverse('redirect_to_moderator_page'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_app/moderator_page.html')

        self.client.logout()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ViewMediaPageModeratorContentTestCase(TestCase):

    def setUp(self):

        self.client = Client()

        visitor_user_credentials = {
            'username': 'test_user_visitor',
            'password': 'test_password',
            'email': 'test_email_1@mail.com',
            'role': 1,
        }
        moderator_user_credentials = {
            'username': 'test_user_moderator',
            'password': 'test_password',
            'email': 'test_email_2@mail.com',
            'role': 2,
        }

        self.visitor_user = User.objects.create(**visitor_user_credentials)
        self.moderator_user = User.objects.create(**moderator_user_credentials)

        test_file = SimpleUploadedFile('test_file.pdf', b'file_content', content_type='application/pdf')

        not_active_media_now_date_data = {
            'title': 'not_active_media_now_date_title',
            'description': 'test_description_1',
            'author': 'test_author',
            'user_who_added': self.visitor_user,
            'active': 0,
        }
        not_active_media_yesterday_date_data = {
            'title': 'not_active_media_yesterday_date_title',
            'description': 'test_description_3',
            'author': 'test_author',
            'user_who_added': self.visitor_user,
            'file': test_file,
            'active': 0,
        }

        # not for moderator task
        self.not_active_media_now_date = Media.objects.create(**not_active_media_now_date_data)

        not_active_media_yesterday_date = Media.objects.create(**not_active_media_yesterday_date_data)

        # Set yesterday date:
        not_active_media_yesterday_date.pub_date = datetime.today() - timedelta(days=1)

        not_active_media_yesterday_date.save()

        self.moderator_task = \
            ModeratorTask.objects.create(user_who_added=self.moderator_user, media=not_active_media_yesterday_date)

    def test_get_with_visitor_login(self):

        self.client.force_login(self.visitor_user)

        response = \
            self.client.get(reverse('view_media', kwargs={'media_id': self.moderator_task.media.id}), follow=True)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    def test_get_moderator_user_without_task(self):

        self.client.force_login(self.moderator_user)

        response = \
            self.client.get(reverse('view_media', kwargs={'media_id': self.not_active_media_now_date.id}), follow=True)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    def test_get_moderator_user(self):

        self.client.force_login(self.moderator_user)

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.moderator_task.media.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/view_media.html')

        moderator_content = (
            '<section class="border border-danger mt-5 d-inline-block pt-1 pb-1 pr-2 pl-2">',
            '<form method="post">',
            '<section class="form-check">',
            '<button class="btn btn-outline-primary m-2" name="approve_button" id="approve_button">Confirm</button>',
        )

        for content in moderator_content:
            self.assertContains(response, content)

        self.client.logout()

    def test_post_incorrect_data(self):

        self.client.force_login(self.moderator_user)

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.moderator_task.media.id}),
            data={},
            follow=True,
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')

        self.client.logout()

    def test_post_approve_radio_buttons_false_value(self):

        self.client.force_login(self.moderator_user)

        post_data = {
            'is_approve_radio': 'disapprove',
            'is_auto_next_task': 'false',
            'approve_button': '',  # this is needed because this is sending the form
        }

        moderator_task_media = self.moderator_task.media

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': moderator_task_media.id}),
            data=post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_app/moderator_page.html')

        moderator_task_media.refresh_from_db()

        self.assertEqual(Media.NOT_VALID, moderator_task_media.active)

        self.client.logout()

    def test_post_approve_radio_buttons_true_value(self):

        self.client.force_login(self.moderator_user)

        post_data = {
            'is_approve_radio': 'approve',
            'is_auto_next_task': 'false',
            'approve_button': '',  # this is needed because this is sending the form
        }

        moderator_task_media = self.moderator_task.media

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': moderator_task_media.id}),
            data=post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_app/moderator_page.html')

        moderator_task_media.refresh_from_db()

        self.assertEqual(Media.ACTIVE, moderator_task_media.active)

        self.client.logout()

    def test_post_is_auto_next_task_radio_buttons_false_value(self):

        user = self.moderator_user

        self.client.force_login(user)

        post_data = {
            'is_approve_radio': 'approve',
            'is_auto_next_task': 'false',
            'approve_button': '',  # this is needed because this is sending the form
        }

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.moderator_task.media.id}),
            data=post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_app/moderator_page.html')

        self.assertFalse(ModeratorTask.objects.filter(user_who_added=user))

        self.client.logout()

    def test_post_is_auto_next_task_radio_buttons_true_value(self):

        user = self.moderator_user

        self.client.force_login(user)

        post_data = {
            'is_approve_radio': 'approve',
            'is_auto_next_task': 'true',
            'approve_button': '',  # this is needed because this is sending the form
        }

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.moderator_task.media.id}),
            data=post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_app/moderator_page.html')

        self.assertTrue(ModeratorTask.objects.filter(user_who_added=user))

        self.client.logout()

    @classmethod
    def tearDownClass(cls):

        super().tearDownClass()

        rmtree(TEST_MEDIA_ROOT)
