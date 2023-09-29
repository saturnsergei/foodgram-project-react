from django_filters import rest_framework as filters
from rest_framework import filters as search_filter

from recipes.models import Recipe


class IngredientFilter(search_filter.SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    BOOL_FILTER = {
        '1': True,
        '0': False
    }

    author = filters.CharFilter(field_name='author__id')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.CharFilter(
        field_name='is_favorited', method='filter_is_favorited')
    is_in_shopping_cart = filters.CharFilter(
        field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if user is None or value not in self.BOOL_FILTER:
            return queryset
        if self.BOOL_FILTER[value]:
            return queryset.filter(favorite_user__user=user)
        else:
            return queryset.exclude(favorite_user__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if user is None or value not in self.BOOL_FILTER:
            return queryset
        if self.BOOL_FILTER[value]:
            return queryset.filter(cart_user__user=user)
        else:
            return queryset.exclude(cart_user__user=user)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
