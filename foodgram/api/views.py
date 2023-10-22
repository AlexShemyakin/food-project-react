from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action

from .utils.paginators import CustomPaginator
from .utils.responses import download_csv
from .filters import RecipeFilter
from recipes.permissions import IsAuthorOrReadOnly
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
    IngredientSerializer,
    ShoppingCartSerizlizer,
    FavoriteRecipeSerializer,
    FollowSerializer,
    FollowingUserSerializer,
)


class CustomUserViewSet(UserViewSet):
    """
    Представление модели User.
    CRD(create, read, delete) моделей User, Follow.
    """
    pagination_class = CustomPaginator

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
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
        get_object_or_404(
            Follow,
            user=request.user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__user=request.user.id
        )
        serializer = FollowingUserSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    """Представление тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    lookup_field = 'slug'


class RecipeViewSet(ModelViewSet):
    """
    CRUD моделей Favorite, ShoppingCart,
    Recipe, RecipeIngredient.
    """
    queryset = Recipe.objects.prefetch_related(
        'tags', 'ingredients'
    ).select_related('author')
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = IsAuthorOrReadOnly

    def get_queryset(self):
        if self.action == 'favorite':
            return self.filter_queryset(self.get_queryset())
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

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
        return Response(
            serializer,
            status=status.HTTP_201_CREATED
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
        permission_classes=(IsAuthenticated,),
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
            ShoppingCartSerizlizer,
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
