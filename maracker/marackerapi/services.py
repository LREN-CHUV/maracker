import requests
import json
from rest_framework import status
from copy import copy


def get_docker_metadata(namespace, name):
    api_url = "https://api.microbadger.com"
    details_url = api_url + "/v1/images/{}/{}"

    url = details_url.format(namespace, name)
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
    def __init__(self, url):
        self.url = url
        self.deploy_url = self.url + "/v2/apps"
        self.delete_url = self.deploy_url + "/{}"

    def deploy_on_marathon(self, marathon_config, instances=1):

        marathon_data = {
            "id": self.get_marathon_name(marathon_config),
            # "cmd": app.command,
            "cpus": float(marathon_config.cpu),
            "mem": marathon_config.memory,
            "instances": instances,
        }

        app = marathon_config.maracker_app

        if not app.docker_container:
            if app.command:
                marathon_data["cmd"] = app.command
            if marathon_config.args:
                marathon_data["cmd"] = f" {marathon_config.args}"

        elif app.docker_container is not None:
            marathon_data["container"] = {
                "type": "DOCKER",
                "docker": {
                    "image": f"{app.docker_container.image}",
                    "network": "BRIDGE",
                    "forcePullImage": False,
                },
            }
            if app.command:
                marathon_data["cmd"] = app.command

                if marathon_config.args:
                    marathon_data["cmd"] += f" {marathon_config.args}"

            elif marathon_config.args:
                marathon_data["args"] = marathon_config.args

            if app.docker_container.ports:
                marathon_data["container"]["docker"]["portMappings"] = [{
                    "containerPort":
                    p,
                    "hostPort":
                    0
                } for p in app.docker_container.ports]
                marathon_data["labels"] = {
                    "traefik.frontend.rule":
                    f"Host:{app.name}{marathon_config.id}.marathon.localhost",
                    "traefik.backend":
                    f"{app.name}{marathon_config.id}"
                }

        if marathon_config.env_vars:
            marathon_data["env"] = copy(marathon_config.env_vars)

        response = requests.post(self.deploy_url, json=marathon_data)

        if response.status_code != status.HTTP_201_CREATED:
            raise Exception(response.json()["message"])

        return response

    def delete_from_marathon(self, marathon_config):
        response = requests.delete(
            self.delete_url.format(self.get_marathon_name(marathon_config)))

        if response.status_code != status.HTTP_200_OK:
            raise Exception(response.json()["message"])

        return response

    def get_marathon_name(self, marathon_conf):
        return f"{marathon_conf.maracker_app.name}.{marathon_conf.id}"
