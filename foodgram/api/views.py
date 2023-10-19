from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action

from .utils import download_csv
from utils.paginators import CustomPaginator
from recipes.filters import RecipeFilter
from recipes.permissions import IsAuthor
from recipes.models import (
    Tag,
    Recipe,
    User,
    Ingredient,
    ShoppingCart,
    Favorite,
    Follow,
    RecipeIngredient,
)
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    RecipeCreateUpdateSerializer,
    RecipeShortSerializer,
    IngredientSerializer,
    ShoppingCartSerizlizer,
    FavoriteRecipeSerializer,
    FollowSerializer,
    FollowingUserSerializer,
)


class CustomUserViewSet(UserViewSet):
    """Создание/чтение/удаление пользователей/подписок."""
    pagination_class = CustomPaginator

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            follow = FollowSerializer(
                data={'id': author.id},
                context={'request': request}
            )
            follow.is_valid(raise_exception=True)
            follow.save()
            return Response(
                FollowingUserSerializer(
                    author,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        if not Follow.objects.filter(
            user=request.user,
            author=author
        ).exists():
            raise ValidationError({
                'error': 'Пользователь отсутствует в избранном'
            })
        Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthor,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__user=request.user.id
        )
        page = self.paginate_queryset(queryset)
        if page:
            serializer = FollowingUserSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        return Response(
            FollowingUserSerializer(
                queryset,
                many=True,
                context={'request': request}
            )
        )


class IngredientViewSet(ModelViewSet):
    """Ингридиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ModelViewSet):
    """Тэги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'slug'
    


class RecipeViewSet(ModelViewSet):
    """
    Рецепты.
    Создание/удаление моделей рецептов,
    избранного, списка покупок.
    """
    queryset = Recipe.objects.prefetch_related(
        'tags', 'ingredients'
    ).select_related('author')
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter


    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            self.permission_classes = (IsAuthor,)
        else:
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def delete_action(self, request, pk, serializer, model):
        """Удаление объекта модели favorite/shopping_cart."""
        obj = serializer(
            data={'id': pk},
            context={'request': request}
        )
        obj.is_valid(raise_exception=True)
        self.perform_destroy(
            model.objects.filter(recipe=pk, user=request.user)
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_action(self, request, pk, serializer):
        """Создание объекта модели favorite/shopping_cart."""
        obj = serializer(
            data={'id': pk},
            context={'request': request}
        )
        obj.is_valid(raise_exception=True)
        obj.save()
        recipe = get_object_or_404(Recipe, id=pk)
        return Response(
            RecipeShortSerializer(recipe).data,
            status=status.HTTP_200_OK
        )

    @action(
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        detail=True,
    )
    def favorite(self, request, pk=None):
        """Создание/удаление модели избранного."""
        if request.method == 'POST':
            return self.create_action(
                request,
                pk,
                FavoriteRecipeSerializer
            )
        return self.delete_action(
            request,
            pk,
            FavoriteRecipeSerializer,
            Favorite
        )

    @action(
        methods=('post', 'delete'),
        permission_classes=(IsAuthor,),
        detail=True,
    )
    def shopping_cart(self, request, pk=None):
        """Создать/удалить модель списка покупок."""
        if request.method == 'POST':
            return self.create_action(
                request,
                pk,
                ShoppingCartSerizlizer
            )
        return self.delete_action(
            request,
            pk,
            FavoriteRecipeSerializer,
            ShoppingCart
        )

    @action(
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        detail=False
    )
    def download_shopping_cart(self, request):
        """Создание/скачивание файла списка покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).select_related(
            'author'
        ).prefetch_related(
            'tags', 'ingredients'
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        )
        return download_csv(ingredients)
