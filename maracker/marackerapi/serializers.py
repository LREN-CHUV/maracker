from rest_framework import serializers
from .models import MarathonCmd, CmdApp, MarathonDocker, DockerApp


class MarathonCmdSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarathonCmd
        fields = ('id', 'cpu', 'memory', 'args', 'env_vars')


class MarathonDockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarathonDocker
        fields = ('id', 'cpu', 'memory', 'args', 'ports', 'env_vars')


class DockerAppSerializer(serializers.ModelSerializer):
    marathon_docker = MarathonDockerSerializer(
        source='marathondocker_set', many=True, required=False)

    class Meta:
        model = DockerApp
        fields = ('id', 'name', 'description', 'namespace', 'image', 'vcs_url',
                  'marathon_docker')

    def create(self, validated_data):
        marathon_configs_data = validated_data.get('marathondocker_set', [])
        docker_application = DockerApp.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            namespace=validated_data['namespace'],
            image=validated_data['image'])

        for conf_data in marathon_configs_data:
            MarathonDocker.objects.create(
                docker_app=docker_application, **conf_data)

        return docker_application


class CmdAppSerializer(serializers.ModelSerializer):
    marathon_cmd = MarathonCmdSerializer(
        source='marathoncmd_set', many=True, required=False)

    class Meta:
        model = CmdApp
        fields = ('id', 'name', 'description', 'command', 'vcs_url',
                  'marathon_cmd', )

    def create(self, validated_data):
        marathon_configs_data = validated_data.get('marathoncmd_set', [])
        cmd_application = CmdApp.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            command=validated_data['command'])

        for conf_data in marathon_configs_data:
            MarathonCmd.objects.create(cmd_app=cmd_application, **conf_data)

        return cmd_application
