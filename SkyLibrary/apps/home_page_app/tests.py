from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse

from crispy_forms.utils import render_crispy_form

from ast import literal_eval

from .views import handler400, handler403, handler404, handler500
from .forms import SearchMediaForm
from media_app.models import Media, MediaTags

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

        page_should_contain = (
            f'<a href="/en-us/media/view/{self.media_1.id}/" class="font-italic">{self.media_1.title}</a>',
            f'<a href="/en-us/media/view/{self.media_2.id}/" class="font-italic">{self.media_2.title}</a>',
        )

        for item in page_should_contain:
            self.assertContains(response, item)

        self.assertNotContains(
            response, f'<a href="/en-us/media/view/{self.not_active_media.id}/">{self.not_active_media.title}</a>'
        )


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


class SearchMediaTestCase(TestCase):

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

        test_tag_1 = MediaTags.objects.create(
            name_en_us='test tag 1',
            help_text_en_us='test tag 1 help text',
            name_ru='test tag 1 ru',
            help_text_ru='test tag 1 help text ru',
            user_who_added=user,
        )
        test_tag_2 = MediaTags.objects.create(
            name_en_us='test tag 2',
            help_text_en_us='test tag 2 help text',
            name_ru='test tag 2 ru',
            help_text_ru='test tag 2 help text ru',
            user_who_added=user,
        )

        cls.media_1_tags = (test_tag_1,)
        cls.media_2_tags = (test_tag_2,)
        cls.media_3_tags = (test_tag_1, test_tag_2)

        cls.media_1_and_3_tags_ids = f"{test_tag_1.id}"

        cls.media_search_1_and_2_medias_title_key = 'key1'
        cls.media_search_1_and_3_medias_title_key = 'key2'

        cls.media_data_1 = {
            'title':
                f'test_title_1_{cls.media_search_1_and_2_medias_title_key}_{cls.media_search_1_and_3_medias_title_key}',
            'description': 'test_description_1',
            'author': 'test_author',
            'user_who_added': user,
            'active': 1,
        }
        cls.media_data_2 = {
            'title': f'test_title_2_{cls.media_search_1_and_2_medias_title_key}',
            'description': 'test_description_2',
            'author': 'test_author',
            'user_who_added': user,
            'active': 1,
        }
        cls.media_data_3 = {
            'title': f'test_title_3_{cls.media_search_1_and_3_medias_title_key}',
            'description': 'test_description_3',
            'author': 'test_author',
            'user_who_added': user,
            'active': 1,
        }

        cls.media_1 = Media.objects.create(**cls.media_data_1)
        cls.media_2 = Media.objects.create(**cls.media_data_2)
        cls.media_3 = Media.objects.create(**cls.media_data_3)

        cls.media_1.tags.set(cls.media_1_tags)
        cls.media_2.tags.set(cls.media_2_tags)
        cls.media_3.tags.set(cls.media_3_tags)

    def test_get_search_button(self):

        response = self.client.get(reverse('index'))

        self.assertContains(response, '<button id="get_search_media_form_button"')

    def test_get_search_media_form_incorrect_data(self):

        response = self.client.get(
            reverse('index'),
            {'request_type': 'bad_data'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home_page_app/index.html')

    def test_get_search_media_form(self):

        response = self.client.get(
            reverse('index'),
            {'request_type': 'get_search_media_form'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django/forms/widgets/input.html')  # response returns form

        page_should_contain: str = render_crispy_form(SearchMediaForm())

        page_content: str = literal_eval(response.content.decode('utf-8'))['search_media_form']

        self.assertEqual(page_content, page_should_contain)

    def test_post_search_media_form_empty_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'search_media',
                'text': '',
                'tags': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        page_should_contain: str = 'Please specify any text or tags to search for'

        # response content example:
        # {'messages': [{'level': 40, 'message': 'Please specify any text or tags to search for', 'tags': 'error'}]}
        page_content = literal_eval(response.content.decode('utf-8'))['messages']

        # page_content example:
        # [{'level': 40, 'message': 'Please specify any text or tags to search for', 'tags': 'error'}]
        self.assertEqual(len(page_content), 1)

        page_content = page_content[0]['message']

        self.assertEqual(page_content, page_should_contain)

    def test_post_search_media_form_tags_incorrect_data(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'search_media',
                'text': '',
                'tags': '998,999',  # not exist tag ids
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        page_should_contain: str = \
            'Something went wrong with your request, please try again or contact support (code: 5.1)'

        # response content example:
        # {'messages': [{'level': 40, 'message': 'Please specify any text or tags to search for', 'tags': 'error'}]}
        page_content: str = literal_eval(response.content.decode('utf-8'))['messages'][0]['message']

        self.assertEqual(page_content, page_should_contain)

    def test_post_search_media_form_text_incorrect_data(self):

        too_long_text = 'too_looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo' \
                        'oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong'

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'search_media',
                'text': too_long_text,
                'tags': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        page_should_contain: str = 'Ensure this value has at most 100 characters (it has 186).'

        # response content example:
        # {'messages': [{'level': 40, 'message': 'Please specify any text or tags to search for', 'tags': 'error'}]}
        page_content = literal_eval(response.content.decode('utf-8'))['messages']

        # page_content example:
        # [{'level': 40, 'message': 'Please specify any text or tags to search for', 'tags': 'error'}]
        self.assertEqual(len(page_content), 1)

        page_content = page_content[0]['message']

        self.assertEqual(page_content, page_should_contain)

    def test_post_search_media_form_text(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'search_media',
                'text': f"{self.media_search_1_and_2_medias_title_key}",
                'tags': '',
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        # response content example:
        # {'search_results': {'test_title_1': {'tags': [{'name': 'test tag 1 ru',
        # 'help_text': 'test tag 1 help text ru'}], 'rating': 0, 'link': '/en-us/media/view/4/'}}}
        page_content = literal_eval(response.content.decode('utf-8'))['search_results']

        self.assertEqual(len(page_content), 2)

        for i, (search_result_key, search_result_value) in enumerate(page_content.items()):

            if i == 0:

                media = self.media_2
                media_data = self.media_data_2
                media_tags = self.media_2_tags

            elif i == 1:

                media = self.media_1
                media_data = self.media_data_1
                media_tags = self.media_1_tags

            self.assertEqual(media_data['title'], search_result_key)

            self.assertEqual(search_result_value['rating'], media.get_rating())
            self.assertEqual(search_result_value['link'], reverse('view_media', kwargs={'media_id': media.id}))

            for response_tag, media_tag in zip(search_result_value['tags'], media_tags):

                self.assertEqual(response_tag['name'], media_tag.name_en_us)
                self.assertEqual(response_tag['help_text'], media_tag.help_text_en_us)

    def test_post_search_media_form_tags(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'search_media',
                'text': '',
                'tags': f"{self.media_1_and_3_tags_ids}",
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        # response content example:
        # {'search_results': {'test_title_1': {'tags': [{'name': 'test tag 1 ru',
        # 'help_text': 'test tag 1 help text ru'}], 'rating': 0, 'link': '/en-us/media/view/4/'}}}
        page_content = literal_eval(response.content.decode('utf-8'))['search_results']

        self.assertEqual(len(page_content), 2)

        for i, (search_result_key, search_result_value) in enumerate(page_content.items()):

            if i == 0:

                media = self.media_3
                media_data = self.media_data_3
                media_tags = self.media_3_tags

            elif i == 1:

                media = self.media_1
                media_data = self.media_data_1
                media_tags = self.media_1_tags

            self.assertEqual(media_data['title'], search_result_key)

            self.assertEqual(search_result_value['rating'], media.get_rating())
            self.assertEqual(search_result_value['link'], reverse('view_media', kwargs={'media_id': media.id}))

            for response_tag, media_tag in zip(search_result_value['tags'], media_tags):

                self.assertEqual(response_tag['name'], media_tag.name_en_us)
                self.assertEqual(response_tag['help_text'], media_tag.help_text_en_us)

    def test_post_search_media_form_all(self):

        response = self.client.post(
            reverse('index'),
            {
                'request_type': 'search_media',
                'text': f"{self.media_search_1_and_3_medias_title_key}",
                'tags': f"{self.media_1_and_3_tags_ids}",
            },
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )

        self.assertEqual(response.status_code, 200)

        # response content example:
        # {'search_results': {'test_title_1': {'tags': [{'name': 'test tag 1 ru',
        # 'help_text': 'test tag 1 help text ru'}], 'rating': 0, 'link': '/en-us/media/view/4/'}}}
        page_content = literal_eval(response.content.decode('utf-8'))['search_results']

        self.assertEqual(len(page_content), 2)

        for i, (search_result_key, search_result_value) in enumerate(page_content.items()):

            if i == 0:

                media = self.media_3
                media_data = self.media_data_3
                media_tags = self.media_3_tags

            elif i == 1:

                media = self.media_1
                media_data = self.media_data_1
                media_tags = self.media_1_tags

            self.assertEqual(media_data['title'], search_result_key)

            self.assertEqual(search_result_value['rating'], media.get_rating())
            self.assertEqual(search_result_value['link'], reverse('view_media', kwargs={'media_id': media.id}))

            for response_tag, media_tag in zip(search_result_value['tags'], media_tags):

                self.assertEqual(response_tag['name'], media_tag.name_en_us)
                self.assertEqual(response_tag['help_text'], media_tag.help_text_en_us)
