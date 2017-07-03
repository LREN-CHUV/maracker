from rest_framework import generics
from .serializers import MarackerApplicationSerializer
from .serializers import DockerContainerSerializer, MarathonConfigSerializer
from .models import MarackerApplication, DockerContainer, MarathonConfig


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
