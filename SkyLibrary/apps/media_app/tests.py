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

from media_app.models import Media, MediaTags, MediaDownload, Comment, CommentRating, get_cover_upload, get_file_upload
from media_app.forms import CreateReplyCommentForm

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
            f' class="float-right cover_image">'
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
            f' class="float-right cover_image">'
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
            f'data-reply-button-target-id="{self.comment.id}"',  # reply button
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
            f'data-reply-button-target-id="{self.comment.id}"',  # reply button
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

        page_content: str = literal_eval(response.content.decode('utf-8'))['comment_reply_form']

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
            f'data-reply-button-target-id="{self.comment_reply.id}"',  # reply button
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment_reply.id}"',  # upvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment_reply.id}"',  # downvote button

            # comment reply reply:
            f'data-reply-button-target-id="{self.comment_reply_reply.id}"',  # reply button
            # upvote button
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment_reply_reply.id}"',
            # downvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment_reply_reply.id}"',
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
            f'data-reply-button-target-id="{self.comment_reply.id}"',  # reply button
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment_reply.id}"',  # upvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment_reply.id}"',  # downvote button

            # comment reply reply:
            self.comment_reply_reply_data['content'],
            self.comment_reply_reply_data['user_who_added'].username,
            naturaltime(self.comment_reply_reply.pub_date),
            self.comment_reply_reply.get_rating(),
            f'data-reply-button-target-id="{self.comment_reply_reply.id}"',  # reply button
            # upvote button
            f'data-vote-button-type="upvote" data-vote-button-target-id="{self.comment_reply_reply.id}"',
            # downvote button
            f'data-vote-button-type="downvote" data-vote-button-target-id="{self.comment_reply_reply.id}"',
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

    @classmethod
    def tearDownClass(cls):

        super().tearDownClass()

        rmtree(TEST_MEDIA_ROOT)
        rmtree(TEST_IMAGES_ROOT)
