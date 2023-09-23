from django_filters import rest_framework as filters
from rest_framework import filters as search_filter

from recipes.models import Recipes


class IngredientFilter(search_filter.SearchFilter):
    search_param = 'name'


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    author = filters.CharFilter(field_name='author__id')
    tags = CharInFilter(field_name='tags__slug', lookup_expr='in')
    is_favorited = filters.CharFilter(
        field_name='is_favorited', method='filter_is_favorited')
    is_in_shopping_cart = filters.CharFilter(
        field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if user is not None:
            if value == '1':
                return queryset.filter(favorite_user__user=user)
            if value == '0':
                return queryset.exclude(favorite_user__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if user is not None:
            if value == '1':
                return queryset.filter(cart_user__user=user)
            if value == '0':
                return queryset.exclude(cart_user__user=user)
        return queryset

    class Meta:
        model = Recipes
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
