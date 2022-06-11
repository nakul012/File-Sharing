from asyncio.windows_events import NULL
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import admin


class User(AbstractUser):
    is_ops = models.BooleanField(default=False)


class FileUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=NULL)
    title = models.CharField(max_length=50)
    file = models.FileField(blank=True, null=True)


admin.site.register(User)
admin.site.register(FileUpload)
