from rest_framework import serializers
from .models import MarathonCmd, CmdApp


class MarathonCmdSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarathonCmd
        fields = ('id', 'cpu', 'memory', 'args', 'env_vars')


class CmdAppSerializer(serializers.ModelSerializer):
    marathon_cmd = MarathonCmdSerializer(
        source='marathoncmd_set', many=True, required=False)

    class Meta:
        model = CmdApp
        fields = ('id', 'name', 'description', 'command', 'marathon_cmd')

    def create(self, validated_data):
        marathon_configs_data = validated_data.get('marathoncmd_set', [])
        cmd_application = CmdApp.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            command=validated_data['command'])

        for conf_data in marathon_configs_data:
            MarathonCmd.objects.create(cmd_app=cmd_application, **conf_data)

        return cmd_application
