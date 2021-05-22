import contextlib
from os import stat
from typing import ContextManager
from django.http.request import validate_host
from django.utils.html import conditional_escape
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from api import serializers, mailing
from django.core.exceptions import ObjectDoesNotExist
from .permissions import IsOwner

from rest_framework.views import APIView


from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from . import forms
from . import models
from rest_framework import generics

# Mailing
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode


from django.contrib.auth import get_user_model
User = get_user_model()

class Home(generics.ListAPIView):
    serializer_class = serializers.OperationSerializer

    def get_queryset(self):
        user = self.request.user
        operations = models.Operation.objects.filter(user=user)
        return operations
    
    def list(self, request, *args, **kwargs):
        user = self.request.user
        balance = user.balance
        response = super().list(request, *args, **kwargs)
        return Response({
            'Balance': balance,
            'Operations': response.data
        })


@api_view(['GET','POST'])
@permission_classes([AllowAny])
def user_api_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            queryset = models.User.objects.all()
            users_serializer = serializers.UserSerializer(queryset, many=True)
            return Response(users_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'messagge':'Unauthenticated user'}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        user_serializer = serializers.RegisterSerializer(data = request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            user = user_serializer.save()
            mailing.send_confirmation_email(user, request)
            return Response({'message':'Successfully registered user!','user': user_serializer.data},status = status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors,status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if user != None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)

class Login(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        login_serializer = self.serializer_class(data = request.data, context = {'request':request})
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            if user.is_active:
                token, created = Token.objects.get_or_create(user = user)
                user_serializer = serializers.UserSerializer(user)
                if created:
                    return Response({
                        'token' : token.key,
                        'user' : user_serializer.data,
                        'message' : 'Successful login'
                        },status=status.HTTP_201_CREATED)
                else:
                    token.delete()
                    token = Token.objects.create(user = user)
                    return Response({
                        'token' : token.key,
                        'user' : user_serializer.data,
                        'message' : 'Successful login'
                        },status=status.HTTP_201_CREATED)
            else:
                return Response({'error' : 'Incorrect information'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error' : 'Incorrect information'}, status=status.HTTP_400_BAD_REQUEST)

class Operation(APIView):
    def post(self, request, format=None):
        form = forms.CreateOperationForm(request.POST)
        if form.is_valid():
            user = request.user
            amount = form.cleaned_data['amount']
            concept = form.cleaned_data['concept']
            typeOperation = form.cleaned_data['typeOperation']
            op = models.Operation(user=user, amount=amount, concept=concept, typeOperation=typeOperation)
            op.save()
            if typeOperation.name == 'ingreso':
                user.balance += op.amount
            else:
                user.balance -= op.amount
            user.save()
            return Response(serializers.OperationSerializer(op, many=False).data, status=status.HTTP_201_CREATED)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class OperationSpecific(APIView):
    permission_classes = [IsOwner]

    def put(self, request, id, formate=None):
        op = models.Operation.objects.get(id=id)
        serializer = serializers.OperationSpecificSerializer(data=request.data, instance=op, context={'request':request})
        if serializer.is_valid():
            op.amount = serializer.validated_data['amount']
            op.concept = serializer.validated_data['concept']
            op.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id, formate=None):
        try:
            op = models.Operation.objects.get(pk=id)
            op.delete()
            return Response({'message' : f'Operation {id} removed successfully'},status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error' : f'Operation {id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

#Comentario para probar git.