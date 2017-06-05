from rest_framework import serializers
from .models import MipApplication

class MipApplicationSerializer(serializers.ModelSerializer):
    """ Serializer to map the Model instance into JSON format. """

    class Meta:
        """ Meta class to map serializer's fields with the model fields. """
        model = MipApplication
        fields = ('id', 'docker_name', 'description', 'cpu', 'memory')
        # read_only_fields = ()
