from django.contrib import admin

# Register your models here.
from apps.segyviewer.models import File

admin.site.register(File)