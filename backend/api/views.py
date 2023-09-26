import io

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Tag, Ingredient, Recipe, Follow, Favorite,
                            ShoppingCart, IngredientAmount)
from .filters import RecipeFilter, IngredientFilter
from .pagination import PagePagination
from .permissions import ReadOnly, IsAdmin, IsAuthor
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer,
                          UserSerializer,
                          ChangePasswordSerializer, FollowSerializer,
                          FollowSubscribeSerializer, FavoriteSerializer,
                          ShoppingCartSerializer)

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """Вьюсет для пользователей."""

    permission_classes = (AllowAny,)

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagePagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,))
    def me(self, request):

        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = ChangePasswordSerializer(
            instance=request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_password = serializer.validated_data.get('new_password')
            request.user.set_password(new_password)
            request.user.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):

        users = User.objects.filter(following__user=request.user)

        page = self.paginate_queryset(users)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            users, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = FollowSubscribeSerializer(
                author, data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                Follow.objects.create(user=request.user, author=author)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        queryset = Follow.objects.filter(user=request.user, author=author)
        if not queryset.exists():
            return Response({'errors': 'Вы не подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            follower = Follow.objects.filter(user=request.user, author=author)
            follower.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (ReadOnly | IsAdmin,)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    permission_classes = (ReadOnly | IsAdmin,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (ReadOnly | IsAuthor | IsAdmin,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def custom_create_delete(self, request, model, model_serializer, pk=None):
        """Метод для создания и удаления записи о рецепте для модели."""

        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = model_serializer(
                recipe, data=request.data, context={'user': request.user})
            if serializer.is_valid(raise_exception=True):
                model.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        queryset = model.objects.filter(
            user=request.user, recipe=recipe)
        if not queryset.exists():
            return Response({'errors': 'Рецепт не добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            record = model.objects.filter(
                user=request.user, recipe=recipe)
            record.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self.custom_create_delete(request, Favorite,
                                         FavoriteSerializer, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        return self.custom_create_delete(request, ShoppingCart,
                                         ShoppingCartSerializer, pk)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(cart_user__user=request.user)
        queryset = IngredientAmount.objects.filter(
            recipe__in=recipes).values('ingredient').annotate(
                total=Sum('amount'))

        text_buffer = io.StringIO()
        text_buffer.write('Ваш список покупок: \n\n')
        for row in queryset:

            ingredient = get_object_or_404(
                Ingredient, pk=row.get('ingredient'))
            total = row.get('total')
            text_buffer.write(
                f'{ingredient.name} - {total} ({ingredient.measurement_unit})'
                + '\n')

        file_data = text_buffer.getvalue()

        response = HttpResponse(file_data, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'

        return response
