from django.test import TestCase, override_settings
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.utils.formats import date_format

from PIL import Image
from shutil import rmtree

from media_app.models import Media, MediaTags, MediaDownload, get_cover_upload, get_file_upload

User = get_user_model()

TEST_MEDIA_DIR_NAME = 'media_for_tests'

TEST_MEDIA_ROOT = settings.BASE_DIR.joinpath(TEST_MEDIA_DIR_NAME)
TEST_IMAGES_ROOT = settings.BASE_DIR.joinpath('images_for_tests')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CreateMediaTestCase(TestCase):

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

        cls.test_file = SimpleUploadedFile('test_file.pdf', b'file_content', content_type='application/pdf')

        TEST_IMAGES_ROOT.mkdir(parents=True, exist_ok=True)

        Image.new('RGB', (1, 1), color='blue').save('images_for_tests/test_image_good.png')

        cls.test_cover = SimpleUploadedFile(
            name='test_image_good.png',
            content=open('images_for_tests/test_image_good.png', 'rb').read(),
            content_type='image/jpeg',
        )

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

        cls.test_tag_ids = (test_tag_1.id, test_tag_2.id)

    def test_get(self):

        # without login:

        response = self.client.get(reverse('create_media'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

        # with login:

        self.client.force_login(self.user)

        response = self.client.get(reverse('create_media'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/create_media.html')

        self.client.logout()

    def test_post_without_login(self):

        response = self.client.post(reverse('create_media'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_post_incorrect_data(self):

        self.client.force_login(self.user)

        incorrect_post_data = {
            'title': 'test_too_big_title_dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'description': 'test_incorrect_data_description',
            'author': 'test_too_big_author_dataaaaaaaa',
            'tags': (0,),  # "0" database id
        }

        response = self.client.post(reverse('create_media'), incorrect_post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/create_media.html')

        self.assertFalse(Media.objects.filter(title=incorrect_post_data['title']))

        incorrect_form_errors = {
            'title': 'Ensure this value has at most 60 characters (it has 61).',
            'author': 'Ensure this value has at most 30 characters (it has 31).',
            'file': 'This field is required.',
            'tags': 'Select a valid choice. 0 is not one of the available choices.',
        }

        for field, error in incorrect_form_errors.items():
            self.assertFormError(response, 'form', field, error)

        self.client.logout()

    def test_post_correct_data(self):

        self.client.force_login(self.user)

        correct_post_data = {
            'title': 'test_title_data',
            'description': 'test_correct_data_description',
            'author': 'test_author_data',
            'file': self.test_file,
            'cover': self.test_cover,
            'tags': self.test_tag_ids,
        }

        response = self.client.post(reverse('create_media'), correct_post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/create_media_successful.html')

        self.assertEqual(1, Media.objects.filter(title=correct_post_data['title']).count())

        self.client.logout()

    def test_post_duplicate_data(self):

        self.client.force_login(self.user)

        duplicate_media_data = {
            'title': 'test_title',
            'description': 'test_description',
            'author': 'test_author',
            'user_who_added': self.user,
            'file': self.test_file,
        }

        Media.objects.create(**duplicate_media_data)

        response = self.client.post(reverse('create_media'), duplicate_media_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/create_media.html')

        self.assertEqual(1, Media.objects.filter(title=duplicate_media_data['title']).count())

        duplicate_form_errors = {
            'title': 'Not a unique title, change it.',
            'description': 'Not a unique description, change it.',
        }

        for field, error in duplicate_form_errors.items():
            self.assertFormError(response, 'form', field, error)

        self.client.logout()

    @classmethod
    def tearDownClass(cls):

        super().tearDownClass()

        rmtree(TEST_MEDIA_ROOT)
        rmtree(TEST_IMAGES_ROOT)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ViewMediaTestCase(TestCase):

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

        cls.test_file = SimpleUploadedFile('test_file.pdf', b'file_content', content_type='application/pdf')

        TEST_IMAGES_ROOT.mkdir(parents=True, exist_ok=True)

        Image.new('RGB', (1, 1), color='blue').save('images_for_tests/test_image_good.png')

        cls.test_cover = SimpleUploadedFile(
            name='test_image_good.png',
            content=open('images_for_tests/test_image_good.png', 'rb').read(),
            content_type='image/jpeg',
        )

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

        cls.test_tags = (test_tag_1, test_tag_2)

        cls.media_data = {
            'title': 'test_title',
            'description': 'test_description',
            'author': 'test_author',
            'user_who_added': cls.user,
            'file': cls.test_file,
            'active': 1,
            'cover': cls.test_cover,
        }
        cls.not_active_media_data = {
            'title': 'test_title 2',
            'description': 'test_description 2',
            'author': 'test_author',
            'user_who_added': cls.user,
            'file': cls.test_file,
            'active': 0,
            'cover': cls.test_cover,
        }

        cls.media = Media.objects.create(**cls.media_data)
        cls.not_active_media = Media.objects.create(**cls.not_active_media_data)

        cls.media.tags.set(cls.test_tags)
        cls.not_active_media.tags.set(cls.test_tags)

    def test_get_not_exist_media(self):

        response = self.client.get(reverse('view_media', kwargs={'media_id': 0}), follow=True)  # 0 id does not exist

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'errors/404.html')

    def test_get_inactive_media(self):

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.not_active_media.id}), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_get_active_media_without_login(self):

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.media.id}), follow=True)

        self.assertTemplateUsed(response, 'media_app/view_media.html')

        page_should_contain = list(self.media_data.values())

        # not required in this check:
        page_should_contain.remove(self.media_data['file'])
        page_should_contain.remove(self.media_data['cover'])
        page_should_contain.remove(self.media_data['active'])

        # add tags:
        for tag in self.media.tags.values():

            page_should_contain.append(tag['name_en_us'])
            page_should_contain.append(tag['help_text_en_us'])

        # add cover:
        page_should_contain.append(
            f'<img src="{settings.MEDIA_URL}{get_cover_upload(self.media, self.media_data["cover"].name)}"'
            f' class="float-right cover_image">'
        )

        # add pub date:
        page_should_contain.append(date_format(self.media.pub_date, 'DATE_FORMAT'))

        # add file downloads:
        page_should_contain.append(f'Downloads: {self.media.get_downloads_number()}')

        # check all in the list:
        for item in page_should_contain:
            self.assertContains(response, item)

    def test_get_active_media(self):

        self.client.force_login(self.user)

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.media.id}), follow=True)

        self.assertTemplateUsed(response, 'media_app/view_media.html')

        page_should_contain = list(self.media_data.values())

        # not required in this check:
        page_should_contain.remove(self.media_data['file'])
        page_should_contain.remove(self.media_data['cover'])
        page_should_contain.remove(self.media_data['active'])

        # add tags:
        for tag in self.media.tags.values():

            page_should_contain.append(tag['name_en_us'])
            page_should_contain.append(tag['help_text_en_us'])

        # add cover:
        page_should_contain.append(
            f'<img src="{settings.MEDIA_URL}{get_cover_upload(self.media, self.media_data["cover"].name)}"'
            f' class="float-right cover_image">'
        )

        # add pub date:
        page_should_contain.append(date_format(self.media.pub_date, 'DATE_FORMAT'))

        # check all in the list:
        for item in page_should_contain:
            self.assertContains(response, item)

        # check file download:
        response_content: str = response.content.decode('utf-8').replace('\n', '').replace(' ', '')

        downloads_number_tag: str = \
            f'<span class="small" id="downloads_number">{self.media.get_downloads_number()}</span>'.replace(' ', '')

        self.assertIn(downloads_number_tag, response_content)

        file_download_button_tag: str = \
            f'<a id="download_link" class="btn btn-primary"' \
            f' href="{settings.MEDIA_URL}{get_file_upload(self.media, self.media_data["file"].name)}"' \
            f' download>Download file'.replace(' ', '')

        self.assertIn(file_download_button_tag, response_content)

        self.client.logout()

    def test_post_download_file(self):

        # without login:

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'download_file'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'errors/403.html')

        # with login:

        self.client.force_login(self.user)

        user_download = MediaDownload.objects.filter(user_who_added=self.user, media=self.media)

        if user_download:
            user_download.delete()

        downloads_before_request: int = self.media.get_downloads_number()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'download_file'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        # check downloads number:

        self.media.refresh_from_db()

        self.assertEqual(downloads_before_request + 1, self.media.get_downloads_number())

        # check again, one download from one user:
        self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'download_file'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.media.refresh_from_db()

        self.assertEqual(downloads_before_request + 1, self.media.get_downloads_number())

        self.client.logout()

    @classmethod
    def tearDownClass(cls):

        super().tearDownClass()

        rmtree(TEST_MEDIA_ROOT)
        rmtree(TEST_IMAGES_ROOT)
