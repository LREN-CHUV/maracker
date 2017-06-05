from django.test import TestCase
from .services import MicrobadgerService


class MicrobadgerTestCase(TestCase):
    def setUp(self):
        pass

    def test_service_can_fetch_data_and_create_model(self):
        microbadger_data = MicrobadgerService.get_docker_metadata(
            'hbpmip', 'portal-backend')
        # print("Retrieved data:")
        # print(microbadger_data.__dict__)
        self.assertIsNotNone(microbadger_data)

    def test_service_handle_non_existent_image(self):
        microbadger_data = MicrobadgerService.get_docker_metadata(
            'toto', 'portal-backend')
        self.assertIsNone(microbadger_data)
