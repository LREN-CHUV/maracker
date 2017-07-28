from rest_framework import serializers
from .models import MarackerApplication, DockerContainer, MarathonConfig


class DockerContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockerContainer
        fields = ('id', 'image', 'ports')


class MarathonConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarathonConfig
        fields = ('id', 'cpu', 'memory', 'args', 'env_vars')


class MarackerApplicationSerializer(serializers.ModelSerializer):
    docker_container = DockerContainerSerializer(required=False)
    marathon_configs = MarathonConfigSerializer(
        source='marathonconfig_set', many=True, required=False)

    class Meta:
        model = MarackerApplication
        fields = ('id', 'name', 'description', 'command', 'vcs_url',
                  'docker_container', 'marathon_configs')

    def create(self, validated_data):
        container_data = validated_data.get('docker_container', None)
        container = None

        if container_data:
            container = DockerContainer.objects.create(**container_data)

        marackerapp = MarackerApplication(
            name=validated_data.get(
                'name',
                MarackerApplication._meta.get_field('name').get_default()),
            description=validated_data.get(
                'description',
                MarackerApplication._meta.get_field('description')),
            command=validated_data.get(
                'command',
                MarackerApplication._meta.get_field('command').get_default()),
            vcs_url=validated_data.get('vcs_url', ''), )

        if container_data:
            marackerapp.docker_container = container

        marackerapp.save()
        marathon_configs = validated_data.get('marathonconfig_set', [])

        for config in marathon_configs:
            MarathonConfig.objects.create(
                cpu=config.get(
                    'cpu',
                    MarathonConfig._meta.get_field('cpu').get_default()),
                memory=config.get(
                    'memory',
                    MarathonConfig._meta.get_field('memory').get_default()),
                args=config.get(
                    'args',
                    MarathonConfig._meta.get_field('args').get_default()),
                env_vars=config.get(
                    'env_vars',
                    MarathonConfig._meta.get_field('env_vars').get_default()),
                maracker_app=marackerapp, )

        return marackerapp

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description',
                                                  instance.description)
        instance.command = validated_data.get('command', instance.command)
        instance.vcs_url = validated_data.get('vcs_url', instance.vcs_url)

        container_data = validated_data.get('docker_container', None)

        # If a new container or new marathon configurations are pushed
        # the old ones are deleted and replaced the ones pushed
        # by the user.
        if container_data:
            container = DockerContainer.objects.create(**container_data)
            instance.docker_container.delete()
            instance.docker_container = container

        instance.save()

        if validated_data.get('marathonconfig_set', None):
            instance.marathonconfig_set.all().delete()

            for conf in validated_data.get('marathonconfig_set', []):
                MarathonConfig.objects.create(maracker_app=instance, **conf)

        return instance
