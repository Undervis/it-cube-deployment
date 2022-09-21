from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    fields = ('user',)


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class EUserAdmin(UserAdmin):
    inlines = [
        ProfileInline
    ]
    list_display = UserAdmin.list_display


admin.site.unregister(User)
admin.site.register(User, EUserAdmin)

admin.site.register(Student)
admin.site.register(Group)
admin.site.register(PaidGroup)
admin.site.register(Direction)
