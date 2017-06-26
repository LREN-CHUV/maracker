from django.test import TestCase
from .services import MicrobadgerService, MarathonService
from .models import CmdApp, MarathonCmd, DockerApp, MarathonDocker
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


class MarathonServiceTestCase(TestCase):
    fixtures = ["marackerapi/fixtures/marackerapi.yaml"]

    def setUp(self):
        self.cmd_app = CmdApp.objects.get(pk=1)

    def test_marathon_service(self):
        MarathonService.test_me(self.cmd_app,
                                self.cmd_app.marathoncmd_set.first())


class CmdAppTestCase(TestCase):
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


class DockerAppTestCase(TestCase):
    def setUp(self):
        self.docker_app = DockerApp(
            name="postgres",
            description="Simple postgres container",
            namespace="library",
            image="postgres")

    def test_app_creation_and_marathon_conf_creation(self):
        before_count = DockerApp.objects.count()
        self.docker_app.save()
        after_count = DockerApp.objects.count()
        self.assertNotEqual(before_count, after_count)
        before_count = MarathonDocker.objects.count()
        marathon_docker = MarathonDocker(
            cpu=0.3, memory=128, ports=[5432], docker_app=self.docker_app)
        marathon_docker.save()
        after_count = MarathonDocker.objects.count()
        self.assertNotEqual(before_count, after_count)


class APICmdAppTestCase(TestCase):
    fixtures = ["marackerapi/fixtures/marackerapi.yaml"]

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
            "vcs_url": "https://github.com/groovytron/maracker",
            "marathon_cmd": [
                {
                    "cpu": 0.6,
                    "memory": 256
                },
            ]
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

    def test_api_can_update_cmd_app(self):
        app = CmdApp.objects.get(pk=1)
        before_count = app.marathoncmd_set.count()

        # Test detail view and get JSON to update the model
        response = self.client.get(
            reverse("cmd_app.details", kwargs={'pk': app.id}))
        app_data = response.data
        app_data["name"] = "env"
        app_data["command"] = "env"
        app_data[
            "description"] = "Simple command showing environment variables"

        # Test PUT method (marathon configuration should not be overwritten)
        response = self.client.put(
            reverse("cmd_app.details", kwargs={'pk': app.id}),
            app_data,
            format="json")

        after_count = app.marathoncmd_set.count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(before_count, after_count)

    def test_api_can_overwrite_marathon_config(self):
        app = CmdApp.objects.get(pk=1)
        before_count = app.marathoncmd_set.count()

        # Test detail view and get JSON to update the model
        response = self.client.get(
            reverse("cmd_app.details", kwargs={'pk': app.id}))
        app_data = response.data
        app_data["name"] = "env"
        app_data["command"] = "env"
        app_data[
            "description"] = "Simple command showing environment variables"
        app_data["marathon_cmd"] = [
            {
                "cpu": 1.0,
                "memory": 32
            },
            {
                "cpu": 0.5,
                "memory": 64
            },
            {
                "cpu": 2.0,
                "memory": 1024
            },
        ]

        # Test PUT method (marathon configuration should be overwritten)
        response = self.client.put(
            reverse("cmd_app.details", kwargs={'pk': app.id}),
            app_data,
            format="json")

        after_count = app.marathoncmd_set.count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(before_count, after_count)


class APIDockerAppTestCase(TestCase):
    fixtures = ["marackerapi/fixtures/marackerapi.yaml"]

    def setUp(self):
        self.client = APIClient()
        self.docker_app_data = {
            "name": "postgres database container",
            "description": "container embedding postgreSQL database service",
            "namespace": "library",
            "image": "postgres"
        }
        self.docker_app_with_marathon = {
            "name":
            "nginx http server container",
            "description":
            "container embedding nginx http server and reverse proxy service",
            "namespace":
            "library",
            "image":
            "nginx",
            "vcs_url":
            "https://github.com/nginxinc/docker-nginx",
            "marathon_docker": [
                {
                    "cpu": 0.2,
                    "memory": 512,
                    "version": "latest",
                    "ports": [8080],
                    "env_vars": {
                        "NGINX_PORT": 8080,
                        "NGINX_HOST": "foobar.com"
                    }
                },
                {
                    "cpu": 0.1,
                    "memory": 32,
                    "version": "latest",
                    "ports": [80],
                    "env_vars": {
                        "NGINX_PORT": 80,
                        "NGINX_HOST": "example.com"
                    }
                },
            ]
        }

    def test_api_can_create_docker_app(self):
        response = self.client.post(
            reverse("docker_app.create"), self.docker_app_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_can_create_docker_app_with_marathon_config(self):
        response = self.client.post(
            reverse("docker_app.create"),
            self.docker_app_with_marathon,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        docker_app = DockerApp.objects.get(pk=response.data["id"])
        self.assertTrue(docker_app.marathondocker_set.all())

    def test_api_can_update_docker_app(self):
        app = DockerApp.objects.get(pk=2)
        before_count = app.marathondocker_set.count()

        # Test detail view and get JSON to update the model
        response = self.client.get(
            reverse("cmd_app.details", kwargs={'pk': app.id}))
        app_data = response.data
        app_data["name"] = "woken"
        app_data["namespace"] = "hbpmip"
        app_data["image"] = "woken"
        app_data["description"] = (
            "An orchestration platform for Docker containers"
            " running data mining algorithms.")

        # Test PUT method (marathon configuration should not be overwritten)
        response = self.client.put(
            reverse("docker_app.details", kwargs={'pk': app.id}),
            app_data,
            format="json")

        after_count = app.marathondocker_set.count()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(before_count, after_count)

    # def test_api_can_overwrite_marathon_config(self):
    #     app = DockerApp.objects.get(pk=2)
    #     before_count = app.marathondocker_set.count()

    #     # Test detail view and get JSON to update the model
    #     response = self.client.get(
    #         reverse("docker_app.details", kwargs={'pk': app.id}))
    #     app_data = response.data
    #     app_data["name"] = "woken"
    #     app_data["namespace"] = "hbpmip"
    #     app_data["image"] = "woken"
    #     app_data["description"] = (
    #         "An orchestration platform for Docker containers"
    #         " running data mining algorithms.")
    #     app_data["marathon_docker"] = [
    #         {
    #             "cpu": 1.0,
    #             "memory": 32,
    #             "env_vars": {
    #                 "WOKEN_HOST": "foobar.com"
    #             }
    #         },
    #         {
    #             "cpu": 0.5,
    #             "memory": 64,
    #             "ports": [1534, 32432]
    #         },
    #         {
    #             "cpu": 2.0,
    #             "memory": 1024
    #         },
    #     ]

    #     # Test PUT method (marathon configuration should be overwritten)
    #     response = self.client.put(
    #         reverse("docker_app.details", kwargs={'pk': app.id}),
    #         app_data,
    #         format="json")

    #     after_count = app.marathondocker_set.count()

    #     print(response.__dict__)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertNotEqual(before_count, after_count)
