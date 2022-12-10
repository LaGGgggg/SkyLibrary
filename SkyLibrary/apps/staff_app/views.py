from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction

from json import dumps

from .models import ModeratorTask
from media_app.models import Media


User = get_user_model()


class ViewModeratorPage(LoginRequiredMixin, View):

    template_name: str = 'staff_app/moderator_page.html'
    no_permission_template_name: str = 'errors/403.html'

    def get(self, request):

        if request.user.role != User.MODERATOR:
            return render(request, self.no_permission_template_name)

        try:
            moderator_task = ModeratorTask.objects.get(user_who_added=request.user).media

        except ModeratorTask.DoesNotExist:
            moderator_task = None

        return render(request, self.template_name, {'moderator_task': moderator_task})

    @staticmethod
    def get_moderator_task(request) -> str | None:

        moderator_task_media = Media.objects.filter(active=0).order_by('pub_date')[:1]

        if moderator_task_media:

            moderator_task_media = moderator_task_media[0]

            ModeratorTask.objects.create(
                user_who_added=request.user,
                media=moderator_task_media,
            )

            moderator_task = f'<a href="{reverse("view_media", kwargs={"media_id": moderator_task_media.id})}"' \
                             f' class="h4 font-italic">{moderator_task_media.title}</a>'

        else:
            moderator_task = None

        return moderator_task

    def post(self, request):

        if request.user.role != User.MODERATOR:
            return render(request, self.no_permission_template_name)

        # ajax, get task
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            moderator_task = self.get_moderator_task(request)

            return HttpResponse(
                dumps({'moderator_task': moderator_task}),
                content_type='application/json',
            )

    @transaction.atomic
    def post_from_view_page(self, request, media: Media):

        if request.user.role != User.MODERATOR:
            return render(request, self.no_permission_template_name)

        ModeratorTask.objects.get(user_who_added=request.user, media=media).delete()

        if request.POST.get('is_approve_radio') == 'approve':
            media.active = Media.ACTIVE

        elif request.POST.get('is_approve_radio') == 'disapprove':
            media.active = Media.NOT_VALID

        media.save()

        if request.POST.get('is_auto_next_task') == 'true':
            moderator_task = self.get_moderator_task(request)

        else:
            moderator_task = None

        return redirect(reverse('moderator_page'), {'moderator_task': moderator_task})
