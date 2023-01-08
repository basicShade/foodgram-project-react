from django.contrib import admin
from django.db.models import Count

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeIngredientAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 0


class RecipeTagAdmin(admin.TabularInline):
    model = Recipe.tags.through
    extra = 0


class ShoppingCartInline(admin.StackedInline):
    model = ShoppingCart
    fk_name = 'user'
    extra = 0


class FavoriteInline(admin.StackedInline):
    model = Favorite
    fk_name = 'user'
    extra = 0


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'user',
        'recipe'
    )
    search_fields = ('user__username', 'recipe__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'user',
        'recipe'
    )
    search_fields = ('user__username', 'recipe__name')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cooking_time',
        'author',
        'favorite_count'
    )
    readonly_fields = ('pub_date',)
    list_editable = ()
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = [RecipeIngredientAdmin, RecipeTagAdmin]

    def favorite_count(self, obj):
        return obj.favorite_count
    favorite_count.short_description = "is_favorited counter"

    def get_queryset(self, request):
        qs = super().get_queryset(request=request)
        return qs.annotate(favorite_count=Count('is_favorited'))


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
