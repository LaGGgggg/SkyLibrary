from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import Media, MediaRating, MediaDownload
from .forms import CreateMediaForm


class ViewCreateMedia(LoginRequiredMixin, CreateView):

    form_class = CreateMediaForm
    model = Media
    template_name = 'media_app/create_media.html'
    success_url = reverse_lazy('create_media_successful')

    def form_valid(self, form):

        form.instance.user_who_added = self.request.user

        return super().form_valid(form)
