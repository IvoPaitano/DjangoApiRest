from django.contrib.auth.models import User
from django.forms import ValidationError
from django.forms.models import ModelForm
from . import models
from django import forms

from django.contrib.auth import get_user_model
User = get_user_model()

class CreateOperationForm(ModelForm):
    class Meta:
        model = models.Operation
        fields = ['amount','concept','typeOperation']
    
    def clean_amount(self):
        data = self.cleaned_data['amount']
        if data <= 0:
            raise ValidationError('Invalid amount')
        return data

class UpdateOperationForm(ModelForm):
    class Meta:
        model = models.Operation
        fields = ['amount','concept',]

    def clean_amount(self):
        data = self.cleaned_data['amount']
        if data <= 0:
            raise ValidationError('Invalid amount')
        return data

