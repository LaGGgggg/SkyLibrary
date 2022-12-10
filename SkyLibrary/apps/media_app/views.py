from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from json import dumps

from .models import Media, MediaDownload
from .forms import CreateMediaForm
from staff_app.models import ModeratorTask
from staff_app.views import ViewModeratorPage


User = get_user_model()
ViewModeratorPage = ViewModeratorPage()


class ViewCreateMedia(LoginRequiredMixin, CreateView):

    form_class = CreateMediaForm
    model = Media
    template_name = 'media_app/create_media.html'
    success_url = reverse_lazy('create_media_successful')

    def form_valid(self, form):

        form.instance.user_who_added = self.request.user

        return super().form_valid(form)


class ViewViewMedia(View):

    template_name = 'media_app/view_media.html'
    not_found_template_name = 'errors/404.html'
    no_permission_template_name = 'errors/403.html'

    @staticmethod
    def get_media(media_id: int) -> Media | None:

        try:
            return Media.objects.get(id=media_id)

        except Media.DoesNotExist:
            return None

    @staticmethod
    def is_moderate(request, media: Media) -> bool:

        if not request.user.is_anonymous and request.user.role == User.MODERATOR:

            try:

                ModeratorTask.objects.get(user_who_added=request.user, media=media)

                return True

            except ModeratorTask.DoesNotExist:
                return False

        else:
            return False

    def get(self, request, media_id: int):

        media = self.get_media(media_id)

        if not media:
            return render(request, self.not_found_template_name)

        if request.user.is_anonymous:
            user_role = None

        else:
            user_role = request.user.role

        is_user_moderator = user_role == User.MODERATOR

        is_moderate = self.is_moderate(request, media)

        if media.active != Media.ACTIVE and not is_user_moderator:
            return render(request, self.no_permission_template_name)

        elif media.active != Media.ACTIVE and is_user_moderator and not is_moderate:
            return render(request, self.no_permission_template_name)

        return render(request, self.template_name, {'media': media, 'is_moderate': is_moderate})

    def post(self, request, media_id: int):

        if not request.user.is_authenticated:
            return render(request, self.no_permission_template_name)

        # ajax, download file:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.POST.get('request_type') == 'download_file':

            media = self.get_media(media_id)

            if not media:
                return render(request, self.not_found_template_name)

            try:
                MediaDownload.objects.create(media=media, user_who_added=request.user)

            except ValidationError:
                pass

            return HttpResponse(
                dumps({'downloads_number': media.get_downloads_number()}),
                content_type='application/json',
            )

        else:
            return ViewModeratorPage.post_from_view_page(request, self.get_media(media_id))
