from django.urls import include, path
from rest_framework import routers

from .views import RecipeViewSet, IngredientViewSet, TagViewSet

# from .views import ShoppingListViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()
# router_v1.register(
#     r'recipes/download_shopping_cart',
#     ShoppingListViewSet,
#     basename='download_shopping_cart',
# )
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
# router_v1.register(
#     r'recipes/(?P<pk>[1-9]+[0-9]*)/shopping_cart',
#     ShoppingCartViewSet,
#     basename='shopping_cart',
# )
# router_v1.register(
#     r'recipes/(?P<pk>[1-9]+[0-9]*)/favorite',
#     FavoriteViewSet,
#     basename='favorite',
# )


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('users.urls'))

]