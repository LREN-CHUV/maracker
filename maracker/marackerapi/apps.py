from django.apps import AppConfig
from django.db.models.signals import pre_save


class MarackerapiConfig(AppConfig):
    name = 'marackerapi'

    def ready(self):
        from .signals import mipapp_pre_save
        from .models import MipApplication
        pre_save.connect(mipapp_pre_save, sender=MipApplication)
