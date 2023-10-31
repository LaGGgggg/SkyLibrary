from ast import literal_eval
from re import sub

from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse

from crispy_forms.utils import render_crispy_form

from .views import handler400, handler403, handler404, handler500
from .forms import FilterMediaForm
from media_app.models import Media, MediaTags, MediaRating
from .services import _ASCENDING, _DESCENDING

User = get_user_model()


class CommonTestCase(TestCase):

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

        user = User.objects.create_user(**user_credentials)

        media_data_1 = {
            'title': 'test_title_1',
            'description': 'test_description_1',
            'author': 'test_author',
            'user_who_added': user,
            'active': 1,
        }
        media_data_2 = {
            'title': 'test_title_2',
            'description': 'test_description_2',
            'author': 'test_author',
            'user_who_added': user,
            'active': 1,
        }
        not_active_media_data = {
            'title': 'test_title_3',
            'description': 'test_description_3',
            'author': 'test_author',
            'user_who_added': user,
            'active': 0,
        }

        cls.media_1 = Media.objects.create(**media_data_1)
        cls.media_2 = Media.objects.create(**media_data_2)
        cls.not_active_media = Media.objects.create(**not_active_media_data)

    def test_index_page(self):

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home_page_app/index.html')

        page_should_contain = render_crispy_form(FilterMediaForm())

        # removing csrf token:
        response_content = (
            sub(r' <input type="hidden" name="csrfmiddlewaretoken" value=".+">', '', response.content.decode())
        )

        self.assertIn(page_should_contain, response_content)


class ErrorsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.request_factory = RequestFactory()

    def test_400_error_page(self):

        request = self.request_factory.get('/')

        with self.assertTemplateUsed('errors/400.html'):
            response = handler400(request, exception=None)

        self.assertContains(response, 'Oops, invalid url', status_code=400)

    def test_403_error_page(self):

        request = self.request_factory.get('/')

        with self.assertTemplateUsed('errors/403.html'):
            response = handler403(request, exception=None)

        self.assertContains(response, 'Oops, you do not have permission to do this', status_code=403)

    def test_404_error_page(self):

        request = self.request_factory.get('/')

        with self.assertTemplateUsed('errors/404.html'):
            response = handler404(request, exception=None)

        self.assertContains(response, 'Oops, page not found', status_code=404)

    def test_500_error_page(self):

        request = self.request_factory.get('/')

        with self.assertTemplateUsed('errors/500.html'):
            response = handler500(request)

        self.assertContains(response, 'Oops, server error', status_code=500)


class FilterMediaTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.client = Client()

        user_credentials_1 = {
            'username': 'test_user_1',
            'password': 'test_password',
            'email': 'test_email_1@mail.com',
            'role': 1,
        }

        user_credentials_2 = {
            'username': 'test_user_2',
            'password': 'test_password',
            'email': 'test_email_2@mail.com',
            'role': 1,
        }

        user_1 = User.objects.create_user(**user_credentials_1)
        cls.user_2 = User.objects.create_user(**user_credentials_2)

        test_tag_1 = MediaTags.objects.create(
            name_en_us='test tag 1',
            help_text_en_us='test tag 1 help text',
            name_ru='test tag 1 ru',
            help_text_ru='test tag 1 help text ru',
            user_who_added=user_1,
        )
        test_tag_2 = MediaTags.objects.create(
            name_en_us='test tag 2',
            help_text_en_us='test tag 2 help text',
            name_ru='test tag 2 ru',
            help_text_ru='test tag 2 help text ru',
            user_who_added=user_1,
        )

        cls.media_1_tags = (test_tag_1,)
        cls.media_2_tags = (test_tag_2,)
        cls.media_3_tags = (test_tag_1, test_tag_2)

        cls.media_1_and_3_tags_ids = f"{test_tag_1.id}"

        cls.media_filter_1_and_2_medias_title_key = 'key1'
        cls.media_filter_1_and_3_medias_title_key = 'key2'

        cls.media_data_1 = {
            'title':
                f'test_title_1_{cls.media_filter_1_and_2_medias_title_key}_{cls.media_filter_1_and_3_medias_title_key}',
            'description': 'test_description_1',
            'author': 'test_author',
            'user_who_added': user_1,
            'active': 1,
        }
        cls.media_data_2 = {
            'title': f'test_title_2_{cls.media_filter_1_and_2_medias_title_key}',
            'description': 'test_description_2',
            'author': 'test_author',
            'user_who_added': user_1,
            'active': 1,
        }
        cls.media_data_3 = {
            'title': f'test_title_3_{cls.media_filter_1_and_3_medias_title_key}',
            'description': 'test_description_3',
            'author': 'test_author_2',
            'user_who_added': cls.user_2,
            'active': 1,
        }

        cls.media_1 = Media.objects.create(**cls.media_data_1)
        cls.media_2 = Media.objects.create(**cls.media_data_2)
        cls.media_3 = Media.objects.create(**cls.media_data_3)

        cls.media_1.tags.set(cls.media_1_tags)
        cls.media_2.tags.set(cls.media_2_tags)
        cls.media_3.tags.set(cls.media_3_tags)

        # minimum rating
        cls.media_1_rating = MediaRating.objects.create(
            media=cls.media_1,
            user_who_added=user_1,
            rating=MediaRating.rating_choices_list[0],
        )
        # medium rating
        cls.media_2_rating = MediaRating.objects.create(
            media=cls.media_2,
            user_who_added=user_1,
            rating=MediaRating.rating_choices_list[2],
        )
        # maximum rating
        cls.media_3_rating = MediaRating.objects.create(
            media=cls.media_3,
            user_who_added=user_1,
            rating=MediaRating.rating_choices_list[-1],
        )

    def test_post_filter_media_form_empty_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': '',
                'author': '',
                'tags': '',
                'rating_direction': '',
                'rating_minimum_value': '',
                'rating_maximum_value': '',
                'user_who_added': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        # response content example:
        # [{'title': 'test_title_1_key1_key2', 'rating': 0, 'link': '/en-us/media/view/7/',
        # 'tags': [{'name': 'test tag 1', 'help_text': 'test tag 1 help text'}]}]
        page_content = literal_eval(response.content.decode('utf-8'))['filter_results']

        expected_result_data = (
            (self.media_1, self.media_data_1, self.media_1_tags),
            (self.media_2, self.media_data_2, self.media_2_tags),
            (self.media_3, self.media_data_3, self.media_3_tags),
        )

        self.assertEqual(len(page_content), len(expected_result_data))

        for i in range(len(expected_result_data)):

            media, media_data, media_tags = expected_result_data[i]
            filter_result = page_content[i]

            self.assertEqual(media_data['title'], filter_result['title'])

            self.assertEqual(filter_result['rating'], media.get_rating())
            self.assertEqual(filter_result['link'], reverse('view_media', kwargs={'media_id': media.id}))

            for response_tag, media_tag in zip(filter_result['tags'], media_tags):

                self.assertEqual(response_tag['name'], media_tag.name_en_us)
                self.assertEqual(response_tag['help_text'], media_tag.help_text_en_us)

    def test_post_filter_media_form_tags_incorrect_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': '',
                'author': '',
                'tags': '998,999',  # not exist tag ids
                'rating_direction': '',
                'rating_minimum_value': '',
                'rating_maximum_value': '',
                'user_who_added': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 400)

    def test_post_filter_media_form_title_incorrect_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': 'f' * 301,
                'author': '',
                'tags': '',
                'rating_direction': '',
                'rating_minimum_value': '',
                'rating_maximum_value': '',
                'user_who_added': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 400)

    def test_post_filter_media_form_author_incorrect_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': '',
                'author': 'f' * 301,
                'tags': '',
                'rating_direction': '',
                'rating_minimum_value': '',
                'rating_maximum_value': '',
                'user_who_added': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 400)

    def test_post_filter_media_form_user_who_added_incorrect_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': '',
                'author': '',
                'tags': '',
                'rating_direction': '',
                'rating_minimum_value': '',
                'rating_maximum_value': '',
                'user_who_added': 'f' * 301,
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 400)

    def test_post_filter_media_form_rating_direction_incorrect_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': '',
                'author': '',
                'tags': '',
                'rating_direction': 'bad_direction_value',
                'rating_minimum_value': '',
                'rating_maximum_value': '',
                'user_who_added': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 400)

    def test_post_filter_media_form_rating_minimum_value_incorrect_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': '',
                'author': '',
                'tags': '',
                'rating_direction': '',
                'rating_minimum_value': 'bad_minimum_value',
                'rating_maximum_value': '',
                'user_who_added': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 400)

    def test_post_filter_media_form_rating_maximum_value_incorrect_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': '',
                'author': '',
                'tags': '',
                'rating_direction': '',
                'rating_minimum_value': '',
                'rating_maximum_value': 'bad_maximum_value',
                'user_who_added': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 400)

    def _test_post_filter_media_form_field(
            self,
            field_name: str,
            field_text: str,
            expected_result_data: tuple[tuple[Media, dict, tuple[MediaTags, ...]], ...],
    ) -> None:

        post_data = {
            'request_type': 'filter_media',
            'title': '',
            'author': '',
            'tags': '',
            'rating_direction': '',
            'rating_minimum_value': '',
            'rating_maximum_value': '',
            'user_who_added': '',
        }

        post_data[field_name] = field_text

        response = self.client.post(reverse('index'), post_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        self.assertEqual(response.status_code, 200)

        # response content example:
        # [{'title': 'test_title_1_key1_key2', 'rating': 0, 'link': '/en-us/media/view/7/',
        # 'tags': [{'name': 'test tag 1', 'help_text': 'test tag 1 help text'}]}]
        page_content = literal_eval(response.content.decode('utf-8'))['filter_results']

        self.assertEqual(len(page_content), len(expected_result_data))

        for i in range(len(expected_result_data)):

            media, media_data, media_tags = expected_result_data[i]
            filter_result = page_content[i]

            self.assertEqual(media_data['title'], filter_result['title'])

            self.assertEqual(filter_result['rating'], media.get_rating())
            self.assertEqual(filter_result['link'], reverse('view_media', kwargs={'media_id': media.id}))

            for response_tag, media_tag in zip(filter_result['tags'], media_tags):

                self.assertEqual(response_tag['name'], media_tag.name_en_us)
                self.assertEqual(response_tag['help_text'], media_tag.help_text_en_us)

    def test_post_filter_media_form_title(self):
        self._test_post_filter_media_form_field(
            'title',
            f"{self.media_filter_1_and_2_medias_title_key}",
            (
                (self.media_1, self.media_data_1, self.media_1_tags),
                (self.media_2, self.media_data_2, self.media_2_tags),
            ),
        )

    def test_post_filter_media_form_author(self):
        self._test_post_filter_media_form_field(
            'author',
            f"{self.media_data_3['author']}",
            (
                (self.media_3, self.media_data_3, self.media_3_tags),
            ),
        )

    def test_post_filter_media_form_user_who_added(self):
        self._test_post_filter_media_form_field(
            'user_who_added',
            f"{self.user_2.username}",
            (
                (self.media_3, self.media_data_3, self.media_3_tags),
            ),
        )

    def test_post_search_media_form_tags(self):
        self._test_post_filter_media_form_field(
            'tags',
            f"{self.media_1_and_3_tags_ids}",
            (
                (self.media_1, self.media_data_1, self.media_1_tags),
                (self.media_3, self.media_data_3, self.media_3_tags),
            ),
        )

    def test_post_search_media_form_rating_direction_ascending(self):
        self._test_post_filter_media_form_field(
            'rating_direction',
            f'{_ASCENDING}',
            (
                (self.media_1, self.media_data_1, self.media_1_tags),
                (self.media_2, self.media_data_2, self.media_2_tags),
                (self.media_3, self.media_data_3, self.media_3_tags),
            ),
        )

    def test_post_search_media_form_rating_direction_descending(self):
        self._test_post_filter_media_form_field(
            'rating_direction',
            f'{_DESCENDING}',
            (
                (self.media_3, self.media_data_3, self.media_3_tags),
                (self.media_2, self.media_data_2, self.media_2_tags),
                (self.media_1, self.media_data_1, self.media_1_tags),
            ),
        )

    def test_post_search_media_form_rating_minimum_value(self):
        self._test_post_filter_media_form_field(
            'rating_minimum_value',
            f'{self.media_2_rating.rating}',
            (
                (self.media_3, self.media_data_3, self.media_3_tags),
                (self.media_2, self.media_data_2, self.media_2_tags),
            ),
        )

    def test_post_search_media_form_rating_maximum_value(self):
        self._test_post_filter_media_form_field(
            'rating_maximum_value',
            f'{self.media_2_rating.rating}',
            (
                (self.media_2, self.media_data_2, self.media_2_tags),
                (self.media_1, self.media_data_1, self.media_1_tags),
            ),
        )

    def test_post_search_media_form_all(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'filter_media',
                'title': self.media_1.title,
                'author': self.media_1.author,
                'tags': f"{self.media_1_tags[0].id}",
                'rating_direction': _ASCENDING,
                'rating_minimum_value': self.media_1_rating.rating,
                'rating_maximum_value': self.media_1_rating.rating,
                'user_who_added': self.media_1.user_who_added.username,
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        # response content example:
        # [{'title': 'test_title_1_key1_key2', 'rating': 0, 'link': '/en-us/media/view/7/',
        # 'tags': [{'name': 'test tag 1', 'help_text': 'test tag 1 help text'}]}]
        page_content = literal_eval(response.content.decode('utf-8'))['filter_results']

        expected_result_data = (
            (self.media_1, self.media_data_1, self.media_1_tags),
        )

        self.assertEqual(len(page_content), len(expected_result_data))

        for i in range(len(expected_result_data)):

            media, media_data, media_tags = expected_result_data[i]
            filter_result = page_content[i]

            self.assertEqual(media_data['title'], filter_result['title'])

            self.assertEqual(filter_result['rating'], media.get_rating())
            self.assertEqual(filter_result['link'], reverse('view_media', kwargs={'media_id': media.id}))

            for response_tag, media_tag in zip(filter_result['tags'], media_tags):

                self.assertEqual(response_tag['name'], media_tag.name_en_us)
                self.assertEqual(response_tag['help_text'], media_tag.help_text_en_us)
