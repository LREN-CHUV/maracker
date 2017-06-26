from rest_framework import generics
from .serializers import CmdAppSerializer, DockerAppSerializer
from .models import CmdApp, DockerApp


class CmdAppCreateView(generics.ListCreateAPIView):
    queryset = CmdApp.objects.all()
    serializer_class = CmdAppSerializer

    def perform_create(self, serializer):
        serializer.save()


class CmdAppDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CmdApp.objects.all()
    serializer_class = CmdAppSerializer


class DockerAppCreateView(generics.ListCreateAPIView):
    queryset = DockerApp.objects.all()
    serializer_class = DockerAppSerializer

    def perform_create(self, serializer):
        serializer.save()


class DockerAppDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DockerApp.objects.all()
    serializer_class = DockerAppSerializer
