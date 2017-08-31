from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (ApplicationCreateView, ApplicationDetailsView,
                    ApplicationSlugView, DockerDetailsView,
                    MarathonDetailsView, deploy, delete)
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

schema_view = get_schema_view(
        title='Maracker API', renderer_classes=[
            OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = {
    url(r'^apps/?$', ApplicationCreateView.as_view(), name="maracker.create"),
    url(r'^apps/(?P<pk>[0-9]+)/?$',
        ApplicationDetailsView.as_view(),
        name="maracker.details"),
    url(r'^apps/(?P<name>[-A-Za-z]+)/?$',
        ApplicationSlugView.as_view(),
        name="maracker.details-slug"),
    url(r'^container/docker/(?P<pk>[0-9]+)/?$',
        DockerDetailsView.as_view(),
        name="maracker.docker"),
    url(r'^marathon-config/(?P<pk>[0-9]+)/?$',
        MarathonDetailsView.as_view(),
        name="maracker.marathon"),
    url(r'^deploy/(?P<config_id>[0-9]+)/?$',
        deploy,
        name="maracker.deploy"),
    url(r'^delete/(?P<config_id>[0-9]+)/?$',
        delete,
        name="maracker.delete"),
    url(r'^$', schema_view, name='doc'),
}

urlpatterns = format_suffix_patterns(urlpatterns)
