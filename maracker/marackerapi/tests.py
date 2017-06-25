from django.test import TestCase
from .services import MicrobadgerService
from .models import CmdApp, MarathonCmd
from rest_framework.test import APIClient
from rest_framework import status
from django.core.urlresolvers import reverse


class MicrobadgerTestCase(TestCase):
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


class CmdAppTestCase(TestCase):
    # fixtures = ["marackerapi/fixtures/marackerapi.yaml"]

    def setUp(self):
        self.cmd_app = CmdApp(
            name="sleepy command",
            description="My first cmd app",
            command="sleep 7324")

    def test_app_creation_and_marathon_conf_creation(self):
        before_count = CmdApp.objects.count()
        self.cmd_app.save()
        after_count = CmdApp.objects.count()
        self.assertNotEqual(before_count, after_count)
        before_count = MarathonCmd.objects.count()
        marathon_cmd = MarathonCmd(cpu=0.3, memory=128, cmd_app=self.cmd_app)
        marathon_cmd.save()
        after_count = MarathonCmd.objects.count()
        self.assertNotEqual(before_count, after_count)


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cmd_app_data = {
            "name": "My cmd app",
            "description": "be careful it's dangerous",
            "command": "env"
        }
        self.cmd_app_with_marathon = {
            "name": "Cmd command with its marathon configuration",
            "description": "Just to test nested relationships",
            "command": "echo 'hello'",
            "marathon_cmd": [{
                "cpu": 0.6,
                "memory": 256
            }]
        }

    def test_api_can_create_cmd_app(self):
        response = self.client.post(
            reverse("cmd_app.create"), self.cmd_app_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_can_create_cmd_app_with_marathon_config(self):
        response = self.client.post(
            reverse("cmd_app.create"),
            self.cmd_app_with_marathon,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cmd_app = CmdApp.objects.get(pk=response.data["id"])
        self.assertTrue(cmd_app.marathoncmd_set.all())
