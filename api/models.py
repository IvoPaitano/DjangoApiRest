from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from django.conf import settings
from django.db.models.base import Model
from django.db.models.deletion import RESTRICT, SET_NULL
from django.db.models.enums import Choices
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class User(AbstractUser):
    balance = models.FloatField(blank=False, null=False, default=0.0, editable=True)

    def __str__(self):
        return self.username

class TypeOperation(models.Model):
    name = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return self.name

class Operation(models.Model):
    user = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    concept = models.CharField(max_length=100, blank=False)
    amount = models.FloatField(blank=False, null=False)
    date = models.DateTimeField(auto_now=True, blank=False, null=False)
    typeOperation = models.ForeignKey(TypeOperation, on_delete=SET_NULL, null=True)

    def __str__(self):
        return str(self.pk)

    

    






