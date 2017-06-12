from django.conf.urls import url

from .views import github_webhook_receiver
from .views import gitlab_webhook_receiver

urlpatterns = [
    url(r'^github$', github_webhook_receiver, name='github'),
    url(r'^gitlab$', gitlab_webhook_receiver, name='gitlab'),
]
