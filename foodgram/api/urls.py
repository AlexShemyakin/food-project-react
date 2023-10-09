from rest_framework import routers
from django.contrib import admin
from django.urls import path, include

from api.views import CustomUserViewSet, TagViewSet, RecipeViewSet
from api.views import IngredientViewSet, ShoppingCartViewSet, FavoriteRecipeViewSet
from api.views import CustomUserViewSet, FollowViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteRecipeViewSet,
    basename='favorite'
)
router.register(
    r'users/(?P<recipe_id>\d+)/subscribe',
    FollowViewSet,
    basename='subscribe'
)

app_name = 'api'

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
