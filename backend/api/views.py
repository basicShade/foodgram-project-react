from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets


from recipes.models import Recipe, Ingredient, Tag

from .serializers import RecipeSerializer, IngredientSerializer
from .serializers import TagSerializer

app_name = 'api'


class RecipeViewSet(viewsets.ModelViewSet):
    """View рецептов"""
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'author',
        'is_favorited',
        'is_in_shopping_cart',
    )
    lookup_field = 'pk'

    def get_queryset(self):
        qset = Recipe.objects.prefetch_related('tag')
        tag = self.request.query_params.get('tag')

        if tag is not None:
            qset = qset.filter(tag__slug__icontains=tag)

        return qset


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
