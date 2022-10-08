"""SkyLibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog

from django_registration.backends.activation.views import RegistrationView

from accounts_app.forms import CustomSignUpForm

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),  # needed for correct js translation
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts_app.urls')),
    path(
        'accounts/register/',
        RegistrationView.as_view(form_class=CustomSignUpForm),
        name='django_registration_register',
    ),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('media/', include('media_app.urls')),
    path('', include('home_page_app.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'home_page_app.views.handler400'
handler403 = 'home_page_app.views.handler403'
handler404 = 'home_page_app.views.handler404'
handler500 = 'home_page_app.views.handler500'
