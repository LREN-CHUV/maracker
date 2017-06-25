from rest_framework import generics
from .serializers import CmdAppSerializer
from .models import CmdApp


class CmdAppCreateView(generics.ListCreateAPIView):
    queryset = CmdApp.objects.all()
    serializer_class = CmdAppSerializer

    def perform_create(self, serializer):
        serializer.save()


class CmdAppDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CmdApp.objects.all()
    serializer_class = CmdAppSerializer
