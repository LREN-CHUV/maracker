from rest_framework import generics
from .serializers import MipApplicationSerializer
from .models import MipApplication


class CreateView(generics.ListCreateAPIView):
    """Create behavior of the API."""
    queryset = MipApplication.objects.all()
    serializer_class = MipApplicationSerializer

    def perform_create(self, serializer):
        """Create a new MipApplication entry into the database."""
        serializer.save()


class DetailsView(generics.RetrieveUpdateDestroyAPIView):
    """Handles the http GET, PUT and DELETE requests."""

    queryset = MipApplication.objects.all()
    serializer_class = MipApplicationSerializer
