from django.test import TestCase
from django.test.client import Client, RequestFactory

from .views import handler400, handler403, handler404, handler500


class HomePageAppTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.client = Client()

    def test_index_page(self):

        response = self.client.get('/en-us/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home_page_app/index.html')


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
