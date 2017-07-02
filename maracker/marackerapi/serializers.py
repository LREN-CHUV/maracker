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
        fields = ('id', 'name', 'description', 'command', 'vcs_url', 'slug',
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


# class MarathonDockerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MarathonDocker
#         fields = ('id', 'cpu', 'memory', 'args', 'ports', 'env_vars')
#
#
# class DockerAppSerializer(serializers.ModelSerializer):
#     marathon_docker = MarathonDockerSerializer(
#         source='marathondocker_set', many=True, required=False)
#
#     class Meta:
#         model = DockerApp
#         fields = ('id', 'name', 'description', 'namespace', 'image', 'vcs_url',
#                   'marathon_docker')
#
#     def create(self, validated_data):
#         marathon_configs_data = validated_data.get('marathondocker_set', [])
#         docker_application = DockerApp.objects.create(
#             name=validated_data['name'],
#             description=validated_data['description'],
#             namespace=validated_data['namespace'],
#             image=validated_data['image'])
#
#         for conf_data in marathon_configs_data:
#             MarathonDocker.objects.create(
#                 docker_app=docker_application, **conf_data)
#
#         return docker_application
#
#
# class CmdAppSerializer(serializers.ModelSerializer):
#     marathon_cmd = MarathonCmdSerializer(
#         source='marathoncmd_set', many=True, required=False)
#
#     class Meta:
#         model = CmdApp
#         fields = ('id', 'name', 'description', 'command', 'vcs_url',
#                   'marathon_cmd', )
#
#     def create(self, validated_data):
#         marathon_configs_data = validated_data.get('marathoncmd_set', [])
#         cmd_application = CmdApp.objects.create(
#             name=validated_data['name'],
#             description=validated_data['description'],
#             command=validated_data['command'])
#
#         for conf_data in marathon_configs_data:
#             MarathonCmd.objects.create(cmd_app=cmd_application, **conf_data)
#
#         return cmd_application
#
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.description = validated_data.get('description',
#                                                   instance.description)
#         instance.command = validated_data.get('command', instance.command)
#         instance.vcs_url = validated_data.get('vcs_url', instance.vcs_url)
#         instance.save()
#
#         if validated_data.get('marathoncmd_set', None) is not None:
#             instance.marathoncmd_set.all().delete()
#             for conf in validated_data.get('marathoncmd_set', []):
#                 MarathonCmd.objects.create(cmd_app=instance, **conf)
#
#         return instance
