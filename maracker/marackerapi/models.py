from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField

appname_max_length = 50


class DockerContainer(models.Model):
    """Represent a Docker container associatded with a Maracker application"""
    image = models.CharField(
        max_length=50,
        blank=False,
        # unique=True,
        validators=[RegexValidator('(:[\w][\w.]{0,127}?)?')])
    ports = ArrayField(
        models.PositiveIntegerField(
            validators=[MinValueValidator(0),
                        MaxValueValidator(65535)], ),
        default=list(),
        blank=True)

    def __str__(self):
        return f"{self.image} (id:{self.id})"


class MarackerApplication(models.Model):
    """Represent an application with its description"""
    name = models.SlugField(
        max_length=appname_max_length,
        unique=True,
        blank=False, )
    description = models.TextField(
        blank=True, default="no description available")
    command = models.TextField(blank=True, default="")
    vcs_url = models.URLField(blank=True, max_length=2000)
    docker_container = models.OneToOneField(
        DockerContainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, )

    def __str__(self):
        return self.name


class MarathonConfig(models.Model):
    """Represent a configuration that can be pushed to Marathon API"""
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
    env_vars = HStoreField(default=dict(), blank=True)
    maracker_app = models.ForeignKey(
        MarackerApplication, on_delete=models.CASCADE)

    def __str__(self):
        return "{self.id}, cpu: {self.cpu}, memory: {self.memory}".format(
            self=self)
