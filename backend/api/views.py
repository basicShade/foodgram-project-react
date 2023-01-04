import pprint

from django.shortcuts import get_object_or_404
from django.db.models import Sum

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient

from .serializers import IngredientSerializer, RecipeListSerializer
from .serializers import TagSerializer, RecipeWriteSerializer
from .serializers import BoolFieldUpdateSerializer
from .serializers import ShoppingListSerializer, RecipeSerializer

app_name = 'api'



# class ShoppingListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     queryset = Ingredient.objects.filter(recipes__is_in_shopping_cart=True)
#     serializer_class = ShoppingListSerializer



class RecipeViewSet(viewsets.ModelViewSet):
    """View рецептов"""
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'author',
        'is_favorited',
        'is_in_shopping_cart',
    )
    lookup_field = 'pk'

    def get_queryset(self):
        qset = Recipe.objects.prefetch_related('tags', 'ingredients')
        tag = self.request.query_params.get('tag')

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
