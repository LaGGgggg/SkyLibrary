from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .forms import SignUpForm


class SignUpView(CreateView):

    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'accounts_app/sign_up.html'


@login_required()
def view_profile(request):
    return render(request, 'accounts_app/profile.html')
