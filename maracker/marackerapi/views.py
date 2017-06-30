from rest_framework import generics
from .serializers import MarackerApplicationSerializer
from .models import MarackerApplication


class MarackerApplicationCreateView(generics.ListCreateAPIView):
    queryset = MarackerApplication.objects.all()
    serializer_class = MarackerApplicationSerializer

    def perform_create(self, serializer):
        serializer.save()


# class CmdAppDetailsView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = CmdApp.objects.all()
#     serializer_class = CmdAppSerializer
#
#
# class DockerAppCreateView(generics.ListCreateAPIView):
#     queryset = DockerApp.objects.all()
#     serializer_class = DockerAppSerializer
#
#     def perform_create(self, serializer):
#         serializer.save()
#
#
# class DockerAppDetailsView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = DockerApp.objects.all()
#     serializer_class = DockerAppSerializer
