"""
GitMate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import logout
from django.contrib.staticfiles.views import serve as serve_static
from django.views.decorators.csrf import ensure_csrf_cookie

from coala_online.views import coala_online

urlpatterns = [
    url(r'^$', ensure_csrf_cookie(serve_static),
        kwargs={'path': 'index.html'}),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('social_django.urls', namespace='auth')),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^api/', include('gitmate_config.urls', namespace='api')),
    url(r'^docs/', include('rest_framework_docs.urls', namespace='docs')),
    url(r'^webhooks/', include('gitmate_hooks.urls', namespace='webhooks')),
    url(r'^logout/', logout,
        {'next_page': settings.SOCIAL_AUTH_LOGOUT_REDIRECT_URL}),
    url(r'^coala_online/', coala_online),
    # catch-all pattern for Angular routes. This must be last in the list.
    url(r'^(?P<path>.*)/$', ensure_csrf_cookie(serve_static),
        kwargs={'path': 'index.html'}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
