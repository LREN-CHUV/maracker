from django.contrib import admin
from .models import MarathonCmd, MarathonDocker, CmdApp, DockerApp

admin.site.register(MarathonCmd)
admin.site.register(MarathonDocker)
admin.site.register(CmdApp)
admin.site.register(DockerApp)
