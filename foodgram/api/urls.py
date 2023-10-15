from rest_framework import routers
# from django.contrib import admin
from django.urls import path, include

from api.views import (
    CustomUserViewSet,
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet
)

router = routers.DefaultRouter()
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#     ShoppingCartViewSet,
#     basename='shopping_cart'
# )
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     FavoriteRecipeViewSet,
#     basename='favorite'
# )
# router.register(
#     r'users/(?P<author_id>\d+)/subscribe',
#     FollowViewSet,
#     basename='subscribe'
# )

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

app_name = 'api'

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
