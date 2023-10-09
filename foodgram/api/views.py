from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from recipes.models import Tag, Recipe, User, Ingredient
from recipes.models import ShoppingCart, Favorite, Follow
from .serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, CustomUserSerializer
from .serializers import SetPasswordSerializer, IngredientSerializer, ShoppingCartSerizlizer
from .serializers import FavoriteRecipeSerializer, FollowSerializer
from .mixins import CreateDestroyViewSet


class CustomUserViewSet(UserViewSet):
    """Создание, чтение пользователей."""
    # queryset = User.objects.all()
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    # pagination_class = ВЗЯТЬ ИЗ SETTINGS

    # def get_serializer_class(self):
    #     if self.action == 'set_password':
    #         return SetPasswordSerializer
    #     # if self.action == 'create':
    #     #     return UserCreateSerializer
    #     return CustomUserSerializer

    @action(methods=('post', 'delete',), detail=False)
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            author = get_object_or_404(
                User,
                id=id
            )
            follow = FollowSerializer(
                data={'id': author.id},
                context={'request': request}
            )
            follow.save()
            return Response(
                FollowSerializer(
                    author,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )


    @action(
            methods=('get',),
            detail=False,
            permission_classes=(IsAuthenticatedOrReadOnly,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__author=request.user.id
        )
        # page = self.paginate_queryset(queryset)
        return Response(
            FollowSerializer(
                queryset,
                many=True,
                context={'request': request}
            ).data
        )



class FollowViewSet(CreateDestroyViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return self.request.user.follower.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author_id'] = self.kwargs.get('user_id')
        return context
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            author=get_object_or_404(
                User,
                id=self.kwargs.get('user_id')
            )
        )


class TagViewSet(ModelViewSet):
    """Тэги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    
    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class ShoppingCartViewSet(ModelViewSet):
    serializer_class = ShoppingCartSerizlizer
    
    def get_queryset(self):
        user = self.request.user.id
        return ShoppingCart.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs['recipe_id']
            )
        )


class FavoriteRecipeViewSet(ModelViewSet):
    serializer_class = FavoriteRecipeSerializer

    def get_queryset(self):
        user = self.request.user.id
        return Favorite.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            favorite_recipe=get_object_or_404(
                Recipe,
                id=self.kwargs['recipe_id']
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        user = request.user
        if not user.favorite.select_related(
            'favorite_recipe').filter(
                favorite_recipe_id=recipe_id).exists():
            return Response(
                {'errors': f'Рецепт отсутствует в Избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(
            Favorite,
            user=request.user,
            favorite_recipe_id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


