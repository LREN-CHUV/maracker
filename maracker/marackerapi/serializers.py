from rest_framework import serializers
from .models import MarackerApplication, DockerContainer


class DockerContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockerContainer
        fields = ('id', 'image', 'ports')


class MarackerApplicationSerializer(serializers.ModelSerializer):
    docker_container = DockerContainerSerializer(required=False)

    class Meta:
        model = MarackerApplication
        fields = ('id', 'name', 'description', 'command', 'vcs_url', 'slug',
                  'docker_container')

    def create(self, validated_data):
        container_data = validated_data.get('docker_container', None)
        container = None

        if container_data:
            container = DockerContainer.objects.create(**container_data)
        # heModel._meta.get_field('field_name')
        marackerapp = MarackerApplication(
            name=validated_data.get(
                'name',
                MarackerApplication._meta.get_field('name').get_default()),
            description=validated_data.get('description', None),
            command=validated_data.get(
                'command',
                MarackerApplication._meta.get_field('name').get_default()),
            vcs_url=validated_data.get('vcs_url', ''), )

        if container_data:
            marackerapp.docker_container = container

        marackerapp.save()

        return marackerapp


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
