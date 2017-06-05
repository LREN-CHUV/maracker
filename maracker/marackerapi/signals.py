from .models import MipApplication
from .services import MicrobadgerService

def mipapp_pre_save(sender, instance, **kwargs):
    print("Test API")
    metadata = MicrobadgerService.get_docker_metadata(instance.docker_namespace, instance.docker_image)
    instance.memory = metadata.memory
    instance.description = metadata.description
