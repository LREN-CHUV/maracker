from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import MarackerApplicationCreateView

urlpatterns = {
    url(r'^cmdapps/?$', MarackerApplicationCreateView.as_view(), name="maracker.create"),
    #     url(r'^cmdapps/(?P<pk>[0-9]+)/?$',
    #         CmdAppDetailsView.as_view(),
    #         name="cmd_app.details"),
    #     url(r'^dockerapps/?$',
    #         DockerAppCreateView.as_view(),
    #         name="docker_app.create"),
    #     url(r'^dockerapps/(?P<pk>[0-9]+)/?$',
    #         DockerAppDetailsView.as_view(),
    #         name="docker_app.details")
}

urlpatterns = format_suffix_patterns(urlpatterns)
