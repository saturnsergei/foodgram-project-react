import io
from rest_framework import mixins, status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from .pagination import PagePagination
from recipes.models import (Tags, Ingredients, Recipes, Follow, Favorite,
                            ShoppingCart, IngredientsAmount)
from .serializers import (TagsSerializer, IngredientsSerializer,
                          RecipesSerializer, TokenSerializer, UserSerializer,
                          ChangePasswordSerializer, FollowSerializer,
                          FollowSubscribeSerializer, FavoriteSerializer,
                          ShoppingCartSerializer)
from .filters import RecipeFilter, IngredientFilter
from .permissions import ReadOnly, IsAdmin, IsAuthor

User = get_user_model()


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, email=serializer.data.get('email'))

        refresh = RefreshToken.for_user(user)

        return Response(
            {'auth_token': str(refresh.access_token)},
            status=status.HTTP_201_CREATED)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):

    permission_classes = (ReadOnly,)

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagePagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
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
            # TODO
            serializer = FollowSerializer(
                page, many=True, context={
                    'user': request.user, 'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            users, many=True, context={'user': request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = FollowSubscribeSerializer(
                author, data=request.data, context={'user': request.user})
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


class TagsViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (ReadOnly | IsAdmin,)


class IngredientsViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('^name')
    permission_classes = (ReadOnly | IsAdmin,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
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

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipes, pk=pk)

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                recipe, data=request.data, context={'user': request.user})
            if serializer.is_valid(raise_exception=True):
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        queryset = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not queryset.exists():
            return Response({'errors': 'Рецепт не добавлен в избранное'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            favorite = Favorite.objects.filter(
                user=request.user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipes, pk=pk)

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                recipe, data=request.data, context={'user': request.user})
            if serializer.is_valid(raise_exception=True):
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        queryset = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe)
        if not queryset.exists():
            return Response({'errors': 'Рецепт не добавлен в список покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            cart = ShoppingCart.objects.filter(
                user=request.user, recipe=recipe)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        recipes = Recipes.objects.filter(cart_user__user=request.user)
        queryset = IngredientsAmount.objects.filter(
            recipe__in=recipes).values('ingredient').annotate(
                total=Sum('amount'))

        text_buffer = io.StringIO()
        text_buffer.write('Ваш список покупок: \n\n')
        for row in queryset:

            ingredient = get_object_or_404(
                Ingredients, pk=row.get('ingredient'))
            total = row.get('total')
            text_buffer.write(
                f'{ingredient.name} - {total} ({ingredient.measurement_unit})'
                + '\n')

        file_data = text_buffer.getvalue()

        response = HttpResponse(file_data, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'

        return response
