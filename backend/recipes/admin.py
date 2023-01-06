from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Recipe, Ingredient, Tag


class RecipeIngredientAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 0


class RecipeTagAdmin(admin.TabularInline):
    model = Recipe.tags.through
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cooking_time',
        'author',
    )
    list_editable = ()
    search_fields = ('name',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'
    inlines = [RecipeIngredientAdmin, RecipeTagAdmin]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
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
        'name',
        'color',
        'slug',
    )
    list_editable = ()
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('name',)}