from django.conf.urls import url

from .views import github_webhook_receiver

urlpatterns = [
    url(r'^github$', github_webhook_receiver),
]
