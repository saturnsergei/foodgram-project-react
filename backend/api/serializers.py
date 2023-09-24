import base64
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.base import ContentFile

from recipes.models import (Tag, Ingredient, Recipe,
                            IngredientAmount, ShoppingCart)

User = get_user_model()


# class TokenSerializer(serializers.Serializer):
#     """Сериализатор для получения токена."""

#     email = serializers.EmailField(max_length=150)
#     password = serializers.CharField(max_length=254)

#     def validate(self, data):
#         user = get_object_or_404(
#             User, email=data.get('email'))

#         if not check_password(data.get('password'), user.password):
#             raise serializers.ValidationError(
#                 'Неправильный пароль')
#         return data


# # class LogoutSerializer(serializers.Serializer):

class IsSubscribedSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.following.filter(user=request.user).exists()
        return False


class UserSerializer(IsSubscribedSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password', 'is_subscribed')
        write_only_fields = ('password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=True)
    current_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('new_password', 'current_password',)

    def validate(self, data):
        user = self.instance

        if not check_password(data.get('current_password'), user.password):
            raise serializers.ValidationError(
                'Неправильный пароль')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов"""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class Base64ImageField(serializers.ImageField):
    def to_representation(self, value):
        if value:
            return value.url
        return None

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов"""

    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set', many=True, read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('user')
        return obj.favorite_user.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('user')
        return obj.cart_user.filter(user=user).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')
        read_only_fields = ('author',)
        depth = 1

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)

        if 'ingredients' in self.initial_data:
            ingredients = self.initial_data.get('ingredients')

            for ingredient in ingredients:
                id = ingredient.get('id')
                amount = ingredient.get('amount')
                current_ingredient = get_object_or_404(Ingredient, pk=id)
                IngredientAmount.objects.create(
                    ingredient=current_ingredient, recipe=recipe, amount=amount
                )
        if 'tags' in self.initial_data:
            tags = self.initial_data.get('tags')
            for tag in tags:
                recipe.tags.add(tag)
        recipe.save()

        return recipe

    def update(self, instance, validated_data):
        IngredientAmount.objects.filter(recipe=instance).delete()

        if 'ingredients' in self.initial_data:
            ingredients = self.initial_data.get('ingredients')

            for ingredient in ingredients:
                id = ingredient.get('id')
                amount = ingredient.get('amount')
                current_ingredient = get_object_or_404(Ingredient, pk=id)
                IngredientAmount.objects.create(
                    ingredient=current_ingredient,
                    recipe=instance, amount=amount
                )
        if 'tags' in self.initial_data:
            tags = self.initial_data.get('tags')
            instance.tags.set([])
            for tag in tags:
                instance.tags.add(tag)
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенной модели рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(IsSubscribedSerializer):

    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(many=True, read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit is not None and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
            data['recipes'] = data['recipes'][:recipes_limit]

        return data


class FollowSubscribeSerializer(FollowSerializer):

    def validate(self, data):
        author = self.instance
        request = self.context['request']

        if request.user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')

        if author.following.filter(user=request.user).exists():
            raise serializers.ValidationError('Нельзя подписаться второй раз')

        return data


class FavoriteSerializer(RecipeShortSerializer):

    def validate(self, data):
        recipe = self.instance
        user = self.context['user']

        if recipe.favorite_user.filter(user=user).exists():
            raise serializers.ValidationError(
                'Нельзя добавить в избранное второй раз')

        return data


class ShoppingCartSerializer(RecipeShortSerializer):

    def validate(self, data):
        recipe = self.instance
        user = self.context['user']

        if ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок')

        return data
