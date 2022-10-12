from django.test import TestCase, override_settings
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from PIL import Image
from shutil import rmtree

from media_app.models import Media, MediaTags

User = get_user_model()

TEST_MEDIA_ROOT = settings.BASE_DIR.joinpath('media_for_tests')
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
            name='test tag 1',
            help_text='test tag 1 help text',
            user_who_added=cls.user,
        )

        test_tag_2 = MediaTags.objects.create(
            name='test tag 1',
            help_text='test tag 1 help text',
            user_who_added=cls.user,
        )

        cls.test_tags = (test_tag_1, test_tag_2)

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
            'tags': 'bad_tag_name'
        }

        response = self.client.post(reverse('create_media'), incorrect_post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/create_media.html')

        self.assertFalse(Media.objects.filter(title=incorrect_post_data['title']))

        incorrect_form_errors = {
            'title': 'Ensure this value has at most 60 characters (it has 61).',
            'author': 'Ensure this value has at most 30 characters (it has 31).',
            'file': 'This field is required.',
            'tags': 'Select a valid choice. bad_tag_name is not one of the available choices.',
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
            'tags': self.test_tags,
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
