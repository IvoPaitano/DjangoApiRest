from api import models
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    message = "He is not the owner of the operation"

    def has_permission(self, request, view):
        
        # Vemos si viene el ID dentro de los parámetros, y el usuario
        if 'id' in view.kwargs:
            try:
                # Recuperamos el user basado en lo que viene en la request
                userReq = models.User.objects.get(pk=request.user.pk)
                # Recuperamos el user asociado a la operacion
                userOp  = models.Operation.objects.get(pk=view.kwargs['id']).user
                # Vemos que sea el mismo user que hizo la request
                return userReq == userOp
            except models.Operation.DoesNotExist:
                return False
        return False