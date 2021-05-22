from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api.models import Operation, TypeOperation, User

# Register your models here.
UserAdmin.fieldsets += ('Custom field set', {'fields':('balance',)}),
admin.site.register(Operation)
admin.site.register(TypeOperation)
admin.site.register(User, UserAdmin)


