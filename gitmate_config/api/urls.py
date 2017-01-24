from django.conf.urls import include
from django.conf.urls import url

from .views import UserDetailsView

urlpatterns = [
    url(r'^me/', UserDetailsView.as_view())
]
