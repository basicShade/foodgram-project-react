import io

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts

from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient

from .serializers import IngredientSerializer, RecipeListSerializer
from .serializers import TagSerializer, RecipeWriteSerializer
from .serializers import BoolFieldUpdateSerializer
from .serializers import ShoppingListSerializer, RecipeSerializer
from .permissions import IsAuthenticatedAuthor

app_name = 'api'


class RecipeViewSet(viewsets.ModelViewSet):
    """View рецептов"""
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'author',
        'is_favorited',
        'is_in_shopping_cart'
    )
    lookup_field = 'pk'
    permission_classes = [IsAuthenticatedAuthor,]

    def get_queryset(self):
        qset = Recipe.objects.prefetch_related('tags', 'ingredients')
        tag = self.request.query_params.get('tags')

        if tag is not None:
            qset = qset.filter(tags__slug__icontains=tag)

        return qset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        elif self.action == 'list':
            return RecipeListSerializer
        elif self.action == 'retrieve':
            return RecipeSerializer

    def update_bool_field(self, request, pk, field):
        """Меняет значение булевого поля на противоположное"""
        recipe = get_object_or_404(Recipe.objects.filter(pk=pk))
        box_state = getattr(recipe, field)
        is_post = (request.method == 'POST')
        if box_state == is_post:
            error = {'errors': f'{field} is already {is_post}'}
            return error, status.HTTP_400_BAD_REQUEST
        setattr(recipe, field, not box_state)
        recipe.save()

        if not is_post:
            return None, status.HTTP_204_NO_CONTENT
        else:
            return BoolFieldUpdateSerializer(recipe).data, status.HTTP_201_CREATED

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        return Response(
            *self.update_bool_field(
                request,
                pk,
                field='is_in_shopping_cart'
            )
        )

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        return Response(
            *self.update_bool_field(
                request,
                pk,
                field='is_favorited'
            )
        )

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):

        ingredients = Ingredient.objects.filter(recipes__is_in_shopping_cart=True)
        ingredients = ingredients.annotate(Sum('amounts__amount'))
        for i in ingredients:
            print()
            print(i.__dict__)

        buffer = io.BytesIO()

        p = canvas.Canvas(buffer)
        pdfmetrics.registerFont(
            ttfonts.TTFont(
                'TNR', 'times.ttf', 'UTF-8'
            )
        )
        p.setFont('TNR', size=24)
        p.drawString(100, 750, "Список покупок")
        p.setFont('TNR', size=18)
        for i, item in enumerate(ingredients):
            line = f'\u2022 {item.name}, {item.measurement_unit}: {item.amounts__amount__sum}'
            p.drawString(100, 700-i*20, line)
        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """View рецептов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    lookup_field = 'pk'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """View рецептов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'pk'
