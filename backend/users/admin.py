from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'email')


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
