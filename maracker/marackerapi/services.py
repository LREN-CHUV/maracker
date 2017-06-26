import requests
import json
from django.conf import settings
from django.template.loader import render_to_string


class MicrobadgerService:
    api_url = "https://api.microbadger.com"
    details_url = api_url + "/v1/images/{}/{}"

    @staticmethod
    def get_docker_metadata(namespace, name):
        url = MicrobadgerService.details_url.format(namespace, name)
        response = requests.get(url)
        try:
            return MicrobadgerMetadata(response.json())
            # metadata = response.json()
            # labels = metadata["Labels"]
            # return MipApplication(docker_name=metadata["ImageName"],
            #         description=labels["org.label-schema.description"],
            #         cpu=0.1,
            #         memory=labels["org.label-schema.memory-hint"])
        except json.decoder.JSONDecodeError:
            return None


class MicrobadgerMetadata:
    def __init__(self, docker_meta):
        labels = docker_meta["Labels"]
        self.image_name = docker_meta["ImageName"]
        self.image_url = docker_meta["ImageURL"]
        self.author = docker_meta["Author"]
        self.description = labels["org.label-schema.description"]
        self.memory = labels["org.label-schema.memory-hint"]


class MarathonService:
    api_url = settings.MARATHON['URL']

    @staticmethod
    def test_me(app, marathon_config):
        # print(MarathonService.api_url)
        json_text = render_to_string('cmd-application.txt', {
            'app': app,
            'marathon_config': marathon_config
        })
        # print(json_text)
        json_obj = json.loads(json_text)
        print(json_obj)
