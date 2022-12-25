from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User

from .models import Recipe

admin.site.unregister(Group)
admin.site.unregister(User)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
    )
    list_editable = ()
    search_fields = ('name',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'

