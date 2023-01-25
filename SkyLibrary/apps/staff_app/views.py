from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.db import transaction

from json import dumps

from .models import ModeratorTask
from media_app.models import Media
from home_page_app.views import handler403, handler404


User = get_user_model()


class ViewModeratorPage(LoginRequiredMixin, View):

    template_name: str = 'staff_app/moderator_page.html'

    def get(self, request, get_next_task: str, from_view_media_page: str):

        if request.user.role != User.MODERATOR:
            return handler403(request)

        try:
            moderator_task = ModeratorTask.objects.get(user_who_added=request.user).media

        except ModeratorTask.DoesNotExist:

            if get_next_task == 'true' and from_view_media_page == 'true':

                moderator_task_media = Media.objects.filter(active=Media.INACTIVE).order_by('pub_date')[:1]

                if moderator_task_media:

                    moderator_task_media = moderator_task_media[0]

                    ModeratorTask.objects.create(
                        user_who_added=request.user,
                        media=moderator_task_media,
                    )

                    moderator_task = moderator_task_media

                else:
                    moderator_task = None

            else:
                moderator_task = None

        return render(
            request,
            self.template_name,
            {
                'moderator_task': moderator_task,
                'from_view_media_page': from_view_media_page,
                'get_next_task': get_next_task,
            },
        )

    @staticmethod
    def get_moderator_task_tag(request) -> str | None:

        try:
            moderator_task_media = ModeratorTask.objects.get(user_who_added=request.user).media

        except ModeratorTask.DoesNotExist:

            moderator_task_media = Media.objects.filter(active=Media.INACTIVE).order_by('pub_date')[:1]

            if moderator_task_media:

                moderator_task_media = moderator_task_media[0]

                ModeratorTask.objects.create(
                    user_who_added=request.user,
                    media=moderator_task_media,
                )

            else:
                return None

        moderator_task = f'<a href="{reverse("view_media", kwargs={"media_id": moderator_task_media.id})}"' \
                         f' class="h4 font-italic">{moderator_task_media.title}</a>'

        return moderator_task

    def post(self, request, **_):

        if request.user.role != User.MODERATOR:
            return handler403(request)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            moderator_task = self.get_moderator_task_tag(request)

            return HttpResponse(
                dumps({'moderator_task': moderator_task}),
                content_type='application/json',
            )

        else:
            return handler404(request)

    @transaction.atomic
    def post_from_view_page(self, request, media: Media):

        if request.user.role != User.MODERATOR:
            return handler403(request)

        ModeratorTask.objects.get(user_who_added=request.user, media=media).delete()

        if request.POST.get('is_approve_radio') == 'approve':
            media.active = Media.ACTIVE

        elif request.POST.get('is_approve_radio') == 'disapprove':
            media.active = Media.NOT_VALID

        media.save()

        get_next_task: bool = request.POST.get('is_auto_next_task').lower()

        return redirect(
            reverse('moderator_page', kwargs={'get_next_task': get_next_task, 'from_view_media_page': 'true'})
        )
