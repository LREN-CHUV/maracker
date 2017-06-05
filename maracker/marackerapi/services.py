import requests
import json
from .models import MipApplication

class MicrobadgerService:
    api_url = "https://api.microbadger.com"
    details_url = api_url + "/v1/images/{}/{}"

    @staticmethod
    def get_docker_metadata(namespace, name):
        url = MicrobadgerService.details_url.format(namespace, name)
        response = requests.get(url)
        try:
            # return MicrobadgerMetadata(response.json())
            metadata = response.json()
            labels = metadata["Labels"]
            return MipApplication(docker_name=metadata["ImageName"],
                    description=labels["org.label-schema.description"],
                    cpu=0.1,
                    memory=labels["org.label-schema.memory-hint"])
        except json.decoder.JSONDecodeError:
            return None

class MicrobadgerMetadata:
    def __init__(self, docker_meta):
        labels =  docker_meta["Labels"]
        self.image_name = docker_meta["ImageName"]
        self.image_url = docker_meta["ImageURL"]
        self.author= docker_meta["Author"]
        self.description = labels["org.label-schema.description"]
        self.memory = labels["org.label-schema.memory-hint"]
