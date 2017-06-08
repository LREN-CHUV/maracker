from django.db import models
from django.core.validators import MinValueValidator


class MipApplication(models.Model):
    """ Represent a MIP developped app deployable on Marathon """

    docker_namespace = models.CharField(max_length=50, blank=False)
    docker_image = models.CharField(max_length=50, blank=False)
    description = models.TextField(default="no description available")
    cpu = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0.0)
                    ],  # 0.1 due to Marathon's minimum constraint
        default=0.1)
    memory = models.IntegerField(
        validators=[MinValueValidator(32)
                    ],  # 32 due to Marathon's minimum constraint
        default=32)

    class Meta:
        unique_together = ("docker_namespace", "docker_image")

    def __str__(self):
        """ Return human readable represention of the instance """
        return "{}".format(self.docker_name)
