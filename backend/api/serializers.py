import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField

from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient
from users.serializers import UserSerializer


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


class ShowIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ( 'id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


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


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов (retrieve/delete)"""
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True)    
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)

    def get_ingredients(self, obj):
        return ShowIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj),
            many=True).data

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeListSerializer(RecipeSerializer):
    """Сериализатор списка рецептов (list)"""
    tags = SlugRelatedField(
        many=True,
        required=False,
        slug_field='slug',
        queryset=Tag.objects.all()
    )

    class Meta(RecipeSerializer.Meta):
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')


class RecipeWriteSerializer(RecipeSerializer):
    """Сериализатор добаления рецептов (create, update)"""
    tags = PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=Tag.objects.all()
    )
    ingredients = AddIngredientSerializer(many=True)

    class Meta(RecipeSerializer.Meta):
        fields = '__all__'

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_ingredients(validated_data.pop('ingredients'), recipe)
        self.create_tags(validated_data.pop('tags'), recipe)
        return super().update(recipe, validated_data)


class BoolFieldUpdateSerializer(RecipeListSerializer):
    """Инфо после добавления/удаления из корзины/favorites"""
    class Meta(RecipeListSerializer.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок"""
    
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Ingredient
        fields = ('ingredients')