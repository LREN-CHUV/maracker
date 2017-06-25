from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField


class CmdApp(models.Model):
    name = models.CharField(max_length=50, blank=False)
    description = models.TextField(default="no description available")
    command = models.TextField(blank=False)

    def __str__(self):
        return "{self.id}: {self.name}".format(self)


class DockerApp(models.Model):
    name = models.CharField(max_length=50, blank=False)
    description = models.TextField(default="no description available")
    namespace = models.CharField(max_length=50, blank=False)
    image = models.CharField(max_length=50, blank=False)

    class Meta:
        unique_together = ("namespace", "image")

    def __str__(self):
        return "{self.namespace}/{self.image}".format(self)


class MarathonCmd(models.Model):
    cpu = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0.0)
                    ],  # 0.1 due to Marathon's minimum constraint
        default=0.1)
    memory = models.PositiveIntegerField(
        validators=[MinValueValidator(32)
                    ],  # 32 due to Marathon's minimum constraint
        default=32)
    args = models.TextField(blank=True)
    env_vars = HStoreField(default=dict())
    cmd_app = models.ForeignKey(CmdApp, on_delete=models.CASCADE)

    def __str__(self):
        return "{self.id}, cpu: {self.cpu}, memory: {self.memory}".format(self)


class MarathonDocker(models.Model):
    cpu = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0.0)
                    ],  # 0.1 due to Marathon's minimum constraint
        default=0.1)
    memory = models.PositiveIntegerField(
        validators=[MinValueValidator(32)
                    ],  # 32 due to Marathon's minimum constraint
        default=32)
    version = models.CharField(max_length=100, blank=True)
    args = models.TextField(blank=True)
    ports = ArrayField(
        models.PositiveIntegerField(
            validators=[MinValueValidator(0),
                        MaxValueValidator(65535)]))
    env_vars = HStoreField(default=dict())
    docker_app = models.ForeignKey(DockerApp, on_delete=models.CASCADE)

    def __str__(self):
        return "Docker Marathon config: id={self.id}, cpu={self.cpu}".format(
            self)
