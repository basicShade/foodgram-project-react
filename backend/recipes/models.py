from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return self.name + ', ' + self.measurement_unit


class Tag(models.Model):
    """Модель тэгов"""
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='recipe title',
        max_length=200,
    )

    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True,
        default=None
        )

    text = models.TextField()

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )

    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes'
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )

    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель-связка рецептов с ингредиентами"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts'
    )

    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ]
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


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart',
            )
        ]

    def __str__(self):
        return f'{self.recipe} in {self.user} cart'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='is_favorited',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_favorited',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            )
        ]

    def __str__(self):
        return f'{self.recipe} is {self.user} favorite'
