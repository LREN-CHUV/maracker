import requests
import json
from marathon import MarathonClient
from marathon.models.app import MarathonApp
from marathon.models.container import (MarathonContainer,
                                       MarathonDockerContainer,
                                       MarathonContainerPortMapping)
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
        self.client = MarathonClient(url)

    def deploy(self, marathon_config, instances=1):
        marathon_app = MarathonApp(
            id=self.get_marathon_name(marathon_config),
            cpus=float(marathon_config.cpu),
            mem=marathon_config.memory,
            instances=instances)

        maracker_app = marathon_config.maracker_app

        if not maracker_app.docker_container:
            if maracker_app.command:
                marathon_app.cmd = maracker_app.command
            if marathon_config.args:
                marathon_app.cmd += f"{marathon_config.agrs}"

        elif maracker_app.docker_container:
            docker = MarathonDockerContainer(
                image=maracker_app.docker_container.image,
                network="BRIDGE",
                force_pull_image=False)

            if maracker_app.command:
                marathon_app.cmd = maracker_app.command

                if maracker_app.args:
                    marathon_app.cmd += f" {marathon_config.args}"
            elif marathon_config.args:
                marathon_app.args = marathon_config.args
            if maracker_app.docker_container.ports:
                docker.port_mappings = [
                        MarathonContainerPortMapping(
                            container_port=port, host_port=0)
                        for port in maracker_app.docker_container.ports]
                marathon_app.labels = {
                    "traefik.frontend.rule":
                    (f"Host:{maracker_app.name}{marathon_config.id}"
                     ".marathon.localhost"),
                    "traefik.backend":
                    f"{maracker_app.name}{marathon_config.id}"
                }
            marathon_app.container = MarathonContainer(docker=docker)

        if marathon_config.env_vars:
            marathon_app.env = copy(marathon_config.env_vars)

        deployed_app = self.client.create_app(
            f"{maracker_app.name}.{marathon_config.id}", marathon_app)

        return deployed_app

    def delete(self, marathon_config, force=True):
        deployment = self.client.delete_app(
            self.get_marathon_name(marathon_config), force)

        return deployment

    def get_marathon_name(self, marathon_conf):
        return f"{marathon_conf.maracker_app.name}.{marathon_conf.id}"
