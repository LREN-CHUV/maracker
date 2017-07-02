from rest_framework import generics
from .serializers import MarackerApplicationSerializer
from .models import MarackerApplication


class MarackerApplicationCreateView(generics.ListCreateAPIView):
    queryset = MarackerApplication.objects.all()
    serializer_class = MarackerApplicationSerializer

    def perform_create(self, serializer):
        serializer.save()


class MarackerApplicationDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MarackerApplication.objects.all()
    serializer_class = MarackerApplicationSerializer
