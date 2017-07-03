import requests
import json
from django.conf import settings
from rest_framework import status

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


marathon_url = settings.MARATHON["URL"]
marathon_deploy = marathon_url + "/v2/apps"
marathon_delete = marathon_deploy + "/{}"


def deploy_on_marathon(app, marathon_config, instances=1):
    marathon_data = {
        "id": get_marathon_name(app, marathon_config),
        # "cmd": app.command,
        "cpus": float(marathon_config.cpu),
        "mem": marathon_config.memory,
        "instances": instances,
    }

    if not app.docker_container:
        if app.command:
            marathon_data["cmd"] = app.command
        if marathon_config.args:
            marathon_data["cmd"] = " {}".format(marathon_config.args)

    elif app.docker_container is not None:
        marathon_data["container"] = {
            "type": "DOCKER",
            "docker": {
                "image": "{}".format(app.docker_container.image),
                "network": "BRIDGE",
                "forcePullImage": False,
            },
        }
        if app.command:
            marathon_data["cmd"] = app.command

            if marathon_config.args:
                marathon_data["cmd"] += " {}".format(marathon_config.args)

        elif marathon_config.args:
            marathon_data["args"] = marathon_config.args

        if app.docker_container.ports:
            marathon_data["container"]["docker"]["portMappings"] = [{
                "containerPort":
                p,
                "hostPort":
                0
            } for p in app.docker_container.ports]

    if marathon_config.env_vars:
        marathon_data["env"] = {
            k: v
            for k, v in marathon_config.env_vars.items()
        }

    response = requests.post(marathon_deploy, json=marathon_data)

    if response.status_code != status.HTTP_201_CREATED:
        return None

    return response


def delete_from_marathon(app, marathon_config):
    response = requests.delete(
        marathon_delete.format(get_marathon_name(app, marathon_config)))

    if response.status_code != status.HTTP_200_OK:
        return None

    return response


def get_marathon_name(app, marathon_conf):
    return "{}.{}".format(app.name, marathon_conf.id)
