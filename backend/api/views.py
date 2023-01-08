import io
import os

from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.pagination import CustomPageNumberPagination
from users.serializers import RecipeShortListSerializer

from .permissions import IsAuthenticatedAuthor
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeWriteSerializer, TagSerializer)

app_name = 'api'


class RecipeViewSet(viewsets.ModelViewSet):
    """View рецептов"""
    QUERY_PARAMS_FAVORITE_TRUE = '1'
    QUERY_PARAMS_FAVORITE_FALSE = '0'

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'author',
    )
    lookup_field = 'pk'
    permission_classes = [IsAuthenticatedAuthor, ]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        qset = Recipe.objects.prefetch_related('tags', 'ingredients')
        tags = self.request.query_params.getlist('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart'
        )
        user = self.request.user

        if len(tags):
            qset = qset.filter(tags__slug__in=tags)

        if user.is_anonymous:
            return qset

        if is_favorited == self.QUERY_PARAMS_FAVORITE_TRUE:
            qset = qset.filter(is_favorited__user=user)
        elif is_favorited == self.QUERY_PARAMS_FAVORITE_FALSE:
            qset = qset.exclude(is_favorited__user=user)

        if is_in_shopping_cart == self.QUERY_PARAMS_FAVORITE_TRUE:
            qset = qset.filter(is_in_shopping_cart__user=user)
        elif is_in_shopping_cart == self.QUERY_PARAMS_FAVORITE_FALSE:
            qset = qset.exclude(is_in_shopping_cart__user=user)

        return qset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeSerializer

    def update_bool_field(self, request, pk, klass, field):
        """
        Добавляет/удаляет рецепт из списков is_in_shopping_cart, is_favorite.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = klass.objects.filter(
            recipe=recipe,
            user=request.user
        )
        is_post = (request.method == 'POST')
        if is_post == obj.exists():
            error = {
                'errors': (
                    f'{recipe} {field} is already {is_post}'
                )
            }
            return Response(error, status.HTTP_400_BAD_REQUEST)

        if not is_post:
            obj.delete()
            return Response(None, status.HTTP_204_NO_CONTENT)

        klass.objects.create(
            recipe=recipe,
            user=request.user
        )
        data = RecipeShortListSerializer(recipe).data
        return Response(data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        return self.update_bool_field(
            request, pk, ShoppingCart, 'is_in_shopping_cart'
        )

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk):
        return self.update_bool_field(
            request, pk, Favorite, 'is_favorited'
        )

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):

        ingredients = Ingredient.objects.filter(
            recipes__is_in_shopping_cart__user=request.user
        )
        ingredients = ingredients.annotate(Sum('amounts__amount'))

        buffer = io.BytesIO()

        p = canvas.Canvas(buffer)
        pdfmetrics.registerFont(
            ttfonts.TTFont(
                'TNR',
                os.path.join(settings.BASE_DIR, 'api/fonts/Times.ttf'),
                'UTF-8'
            )
        )
        p.setFont('TNR', size=24)
        p.drawString(100, 750, "Список покупок")
        p.setFont('TNR', size=18)
        b = 20  # number of bullet on page
        for i, item in enumerate(ingredients):
            line = (f'\u2022 {item.name}, {item.measurement_unit}: '
                    f'{item.amounts__amount__sum}'
                    )
            pos = 720-(i % b)*20
            p.drawString(100, pos, line)
            if i % b == b-1:
                p.showPage()
                p.setFont('TNR', size=24)
                p.drawString(100, 750, "Список покупок (продолжение)")
                p.setFont('TNR', size=18)

        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_cart.pdf'
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """View рецептов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    lookup_field = 'pk'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """View рецептов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    lookup_field = 'pk'
