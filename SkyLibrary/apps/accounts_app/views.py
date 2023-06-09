from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from json import dumps

from accounts_app.models import User
from media_app.models import Media, MediaDownload, MediaRating
from home_page_app.views import handler404
from .forms import CreateOrUpdateMediaRating


class CustomPasswordResetView(PasswordResetView):

    template_name = 'accounts_app/password_reset.html'
    email_template_name = 'accounts_app/password_reset_email.html'
    success_url = reverse_lazy('password_reset_successful')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):

    template_name = 'accounts_app/password_reset_confirm.html'
    success_url = reverse_lazy('custom_password_reset_complete')


class CustomPasswordChangeView(PasswordChangeView):

    template_name = 'accounts_app/password_change.html'
    success_url = reverse_lazy('password_change_successful')


class ViewProfile(LoginRequiredMixin, View):

    template_name: str = 'accounts_app/profile.html'

    def get(self, request):

        media_active_choices_dict = dict(Media.active_choices)
        media_added_by_user = []

        for media in Media.objects.filter(user_who_added=request.user).order_by('-id'):
            media_added_by_user.append({
                'media': media,
                'active': media_active_choices_dict[media.active],
                'is_user_can_edit': media.active == Media.ACTIVE,
            })

        user_downloads = []

        for download in MediaDownload.objects.filter(user_who_added=request.user).order_by('-id'):

            media = download.media

            if media.active != Media.ACTIVE:
                continue

            media_rating_by_user = MediaRating.objects.filter(user_who_added=request.user, media=media)

            if media_rating_by_user.exists():
                media_rating_by_user = media_rating_by_user[0].rating

            else:
                media_rating_by_user = 0

            user_downloads.append(
                {
                    'media_title': media.title,
                    'media_id': media.id,
                    'media_rating_by_user': media_rating_by_user,
                    'media_tags': media.tags,
                }
            )

        response_data: dict = {
            'is_user_moderator': request.user.role == User.MODERATOR if request.user.is_authenticated else 0,
            'media_added_by_user': media_added_by_user,
            'user_downloads': user_downloads,
        }

        return render(request, self.template_name, response_data)

    @staticmethod
    def post(request):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.POST.get('request_type') == 'update_media_rating':

            media_id = request.POST.get('media_id')
            new_rating = request.POST.get('new_rating')

            media = get_object_or_404(Media, id=media_id)

            if media.active != Media.ACTIVE:
                return handler404(request)

            if media and new_rating:

                create_or_update_media_rating_form_data = {
                    'media': media,
                    'user_who_added': request.user,
                    'rating': new_rating,
                }

                try:
                    instance = MediaRating.objects.get(media=media)

                except MediaRating.DoesNotExist:
                    instance = None

                form = CreateOrUpdateMediaRating(create_or_update_media_rating_form_data, instance=instance)

                if form.is_valid():

                    media_rating_data = {
                        'media': form.cleaned_data['media'],
                        'user_who_added': form.cleaned_data['user_who_added'],
                        'rating': form.cleaned_data['rating'],
                    }

                    if instance:
                        MediaRating.objects.filter(
                            media=media_rating_data['media'], user_who_added=media_rating_data['user_who_added']
                        ).update(rating=media_rating_data['rating'])

                    else:
                        MediaRating.objects.create(**media_rating_data)

                    return HttpResponse(
                        dumps({'result_rating': media_rating_data['rating']}), content_type='application/json'
                    )

            return HttpResponse(dumps({'result_rating': ''}), content_type='application/json')

        else:
            return handler404(request)
