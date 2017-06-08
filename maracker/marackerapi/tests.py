from django.test import TestCase
from .services import MicrobadgerService


class MicrobadgerTestCase(TestCase):
    fixtures = ["marackerapi/fixtures/marackerapi.yaml"]

    def setUp(self):
        pass

    def test_service_can_fetch_data_and_create_model(self):
        namespace, image_name = "hbpmip", "portal-backend"
        microbadger_data = MicrobadgerService.get_docker_metadata(
            namespace, image_name)
        self.assertIsNotNone(microbadger_data)
        self.assertEqual(microbadger_data.image_name,
                         "/".join([namespace, image_name]))

    def test_service_handle_non_existent_image(self):
        microbadger_data = MicrobadgerService.get_docker_metadata(
            'toto', 'portal-backend')
        self.assertIsNone(microbadger_data)

    def test_service_handle_unexpected_values(self):
        microbadger_data = MicrobadgerService.get_docker_metadata(None, None)
        self.assertIsNone(microbadger_data)
