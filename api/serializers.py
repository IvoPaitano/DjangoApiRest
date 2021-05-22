from typing import Type
from rest_framework import serializers
from django.contrib.auth.models import User
from . import models
from django.contrib.auth.hashers import make_password
from .models import Operation, TypeOperation

from django.contrib.auth import get_user_model
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['username','email','password']
        read_only_fields = ['password']
        #to_representation -> modify the way it displays serialized data

    def validate_email(self, value):
        try:
            user = models.User.objects.get(email = value)
            if user != None:
                raise serializers.ValidationError('A user with that email already exists.')
            return value
        except models.User.DoesNotExist:
            return value

    def validate_password(self, value):
        value = make_password(value)
        return value

    def create(self, validated_data):
        user = models.User(**validated_data)
        user.is_active = False
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['username','email','is_active']
    

class TypeOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TypeOperation
        fields = ['name',]

class OperationSerializer(serializers.ModelSerializer):
    typeOperation = TypeOperationSerializer(many=False)
    user = UserSerializer(many=False)
    class Meta:
        model = models.Operation
        fields = '__all__'

class OperationSpecificSerializer(serializers.ModelSerializer):
    typeOperation = TypeOperationSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = models.Operation
        fields = '__all__'
