from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import MarackerApplicationSerializer
from .serializers import DockerContainerSerializer, MarathonConfigSerializer
from .models import MarackerApplication, DockerContainer, MarathonConfig
from .services import MarathonService
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


class ApplicationCreateView(generics.ListCreateAPIView):
    queryset = MarackerApplication.objects.all()
    serializer_class = MarackerApplicationSerializer

    def perform_create(self, serializer):
        serializer.save()


class ApplicationDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MarackerApplication.objects.all()
    serializer_class = MarackerApplicationSerializer


class ApplicationSlugView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MarackerApplication.objects.all()
    serializer_class = MarackerApplicationSerializer
    lookup_field = "name"


class DockerDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DockerContainer.objects.all()
    serializer_class = DockerContainerSerializer


class MarathonDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MarathonConfig.objects.all()
    serializer_class = MarathonConfigSerializer


@csrf_exempt
@api_view(['POST'])
def deploy(request, config_id):
    config = get_object_or_404(MarathonConfig, pk=config_id)
    service = MarathonService(settings.MARATHON["URL"])
    service.deploy(config)
    serializer = MarathonConfigSerializer(config)
    return Response(serializer.data, status.HTTP_200_OK)
