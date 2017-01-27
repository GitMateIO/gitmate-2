from django.conf.urls import include
from django.conf.urls import url

from .views import UserDetailsView
from .views import UserOwnedRepositoriesView

urlpatterns = [
    url(r'^me/', UserDetailsView.as_view()),
    url(r'^repos/?', UserOwnedRepositoriesView.as_view())
]
