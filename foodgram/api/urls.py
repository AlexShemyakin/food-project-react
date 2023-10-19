from rest_framework import routers
from django.urls import path, include

from api.views import (
    CustomUserViewSet,
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet
)


router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls))
]
