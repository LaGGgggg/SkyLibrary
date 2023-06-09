from django.test import TestCase, override_settings
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime

from crispy_forms.utils import render_crispy_form

from PIL import Image
from shutil import rmtree
from ast import literal_eval
from os.path import isfile

from media_app.models import Media, MediaTags, MediaDownload, Comment, CommentRating, get_cover_upload,\
    get_file_upload, Report, ReportType
from media_app.forms import CreateReplyCommentForm, CreateReportCommentForm, CreateReportMediaForm

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
class UpdateMediaTestCase(TestCase):

    @staticmethod
    def _get_test_file(file_content: bytes = b'file_content') -> SimpleUploadedFile:
        return SimpleUploadedFile('test_file.pdf', file_content, content_type='application/pdf')

    @staticmethod
    def _get_test_cover(image_colorname: str = 'blue') -> SimpleUploadedFile:

        TEST_IMAGES_ROOT.mkdir(parents=True, exist_ok=True)

        cover_file_path = 'images_for_tests/test_image_good.png'

        if not isfile(cover_file_path):
            Image.new('RGB', (1, 1), color=image_colorname).save(cover_file_path)

        test_cover = SimpleUploadedFile(
            name='test_image_good.png',
            content=open(cover_file_path, 'rb').read(),
            content_type='image/jpeg',
        )

        return test_cover

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

        test_file = cls._get_test_file()
        test_cover = cls._get_test_cover()

        cls.test_tag_1 = MediaTags.objects.create(
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

        cls.test_tags = (cls.test_tag_1, test_tag_2)
        cls.test_tags_id_post_format = [f'{cls.test_tag_1.id}', f'{test_tag_2.id}']

        cls.media_data = {
            'title': 'test_title',
            'description': 'test_description',
            'author': 'test_author',
            'user_who_added': cls.user,
            'file': test_file,
            'active': 1,
            'cover': test_cover,
        }
        cls.not_active_media_data = {
            'title': 'test_title 2',
            'description': 'test_description 2',
            'author': 'test_author',
            'user_who_added': cls.user,
            'file': test_file,
            'active': 0,
            'cover': test_cover,
        }
        cls.second_user_media_data = {
            'title': 'test_title 3',
            'description': 'test_description 3',
            'author': 'test_author',
            'user_who_added': cls.second_user,
            'file': test_file,
            'active': 1,
            'cover': test_cover,
        }

        cls.media = Media.objects.create(**cls.media_data)
        cls.not_active_media = Media.objects.create(**cls.not_active_media_data)
        cls.second_user_media = Media.objects.create(**cls.second_user_media_data)

        cls.media.tags.set(cls.test_tags)
        cls.not_active_media.tags.set(cls.test_tags)
        cls.second_user_media.tags.set(cls.test_tags)

    def test_get_without_login(self):

        response = self.client.get(reverse('update_media', kwargs={'media_id': self.media.id}), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_get_not_exist_media(self):

        self.client.force_login(self.user)

        # 0 - object with this id cannot exist
        response = self.client.get(reverse('update_media', kwargs={'media_id': 0}))

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')

        self.client.logout()

    def test_get_not_active_media(self):

        self.client.force_login(self.user)

        response = self.client.get(reverse('update_media', kwargs={'media_id': self.not_active_media.id}))

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    def test_get_not_user_who_added(self):

        self.client.force_login(self.user)

        response = self.client.get(reverse('update_media', kwargs={'media_id': self.second_user_media.id}))

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    def test_get(self):

        self.client.force_login(self.user)

        response = self.client.get(reverse('update_media', kwargs={'media_id': self.media.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/update_media.html')

        self.client.logout()

    def test_post_without_login(self):

        post_data = self.media_data.copy()

        del post_data['user_who_added']
        del post_data['active']

        post_data['tags'] = self.test_tags_id_post_format
        post_data['file'] = self._get_test_file()
        post_data['cover'] = self._get_test_cover()

        response = \
            self.client.post(reverse('update_media', kwargs={'media_id': self.media.id}), post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts_app/login.html')

    def test_post_not_exist_media(self):

        self.client.force_login(self.user)

        post_data = self.media_data.copy()

        del post_data['user_who_added']
        del post_data['active']

        post_data['tags'] = self.test_tags_id_post_format
        post_data['file'] = self._get_test_file()
        post_data['cover'] = self._get_test_cover()

        # 0 - object with this id cannot exist
        response = self.client.post(reverse('update_media', kwargs={'media_id': 0}), post_data)

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')

        self.client.logout()

    def test_post_not_active_media(self):

        self.client.force_login(self.user)

        post_data = self.not_active_media_data.copy()

        del post_data['user_who_added']
        del post_data['active']

        post_data['tags'] = self.test_tags_id_post_format
        post_data['file'] = self._get_test_file()
        post_data['cover'] = self._get_test_cover()

        response = self.client.post(reverse('update_media', kwargs={'media_id': self.not_active_media.id}), post_data)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    def test_post_not_user_who_added(self):

        self.client.force_login(self.user)

        post_data = self.second_user_media_data.copy()

        del post_data['user_who_added']
        del post_data['active']

        post_data['tags'] = self.test_tags_id_post_format
        post_data['file'] = self._get_test_file()
        post_data['cover'] = self._get_test_cover()

        response = self.client.post(reverse('update_media', kwargs={'media_id': self.second_user_media.id}), post_data)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        self.client.logout()

    def test_post_incorrect_data(self):

        self.client.force_login(self.user)

        post_data = self.media_data.copy()

        del post_data['user_who_added']
        del post_data['active']

        post_data['title'] = self.second_user_media_data['title']
        post_data['description'] = self.second_user_media_data['description']
        post_data['author'] = ''

        bad_tags_post_data = 'bad_tags_post_data'

        post_data['tags'] = bad_tags_post_data

        response = self.client.post(reverse('update_media', kwargs={'media_id': self.media.id}), post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/update_media.html')

        form_errors = {
            'title': 'Not a unique title, change it.',
            'description': 'Not a unique description, change it.',
            'author': 'This field is required.',
            'tags': f'“{bad_tags_post_data}” is not a valid value.',
            'file': 'The submitted file is empty.',  # empty because the caret is at the end of the file
            'cover': 'The submitted file is empty.',  # empty because the caret is at the end of the file
        }

        for field, error in form_errors.items():
            self.assertFormError(response, 'form', field, error)

        self.client.logout()

    def test_post_no_changes(self):

        self.client.force_login(self.user)

        post_data = self.media_data.copy()

        del post_data['user_who_added']
        del post_data['active']

        post_data['tags'] = self.test_tags_id_post_format
        post_data['file'] = self._get_test_file()
        post_data['cover'] = self._get_test_cover()

        response = self.client.post(reverse('update_media', kwargs={'media_id': self.media.id}), post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/update_media_successful.html')

        self.media.refresh_from_db()

        self.assertEqual(self.media.active, Media.INACTIVE)

        self.assertEqual(self.media.title, post_data['title'])
        self.assertEqual(self.media.description, post_data['description'])
        self.assertEqual(self.media.author, post_data['author'])
        self.assertEqual([str(tag['id']) for tag in self.media.tags.values()], post_data['tags'])

        with self.media.file.open('rb') as media_file:
            with post_data['file'].open('rb') as post_data_file:
                self.assertEqual(media_file.read(), post_data_file.read())

        with self.media.cover.open('rb') as media_cover:
            with post_data['cover'].open('rb') as post_data_cover:
                self.assertEqual(media_cover.read(), post_data_cover.read())

        self.client.logout()

    def test_post(self):

        self.client.force_login(self.user)

        post_data = {
            'title': 'test_new_title',
            'description': 'test_new_description',
            'author': 'test_new_author',
            'tags': [str(self.test_tag_1.id)],
            'file': self._get_test_file(file_content=b'test_new_file_content'),
            'cover': self._get_test_cover(image_colorname='green'),
        }

        response = self.client.post(reverse('update_media', kwargs={'media_id': self.media.id}), post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/update_media_successful.html')

        self.media.refresh_from_db()

        self.assertEqual(self.media.active, Media.INACTIVE)

        self.assertEqual(self.media.title, post_data['title'])
        self.assertEqual(self.media.description, post_data['description'])
        self.assertEqual(self.media.author, post_data['author'])
        self.assertEqual([str(tag['id']) for tag in self.media.tags.values()], post_data['tags'])

        with self.media.file.open('rb') as media_file:
            with post_data['file'].open('rb') as post_data_file:
                self.assertEqual(media_file.read(), post_data_file.read())

        with self.media.cover.open('rb') as media_cover:
            with post_data['cover'].open('rb') as post_data_cover:
                self.assertEqual(media_cover.read(), post_data_cover.read())

        # revert post changes
        Media.objects.filter(id=self.media.id).update(
            title=self.media_data['title'],
            description=self.media_data['description'],
            author=self.media_data['author'],
            file=self._get_test_file(),
            cover=self._get_test_cover(),
        )

        self.media.tags.set(self.test_tags)

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
            'username': 'test_user_1',
            'password': 'test_password',
            'email': 'test_email_1@mail.com',
            'role': 1,
        }
        user_for_media_comment_credentials = {
            'username': 'test_user_2',
            'password': 'test_password',
            'email': 'test_email_2@mail.com',
            'role': 1,
        }
        user_for_media_comment_reply_credentials = {
            'username': 'test_user_3',
            'password': 'test_password',
            'email': 'test_email_3@mail.com',
            'role': 1,
        }
        user_for_comment_reply_reply_credentials = {
            'username': 'test_user_4',
            'password': 'test_password',
            'email': 'test_email_4@mail.com',
            'role': 1,
        }

        cls.user = User.objects.create_user(**user_credentials)
        user_for_media_comment = User.objects.create_user(**user_for_media_comment_credentials)
        user_for_media_comment_reply = User.objects.create_user(**user_for_media_comment_reply_credentials)
        user_for_comment_reply_reply = User.objects.create_user(**user_for_comment_reply_reply_credentials)

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

        cls.comment_data = {
            'content': 'media_comment_content_1',
            'target_type': Comment.MEDIA_TYPE,
            'target_id': cls.media.id,
            'user_who_added': user_for_media_comment,
        }

        cls.comment = Comment.objects.create(**cls.comment_data)

        cls.comment_reply_data = {
            'content': 'media_comment_content_2',
            'target_type': Comment.COMMENT_TYPE,
            'target_id': cls.comment.id,
            'user_who_added': user_for_media_comment_reply,
        }

        cls.comment_reply = Comment.objects.create(**cls.comment_reply_data)

        cls.comment_reply_reply_data = {
            'content': 'media_comment_content_3',
            'target_type': Comment.COMMENT_TYPE,
            'target_id': cls.comment_reply.id,
            'user_who_added': user_for_comment_reply_reply,
        }

        cls.comment_reply_reply = Comment.objects.create(**cls.comment_reply_reply_data)

        test_report_type_1 = ReportType.objects.create(
            name_en_us='test report type 1',
            name_ru='test report type 1 ru',
            user_who_added=cls.user,
        )
        test_report_type_2 = ReportType.objects.create(
            name_en_us='test report type 2',
            name_ru='test report type 2 ru',
            user_who_added=cls.user,
        )

        cls.test_report_types = (test_report_type_1, test_report_type_2)

    def test_get_not_exist_media(self):

        response = self.client.get(reverse('view_media', kwargs={'media_id': 0}), follow=True)  # 0 id does not exist

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')

    def test_get_inactive_media(self):

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.not_active_media.id}), follow=True)

        self.assertEqual(response.status_code, 403)
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
            f' class="float-end mb-5 me-5 cover_image">'
        )

        # add pub date:
        page_should_contain.append(naturalday(self.media.pub_date))

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
            f' class="float-end mb-5 me-5 cover_image">'
        )

        # add pub date:
        page_should_contain.append(naturalday(self.media.pub_date))

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

    def test_post_download_file_without_login(self):

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'download_file'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_download_file_with_login(self):

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

        self.assertEqual(downloads_before_request + 1, self.media.get_downloads_number())

        # check again, one download from one user:
        self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'download_file'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(downloads_before_request + 1, self.media.get_downloads_number())

        self.client.logout()

    def test_get_media_report_button_without_login(self):

        response = self.client.get(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'get_media_report_form'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_get_media_report_button_with_login(self):

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'get_media_report_form'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django/forms/widgets/input.html')  # response returns form

        page_should_contain: str = render_crispy_form(CreateReportMediaForm())

        page_content: str = literal_eval(response.content.decode('utf-8'))['media_report_form']

        self.assertEqual(page_content, page_should_contain)

        self.client.logout()

    def test_post_media_report_without_login(self):

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'media',
                'content': 'good content',
                'report_type': '1',
            },  # 1 - form field value
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_media_report_with_login(self):

        self.client.force_login(self.user)

        # removing the user report if it exists
        user_comment_report = Report.objects.filter(
            user_who_added=self.user, target_type=Report.MEDIA_TYPE, target_id=self.media.id
        )

        if user_comment_report.exists():
            user_comment_report.delete()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'media',
                'content': 'good content',
                'report_type': '1,2',
            },  # 1, 2 - form field values
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Report.objects.filter(
                user_who_added=self.user, target_type=Report.MEDIA_TYPE, target_id=self.media.id
            ).exists()
        )

        page_should_contain = {
            'report_success_message': 'Your report has been successfully created!',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_post_media_report_duplicate_data(self):

        self.client.force_login(self.user)

        duplicate_report_data = {
            'content': 'duplicate report content',
            'target_type': Report.MEDIA_TYPE,
            'target_id': self.media.id,
            'user_who_added': self.user,
        }

        Report.objects.create(**duplicate_report_data)

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'media',
                'content': duplicate_report_data['content'],
                'report_type': '1,2',
            },  # 1, 2 - form field values
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        user_media_reports = Report.objects.filter(
            user_who_added=self.user, target_type=Report.MEDIA_TYPE, target_id=self.media.id
        )

        self.assertEqual(1, user_media_reports.count())

        page_should_contain = {
            'messages': [{
                'level': 40,
                'message': 'You can not create one more report on the same media/comment',
                'tags': 'error',
            }],
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_get_media_with_comments_without_login(self):

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.media.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/view_media.html')

        page_should_contain = [
            self.comment_data['content'],
            self.comment_data['user_who_added'].username,
            naturaltime(self.comment.pub_date),
            self.comment.get_rating(),
        ]

        for item in page_should_contain:
            self.assertContains(response, item)

        page_should_not_contain = [
            f'data-form-adder-button-target-id="{self.comment.id}" data-requested-form-type="reply"',  # reply button
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment.id}"',  # upvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment.id}"',  # downvote button
        ]

        for item in page_should_not_contain:
            self.assertNotContains(response, item)

    def test_get_media_with_comments_with_login(self):

        self.client.force_login(self.user)

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.media.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/view_media.html')

        page_should_contain = [
            self.comment_data['content'],
            self.comment_data['user_who_added'].username,
            naturaltime(self.comment.pub_date),
            self.comment.get_rating(),
            f'data-form-adder-button-target-id="{self.comment.id}" data-requested-form-type="reply"',  # reply button
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment.id}"',  # upvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment.id}"',  # downvote button
        ]

        for item in page_should_contain:
            self.assertContains(response, item)

        self.client.logout()

    def test_post_add_media_comment_without_login(self):

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'create_comment', 'target_type': 'media', 'content': 'content'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_add_media_comment_with_login(self):

        self.client.force_login(self.user)

        added_comment_data = {
            'content': 'content',
            'user_who_added': self.user,
        }

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'create_comment', 'target_type': 'media', 'content': added_comment_data['content']},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        added_comment = Comment.objects.filter(content=added_comment_data['content'])

        self.assertTrue(added_comment.exists())

        added_comment = added_comment[0]

        page_should_contain = {
            'content': added_comment_data['content'],
            'user_who_added': added_comment_data['user_who_added'].username,
            'pub_date': naturaltime(added_comment.pub_date),
            'target_type': Comment.MEDIA_TYPE,
            'target_id': self.media.id,
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))['comment']

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        added_comment.delete()

        self.client.logout()

    def test_post_media_comment_upvote_button_without_login(self):

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'upvote', 'target_id': self.comment.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_media_comment_upvote_button_with_login(self):

        self.client.force_login(self.user)

        # removing user vote if it exists
        user_comment_rating = CommentRating.objects.filter(user_who_added=self.user, comment=self.comment)

        if user_comment_rating.exists():
            user_comment_rating.delete()

        comment_rating_before_post = self.comment.get_rating()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'upvote', 'target_id': self.comment.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        comment_rating: int = self.comment.get_rating()

        self.assertEqual(comment_rating_before_post + 1, comment_rating)

        page_should_contain = {
            'new_rating': comment_rating,
            'target_id': f'{self.comment.id}',
            'not_target_type': 'downvote',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_post_media_comment_downvote_button_without_login(self):

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'downvote', 'target_id': self.comment.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_media_comment_downvote_button_with_login(self):

        self.client.force_login(self.user)

        # removing user vote if it exists
        user_comment_rating = CommentRating.objects.filter(user_who_added=self.user, comment=self.comment)

        if user_comment_rating.exists():
            user_comment_rating.delete()

        comment_rating_before_post = self.comment.get_rating()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'downvote', 'target_id': self.comment.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        comment_rating: int = self.comment.get_rating()

        self.assertEqual(comment_rating_before_post - 1, comment_rating)

        page_should_contain = {
            'new_rating': comment_rating,
            'target_id': f'{self.comment.id}',
            'not_target_type': 'upvote',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_get_media_comment_reply_button_without_login(self):

        response = self.client.get(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'get_comment_reply_form'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_get_media_comment_reply_button_with_login(self):

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'get_comment_reply_form'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django/forms/widgets/input.html')  # response returns form

        page_should_contain: str = render_crispy_form(CreateReplyCommentForm())

        page_content: str = literal_eval(response.content.decode('utf-8'))['under_comment_form']

        self.assertEqual(page_content, page_should_contain)

        self.client.logout()

    def test_get_media_comment_with_replies_without_login(self):

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.media.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/view_media.html')

        page_should_contain = [
            # comment reply:
            self.comment_reply_data['content'],
            self.comment_reply_data['user_who_added'].username,
            naturaltime(self.comment_reply.pub_date),
            self.comment_reply.get_rating(),

            # comment reply reply:
            self.comment_reply_reply_data['content'],
            self.comment_reply_reply_data['user_who_added'].username,
            naturaltime(self.comment_reply_reply.pub_date),
            self.comment_reply_reply.get_rating(),
        ]

        for item in page_should_contain:
            self.assertContains(response, item)

        page_should_not_contain = [
            # comment reply:
            # reply button
            f'data-form-adder-button-target-id="{self.comment_reply.id}" data-requested-form-type="reply"',
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment_reply.id}"',  # upvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment_reply.id}"',  # downvote button
            # report button
            f'data-form-adder-button-target-id="{self.comment_reply.id}" data-requested-form-type="report"',

            # comment reply reply:
            # reply button
            f'data-form-adder-button-target-id="{self.comment_reply_reply.id}" data-requested-form-type="reply"',
            # upvote button
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment_reply_reply.id}"',
            # downvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment_reply_reply.id}"',
            # report button
            f'data-form-adder-button-target-id="{self.comment_reply_reply.id}" data-requested-form-type="report"',
        ]

        for item in page_should_not_contain:
            self.assertNotContains(response, item)

    def test_get_media_comment_with_replies_with_login(self):

        self.client.force_login(self.user)

        response = self.client.get(reverse('view_media', kwargs={'media_id': self.media.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'media_app/view_media.html')

        page_should_contain = [
            # comment reply:
            self.comment_reply_data['content'],
            self.comment_reply_data['user_who_added'].username,
            naturaltime(self.comment_reply.pub_date),
            self.comment_reply.get_rating(),
            # reply button
            f'data-form-adder-button-target-id="{self.comment_reply.id}" data-requested-form-type="reply"',
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment_reply.id}"',  # upvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment_reply.id}"',  # downvote button
            # report button
            f'data-form-adder-button-target-id="{self.comment_reply.id}" data-requested-form-type="report"',

            # comment reply reply:
            self.comment_reply_reply_data['content'],
            self.comment_reply_reply_data['user_who_added'].username,
            naturaltime(self.comment_reply_reply.pub_date),
            self.comment_reply_reply.get_rating(),
            # reply button
            f'data-form-adder-button-target-id="{self.comment_reply_reply.id}" data-requested-form-type="reply"',
            # upvote button
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment_reply_reply.id}"',
            # downvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment_reply_reply.id}"',
            # report button
            f'data-form-adder-button-target-id="{self.comment_reply_reply.id}" data-requested-form-type="report"',
        ]

        for item in page_should_contain:
            self.assertContains(response, item)

        self.client.logout()

    def test_post_add_reply_comment_without_login(self):

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_comment',
                'target_type': 'comment',
                'target_id': f'{self.comment.id}',
                'content': 'content',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_add_reply_comment_with_login(self):

        self.client.force_login(self.user)

        added_comment_data = {
            'content': 'content',
            'user_who_added': self.user,
        }

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_comment',
                'target_type': 'comment',
                'target_id': f'{self.comment.id}',
                'content': added_comment_data['content'],
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        added_comment = Comment.objects.filter(
            content=added_comment_data['content'], user_who_added=added_comment_data['user_who_added']
        )

        self.assertTrue(added_comment.exists())

        added_comment = added_comment[0]

        page_should_contain = {
            'content': added_comment_data['content'],
            'user_who_added': added_comment_data['user_who_added'].username,
            'pub_date': naturaltime(added_comment.pub_date),
            'target_type': Comment.COMMENT_TYPE,
            'target_id': self.comment.id,
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))['comment']

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        added_comment.delete()

        self.client.logout()

    def test_post_reply_comment_upvote_button_without_login(self):

        # reply:
        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'upvote', 'target_id': self.comment_reply.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        # reply reply:
        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'upvote', 'target_id': self.comment_reply_reply.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_reply_comment_upvote_button_with_login(self):

        self.client.force_login(self.user)

        # removing user vote if it exists:
        user_comment_reply_rating = CommentRating.objects.filter(user_who_added=self.user, comment=self.comment_reply)

        if user_comment_reply_rating.exists():
            user_comment_reply_rating.delete()

        comment_reply_rating_before_post = self.comment_reply.get_rating()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'upvote', 'target_id': self.comment_reply.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        comment_reply_rating: int = self.comment_reply.get_rating()

        self.assertEqual(comment_reply_rating_before_post + 1, comment_reply_rating)

        page_should_contain = {
            'new_rating': comment_reply_rating,
            'target_id': f'{self.comment_reply.id}',
            'not_target_type': 'downvote',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_post_reply_reply_comment_upvote_button_with_login(self):

        self.client.force_login(self.user)

        # removing user vote if it exists:
        user_comment_reply_reply_rating = \
            CommentRating.objects.filter(user_who_added=self.user, comment=self.comment_reply_reply)

        if user_comment_reply_reply_rating.exists():
            user_comment_reply_reply_rating.delete()

        comment_reply_reply_rating_before_post = self.comment_reply_reply.get_rating()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'upvote', 'target_id': self.comment_reply_reply.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        comment_reply_reply_rating: int = self.comment_reply_reply.get_rating()

        self.assertEqual(comment_reply_reply_rating_before_post + 1, comment_reply_reply_rating)

        page_should_contain = {
            'new_rating': comment_reply_reply_rating,
            'target_id': f'{self.comment_reply_reply.id}',
            'not_target_type': 'downvote',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_post_reply_comment_downvote_button_without_login(self):

        # reply:
        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'downvote', 'target_id': self.comment_reply.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        # reply reply:
        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'downvote', 'target_id': self.comment_reply_reply.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_reply_comment_downvote_button_with_login(self):

        self.client.force_login(self.user)

        # removing user vote if it exists:
        user_comment_reply_rating = CommentRating.objects.filter(user_who_added=self.user, comment=self.comment_reply)

        if user_comment_reply_rating.exists():
            user_comment_reply_rating.delete()

        comment_reply_rating_before_post = self.comment_reply.get_rating()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'downvote', 'target_id': self.comment_reply.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        comment_reply_rating: int = self.comment_reply.get_rating()

        self.assertEqual(comment_reply_rating_before_post - 1, comment_reply_rating)

        page_should_contain = {
            'new_rating': comment_reply_rating,
            'target_id': f'{self.comment_reply.id}',
            'not_target_type': 'upvote',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_post_reply_reply_comment_downvote_button_with_login(self):

        self.client.force_login(self.user)

        # removing user vote if it exists:
        user_comment_reply_reply_rating = \
            CommentRating.objects.filter(user_who_added=self.user, comment=self.comment_reply_reply)

        if user_comment_reply_reply_rating.exists():
            user_comment_reply_reply_rating.delete()

        comment_reply_reply_rating_before_post = self.comment_reply_reply.get_rating()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'add_comment_vote', 'vote_type': 'downvote', 'target_id': self.comment_reply_reply.id},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        comment_reply_reply_rating: int = self.comment_reply_reply.get_rating()

        self.assertEqual(comment_reply_reply_rating_before_post - 1, comment_reply_reply_rating)

        page_should_contain = {
            'new_rating': comment_reply_reply_rating,
            'target_id': f'{self.comment_reply_reply.id}',
            'not_target_type': 'upvote',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_get_media_comment_report_button_without_login(self):

        response = self.client.get(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'get_comment_report_form'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_get_media_comment_report_button_with_login(self):

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {'request_type': 'get_comment_report_form'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django/forms/widgets/input.html')  # response returns form

        page_should_contain: str = render_crispy_form(CreateReportCommentForm())

        page_content: str = literal_eval(response.content.decode('utf-8'))['under_comment_form']

        self.assertEqual(page_content, page_should_contain)

        self.client.logout()

    def test_post_media_comment_report_without_login(self):

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'comment',
                'target_id': self.comment.id,
                'content': 'good content',
                'report_type': '1',
            },  # 1 - form field value
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_media_comment_report_with_login(self):

        self.client.force_login(self.user)

        # removing the user report if it exists
        user_comment_report = Report.objects.filter(
            user_who_added=self.user, target_type=Report.COMMENT_TYPE, target_id=self.comment.id
        )

        if user_comment_report.exists():
            user_comment_report.delete()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'comment',
                'target_id': self.comment.id,
                'content': 'good content',
                'report_type': '1,2',
            },  # 1, 2 - form field values
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Report.objects.filter(
                user_who_added=self.user, target_type=Report.COMMENT_TYPE, target_id=self.comment.id
            ).exists()
        )

        page_should_contain = {
            'report_success_message': 'Your report has been successfully created!',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_post_reply_comment_report_without_login(self):

        # reply:
        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'comment',
                'target_id': self.comment_reply.id,
                'content': 'good content',
                'report_type': '1',
            },  # 1 - form field value
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

        # reply reply:
        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'comment',
                'target_id': self.comment_reply_reply.id,
                'content': 'good content',
                'report_type': '1',
            },  # 1 - form field value
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/403.html')

    def test_post_reply_comment_report_with_login(self):

        self.client.force_login(self.user)

        # removing the user report if it exists
        user_comment_report = Report.objects.filter(
            user_who_added=self.user, target_type=Report.COMMENT_TYPE, target_id=self.comment_reply.id
        )

        if user_comment_report.exists():
            user_comment_report.delete()

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'comment',
                'target_id': self.comment_reply.id,
                'content': 'good content',
                'report_type': '1,2',
            },  # 1, 2 - form field values
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Report.objects.filter(
                user_who_added=self.user, target_type=Report.COMMENT_TYPE, target_id=self.comment_reply.id
            ).exists()
        )

        page_should_contain = {
            'report_success_message': 'Your report has been successfully created!',
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    def test_post_comment_report_duplicate_data(self):

        self.client.force_login(self.user)

        duplicate_report_data = {
            'content': 'duplicate report content',
            'target_type': Report.COMMENT_TYPE,
            'target_id': self.comment.id,
            'user_who_added': self.user,
        }

        Report.objects.create(**duplicate_report_data)

        response = self.client.post(
            reverse('view_media', kwargs={'media_id': self.media.id}),
            {
                'request_type': 'create_report',
                'target_type': 'comment',
                'target_id': duplicate_report_data['target_id'],
                'content': duplicate_report_data['content'],
                'report_type': '1,2',
            },  # 1, 2 - form field values
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.templates)  # because ajax request does not rendering page

        user_comment_reports = Report.objects.filter(
            user_who_added=self.user, target_type=Report.COMMENT_TYPE, target_id=self.comment.id
        )

        self.assertEqual(1, user_comment_reports.count())

        page_should_contain = {
            'messages': [{
                'level': 40,
                'message': 'You can not create one more report on the same media/comment',
                'tags': 'error',
            }],
        }

        page_content: dict = literal_eval(response.content.decode('utf-8'))

        for field, value in page_should_contain.items():
            self.assertEqual(page_content[field], value)

        self.client.logout()

    @classmethod
    def tearDownClass(cls):

        super().tearDownClass()

        rmtree(TEST_MEDIA_ROOT)
        rmtree(TEST_IMAGES_ROOT)
