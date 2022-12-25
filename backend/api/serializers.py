import base64
import pprint

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import Recipe, Ingredient, Tag


class Base64ImageField(serializers.ImageField):
    """Сериализатор для поля с картинками"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name='rcp_img.' + ext
            )

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""
    image = Base64ImageField(required=False, allow_null=True)
    tag = SlugRelatedField(
        many=True,
        required=False,
        slug_field='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Tag
        fields = '__all__'


