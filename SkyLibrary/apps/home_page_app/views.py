from json import dumps

from django.shortcuts import render
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.http import HttpResponse
from django.urls import reverse_lazy

from crispy_forms.utils import render_crispy_form

from accounts_app.models import User
from .forms import FilterMediaForm
from .services import RATING_DIRECTION_CHOICES_LIST, MediaFilter
from media_app.models import MediaRating


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

        media_filter = MediaFilter()

        media_filter.filter_by_rating()

        best_media = media_filter.get(20)

        response_data: dict = {
            'best_media': best_media,
            'is_user_moderator': request.user.role == User.MODERATOR if request.user.is_authenticated else 0,
            'filter_form': FilterMediaForm(),
        }

        return render(request, self.template_name, response_data)

    @staticmethod
    def _filter_media_by_text_safe(
            filter_media_form: FilterMediaForm,
            media_filter: MediaFilter,
            post_field_name: str,
            filter_function_name: str,
    ) -> None:

        field_value = filter_media_form.cleaned_data.get(post_field_name, None)

        if field_value:
            getattr(media_filter, filter_function_name)(field_value)

    def post(self, request):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.POST.get('request_type') == 'filter_media':

            # needed for correct work with the frontend:

            request_post_mutable = request.POST.copy()

            if tags := request_post_mutable['tags']:
                tags = tags.split(',')

            else:
                tags = []

            request_post_mutable.setlist('tags', tags)

            filter_media_form = FilterMediaForm(request_post_mutable)

            if filter_media_form.is_valid():

                media_filter = MediaFilter()

                # rating part:

                rating_filters = {
                    'minimum_value': filter_media_form.cleaned_data.get('rating_minimum_value', None),
                    'maximum_value': filter_media_form.cleaned_data.get('rating_maximum_value', None),
                    'direction': filter_media_form.cleaned_data.get('rating_direction', None),
                }

                # convert numbers in strings to numbers ('1' -> 1)
                for key, value in rating_filters.items():
                    if value and value.isdigit():
                        rating_filters[key] = int(value)

                # removing unavailable filters:

                if rating_filters['minimum_value'] not in MediaRating.rating_choices_list:
                    del rating_filters['minimum_value']

                if rating_filters['maximum_value'] not in MediaRating.rating_choices_list:
                    del rating_filters['maximum_value']

                if rating_filters['direction'] not in RATING_DIRECTION_CHOICES_LIST:
                    del rating_filters['direction']

                if rating_filters:
                    media_filter.filter_by_rating(**rating_filters)

                # tags part:

                tags_filter = filter_media_form.cleaned_data.get('tags', [])

                if any(tags_filter):
                    media_filter.filter_by_tags(tags_filter)

                # user_who_added, title and author part:

                text_filters = (
                    ('user_who_added', 'filter_by_user_who_added'),
                    ('title', 'filter_by_title'),
                    ('author', 'filter_by_author'),
                )

                for post_field_name, filter_function_name in text_filters:
                    self._filter_media_by_text_safe(
                        filter_media_form, media_filter, post_field_name, filter_function_name
                    )

                # return part:

                page_media_data = []

                if media_filter_result := media_filter.get(20):

                    language = get_language()

                    if language == 'en-us':
                        language_suffix = 'en_us'

                    elif language == 'ru':
                        language_suffix = 'ru'

                    else:
                        return handler500(request)

                    for page_media_object in media_filter_result:

                        page_media_object_tags = []

                        for tag in page_media_object.tags.values():
                            page_media_object_tags.append({
                                'name': tag[f'name_{language_suffix}'],
                                'help_text': tag[f'help_text_{language_suffix}'],
                            })

                        page_media_data.append({
                            'title': page_media_object.title,
                            'rating': page_media_object.get_rating(),
                            'link': f"{reverse_lazy('view_media', kwargs={'media_id': page_media_object.id})}",
                            'tags': page_media_object_tags,
                        })

                return HttpResponse(
                    dumps({'filter_results': page_media_data}), content_type='application/json'
                )

            else:
                return handler400(request)

        else:
            return handler404(request)
