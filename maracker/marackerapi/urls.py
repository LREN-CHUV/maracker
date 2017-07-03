from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import ApplicationCreateView, ApplicationDetailsView

urlpatterns = {
    url(r'^apps/?$', ApplicationCreateView.as_view(), name="maracker.create"),
    url(r'^apps/(?P<pk>[0-9]+)/?$',
        ApplicationDetailsView.as_view(),
        name="maracker.details"),
    #     url(r'^dockerapps/?$',
    #         DockerAppCreateView.as_view(),
    #         name="docker_app.create"),
    #     url(r'^dockerapps/(?P<pk>[0-9]+)/?$',
    #         DockerAppDetailsView.as_view(),
    #         name="docker_app.details")
}

urlpatterns = format_suffix_patterns(urlpatterns)
