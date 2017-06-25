from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CmdAppCreateView, CmdAppDetailsView

urlpatterns = {
    url(r'^cmdapps/?$', CmdAppCreateView.as_view(), name="cmd_app.create"),
    url(r'^cmdapps/(?P<pk>[0-9]+)/?$',
        CmdAppDetailsView.as_view(),
        name="cmd_app.details")
}

urlpatterns = format_suffix_patterns(urlpatterns)
