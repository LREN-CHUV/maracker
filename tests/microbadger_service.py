import requests
import json

class MicrobadgerService:
    api_url = "https://api.microbadger.com"
    details_url = api_url + "/v1/images/{}/{}"

    @staticmethod
    def get_docker_metadata(namespace, name):
        url = MicrobadgerService.details_url.format(namespace, name)
        response = requests.get(url)
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            return None
