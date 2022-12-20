from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=200)


class Tag(models.Model):
    """Модель тэгов"""
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='recipe title',
        mex_length=200,
        unique=True
    )

    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        )

    description = models.TextField()

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )

    tag = models.ManyToManyField(
        Tag,
        through='RecipeTag'
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1))
    )

    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)


class RecipeIngredient(models.Model):
    """Модель-связка рецептов с ингредиентами"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )

    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1))
    )


class RecipeTag(models.Model):
    """Модель-связка рецептов с тэгами"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
