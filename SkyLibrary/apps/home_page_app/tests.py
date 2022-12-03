from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.contrib.auth import get_user_model

from .views import handler400, handler403, handler404, handler500
from media_app.models import Media

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

        response = self.client.get('/en-us/')

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
