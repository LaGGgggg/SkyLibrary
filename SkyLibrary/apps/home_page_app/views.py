from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.http import HttpResponse
from django.db.models import QuerySet
from django.urls import reverse_lazy

from crispy_forms.utils import render_crispy_form

from json import dumps

from media_app.models import Media, MediaTags, get_best_active_media
from accounts_app.models import User
from .forms import SearchMediaForm
from utils_app.services import messages_to_json


def handler400(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def handler403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def handler404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)


class ViewIndex(View):

    template_name: str = 'home_page_app/index.html'

    error_messages = {
        'bad_request':
            _('Something went wrong with your request, please try again or contact support (code: {error_code})'),
    }

    def get(self, request):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.GET.get('request_type') == 'get_search_media_form':

            return HttpResponse(
                dumps({'search_media_form': render_crispy_form(form=SearchMediaForm())}),
                content_type='application/json',
            )

        else:

            recent_media = Media.objects.filter(active=1).order_by('pub_date')[:5]
            best_media = get_best_active_media(amount=5)

            response_data: dict = {
                'recent_media': recent_media,
                'best_media': best_media,
                'is_user_moderator': request.user.role == User.MODERATOR if request.user.is_authenticated else 0,
            }

            return render(request, self.template_name, response_data)

    @staticmethod
    def _search_by_text(text: str) -> QuerySet:
        return Media.objects.filter(title__contains=text)

    @staticmethod
    def _search_by_tags(tags: QuerySet[MediaTags], query_set: QuerySet[Media] = None) -> QuerySet:

        for tag in tags:

            if query_set:
                query_set = query_set.filter(tags=tag)

            else:
                query_set = Media.objects.filter(tags=tag)

        return query_set

    def post(self, request):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.POST.get('request_type') == 'search_media':

            if request.POST.get('tags'):

                request_post_mutable = request.POST.copy()

                request_post_mutable.setlist('tags', request_post_mutable['tags'].split(','))

                form = SearchMediaForm(request_post_mutable)

            else:
                form = SearchMediaForm(request.POST)

            form_valid = False

            # if no tags selected => validation error, but we can search only by text => if it is "no tags selected"
            # error, we allowed to use this "invalid" form
            # (and set cleaned_data['tags'] value to empty string for compatibility and safety).
            if not request.POST.get('tags') and len(form.errors.keys()) == 1 and form.has_error('tags'):

                form.cleaned_data['tags'] = ''
                form_valid = True

            if form.is_valid() or form_valid:

                if form.cleaned_data['text'] and form.cleaned_data['tags']:

                    search_results = self._search_by_text(form.cleaned_data['text'])  # filter by text
                    search_results = self._search_by_tags(form.cleaned_data['tags'], search_results)  # filter by tags

                elif form.cleaned_data['text']:
                    search_results = self._search_by_text(form.cleaned_data['text'])

                elif form.cleaned_data['tags']:
                    search_results = self._search_by_tags(form.cleaned_data['tags'])

                else:

                    messages.error(request, _('Please specify any text or tags to search for'))

                    return HttpResponse(messages_to_json(request), content_type='application/json')

                search_results_json = {}

                language = get_language()

                for result in search_results:

                    tags = []

                    if language == 'en-us':
                        for tag in result.tags.values():
                            tags.append(
                                {
                                    'name': tag['name_en_us'],
                                    'help_text': tag['help_text_en_us'],
                                }
                            )

                    elif language == 'ru':
                        for tag in result.tags.values():
                            tags.append(
                                {
                                    'name': tag['name_ru'],
                                    'help_text': tag['help_text_ru'],
                                }
                            )

                    else:

                        messages.error(request, self.error_messages.get('bad_request').format(error_code='5.2'))

                        return HttpResponse(messages_to_json(request), content_type='application/json')

                    link = f"{reverse_lazy('view_media', kwargs={'media_id': result.id})}"

                    search_results_json[result.title] = {
                        'tags': tags,
                        'rating': result.get_rating(),
                        'link': link,
                    }

                return HttpResponse(dumps({'search_results': search_results_json}), content_type='application/json')

            else:

                if request.POST.get('tags') and form.has_error('tags'):
                    messages.error(request, self.error_messages.get('bad_request').format(error_code='5.1'))

                if form.has_error('text'):
                    messages.error(request, form.errors['text'])

                for error in form.non_field_errors():
                    messages.error(request, error)

                return HttpResponse(messages_to_json(request), content_type='application/json')

        else:
            return handler404(request)
