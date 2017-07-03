import requests
import json
from django.conf import settings

microbadger_url = "https://api.microbadger.com"
microbadger_details = microbadger_url + "/v1/images/{}/{}"


def get_docker_metadata(namespace, name):
    url = microbadger_details.format(namespace, name)
    response = requests.get(url)
    try:
        return MicrobadgerMetadata(response.json())
    except json.decoder.JSONDecodeError:
        return None


class MicrobadgerMetadata:
    def __init__(self, docker_meta):
        labels = docker_meta.get("Labels", {})
        self.image_name = docker_meta.get("ImageName", None)
        self.image_url = docker_meta.get("ImageURL", None)
        self.author = docker_meta.get("Author", None)
        self.description = labels.get("org.label-schema.description", None)
        self.memory = labels.get("org.label-schema.memory-hint", None)


class MarathonService:
    api_url = settings.MARATHON["URL"]
    deploy_url = api_url + "/v2/apps"
    delete_url = deploy_url + "/{}"

    @staticmethod
    def deploy_cmd_app(app, marathon_config, instances=1):
        marathon_data = {
            "id": MarathonService.marathon_name(app),
            "cmd": app.command,
            "cpus": float(marathon_config.cpu),
            "mem": marathon_config.memory,
            "instancer": instances,
        }
        if marathon_config.args:
            marathon_data["cmd"] += " {}".format(marathon_config.args)

        if marathon_config.env_vars:
            marathon_data["env"] = {
                k: v
                for k, v in marathon_config.env_vars.items()
            }

        response = requests.post(
            MarathonService.deploy_url, json=marathon_data)

        return response

    @staticmethod
    def deploy_docker_app(app, marathon_config, instances=1):
        marathon_data = {
            "id": MarathonService.marathon_name(app),
            "cpus": float(marathon_config.cpu),
            "mem": marathon_config.memory,
            "instances": 1,
            "container": {
                "type": "DOCKER",
                "docker": {
                    "image": "{app.namespace}/{app.image}".format(app=app),
                    "network": "BRIDGE",
                    "forcePullImage": False,
                },
            }
        }
        if marathon_config.ports:
            marathon_data["container"]["docker"]["portMappings"] = [{
                "containerPort":
                p,
                "hostPort":
                0
            } for p in marathon_config.ports]

        if marathon_config.env_vars:
            marathon_data["env"] = {
                k: v
                for k, v in marathon_config.env_vars.items()
            }

        response = requests.post(
            MarathonService.deploy_url, json=marathon_data)

        return response

    @staticmethod
    def marathon_name(app):
        return "{app.name}.{app.id}".format(app=app)

    @staticmethod
    def delete_app(app, marathon_config):
        response = requests.delete(
            MarathonService.delete_url.format(
                MarathonService.marathon_name(app)))

        return response
