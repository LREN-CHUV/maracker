from django.contrib import admin
from .models import MarackerApplication, DockerContainer, MarathonConfig

admin.site.register(MarackerApplication)
admin.site.register(DockerContainer)
admin.site.register(MarathonConfig)
