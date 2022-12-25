from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User

from .models import Recipe, Ingredient, Tag

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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_editable = ()
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_editable = ()
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'