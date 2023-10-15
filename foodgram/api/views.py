from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
# from .utils import download_csv

from recipes.permissions import IsAuthor
from recipes.models import Tag, Recipe, User, Ingredient
from recipes.models import ShoppingCart, Favorite, Follow
from .serializers import TagSerializer, RecipeSerializer, RecipeCreateUpdateSerializer, RecipeShortSerializer
from .serializers import IngredientSerializer, ShoppingCartSerizlizer
from .serializers import FavoriteRecipeSerializer, FollowSerializer, FollowingUserSerializer


class CustomUserViewSet(UserViewSet):
    """Создание, чтение пользователей и подписок."""
    pagination_class = PageNumberPagination

    @action(
            methods=('post', 'delete',),
            detail=True,
            permission_classes = (IsAuthenticated,)
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
            ).data
        )


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


# class FollowViewSet(ModelViewSet):
#     """"""
#     serializer_class = FollowingUserSerializer
#     # queryset = User.objects.all()

#     def get_queryset(self):
#         user = self.request.user.id
#         return User.objects.filter(user=user)

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['author_id'] = self.kwargs.get('author_id')
#         return context

#     def perform_create(self, serializer):
#         serializer.save(
#             user=self.request.user,
#             author=get_object_or_404(
#                 User,
#                 id=self.kwargs.get('author_id')
#             )
#         )


class TagViewSet(ModelViewSet):
    """Тэги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'slug'


class RecipeViewSet(ModelViewSet):
    """Рецепты."""
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'ingredients', 'tags'
        ).select_related('author')

    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            self.permission_classes = (IsAuthor,)
        elif self.request.method == 'POST':
            self.permission_classes = (IsAuthenticated,)
        else:
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def delete_action(self, request, pk, model):
        """Удаление объекта модели favorite/shopping_cart."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if not model.objects.filter(
            user=request.user,
            favorite_recipe=recipe
        ).exists():
            raise ValidationError({
                'error': 'Рецепта нет в избранном'
            })
        model.objects.filter(
            user=request.user,
            favorite_recipe=recipe
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def create_action(self, request, pk, serializer):
        """Создание объекта модели favorite/shopping_cart."""
        favorite = serializer(
                data={'id': pk},
                context={'request': request}
            )
        favorite.is_valid(raise_exception=True)
        favorite.save()
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
        if request.method == 'POST':
            return self.create_action(
                request,
                pk,
                FavoriteRecipeSerializer
            )
        return self.delete_action(request, pk, Favorite)

    @action(
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        detail=True,
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.create_action(
                request,
                pk,
                ShoppingCartSerizlizer
            )
        return self.delete_action(
            request,
            pk,
            ShoppingCart
        )

    # @action(
    #     methods=('get',),
    #     permission_classes=(IsAuthenticated,),
    #     detail=False
    # )
    # def download_shopping_cart(self, request):
    #     ingredients = RecipeIngredient.objects.filter(
    #         recipe__in_cart__user=request.user
    #     ).select_related(
    #         'author'
    #     ).prefetch_related(
    #         'tags', 'ingredients'
    #     ).values(
    #         'ingredient__name', 'ingredient__measurement_unit'
    #     ).annotate(
    #         amount=Sum('ingredient_quantity')
    #     )
    #     return download_csv(ingredients)



# class ShoppingCartViewSet(ModelViewSet):
#     serializer_class = ShoppingCartSerizlizer

#     def get_queryset(self):
#         user = self.request.user.id
#         return ShoppingCart.objects.filter(user=user)

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['recipe_id'] = self.kwargs.get('recipe_id')
#         return context
    
#     def perform_create(self, serializer):
#         serializer.save(
#             user=self.request.user,
#             recipe=get_object_or_404(
#                 Recipe,
#                 id=self.kwargs['recipe_id']
#             )
#         )


# class FavoriteRecipeViewSet(ModelViewSet):
#     serializer_class = FavoriteRecipeSerializer

#     def get_queryset(self):
#         user = self.request.user.id
#         return Favorite.objects.filter(user=user)

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['recipe_id'] = self.kwargs.get('recipe_id')
#         return context
    
#     def perform_create(self, serializer):
#         serializer.save(
#             user=self.request.user,
#             favorite_recipe=get_object_or_404(
#                 Recipe,
#                 id=self.kwargs['recipe_id']
#             )
#         )

#     @action(methods=('delete',), detail=True)
#     def delete(self, request, recipe_id):
#         user = request.user
#         if not user.favorite.select_related(
#             'favorite_recipe').filter(
#                 favorite_recipe_id=recipe_id).exists():
#             return Response(
#                 {'errors': f'Рецепт отсутствует в Избранном.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         get_object_or_404(
#             Favorite,
#             user=request.user,
#             favorite_recipe_id=recipe_id
#         ).delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


