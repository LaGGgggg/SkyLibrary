from django.shortcuts import render
from django.views import View

from media_app.models import Media, get_best_active_media
from accounts_app.models import User


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

    def get(self, request):

        recent_media = Media.objects.filter(active=1).order_by('pub_date')[:5]
        best_media = get_best_active_media(amount=5)

        response_data: dict = {
            'recent_media': recent_media,
            'best_media': best_media,
            'is_user_moderator': request.user.role == User.MODERATOR if request.user.is_authenticated else 0,
        }

        return render(request, self.template_name, response_data)
