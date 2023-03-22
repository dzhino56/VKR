from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
from django.utils import timezone

from account.models import Account


class File(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    user_file_path = models.CharField(max_length=250)
    real_file_path = models.CharField(max_length=250)

    class Meta:
        unique_together = ('user', 'name')
