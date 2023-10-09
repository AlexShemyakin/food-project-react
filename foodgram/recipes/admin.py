from django.contrib import admin

from .models import Tag, Recipe, Ingredient, RecipeIngredient
from .models import ShoppingCart, Favorite, Follow, User


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass
    # list_display = (
    #     'pk',
    #     'title',
    #     'measure',
    # )
    # search_fields = ('title',)
    # empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    list_display = (
        'pk',
        'name',
        # 'author',
        # 'pub_date',
        # 'time',
        # 'image',
    )
    # search_fields = ('title', )
    # list_filter = ('author', 'title', 'tags')
    # empty_value_display = '-пусто-'



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
        'color',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    # author = Recipe.author.username

    list_display = (
        'id',
        'user',
        'favorite_recipe',
        # 'author'
    )

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'user',
        'sub_date'
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'recipes_count'
    )
    list_filter = (
        'username',
        'email',
    )

    def recipes_count(self, obj):
        return obj.recipes.all().count()

    recipes_count.short_description = 'Всего рецептов'