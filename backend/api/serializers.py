# from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password

from recipes.models import (Tags, Ingredients, Recipes,
                            IngredientsAmount, Follow, Favorite, ShoppingCart)

User = get_user_model()


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(max_length=254)

    def validate(self, data):
        user = get_object_or_404(
            User, email=data.get('email'))

        if not check_password(data.get('password'), user.password):
            raise serializers.ValidationError(
                'Неправильный пароль')
        return data


# class LogoutSerializer(serializers.Serializer):

class IsSubscribedSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('user')
        return Follow.objects.filter(
            user=user,
            author=obj
        ).exists()


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


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов"""

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов"""

    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsAmountSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов"""

    tags = TagsSerializer(many=True, read_only=True)
    ingredients = IngredientsAmountSerializer(
        source='ingredientsamount_set', many=True, read_only=True)
    image = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    author = UserSerializer(read_only=True)
    # is_favorited = False
    # is_in_shopping_cart = False

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time',)
        read_only_fields = ('author',)
        depth = 1

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def create(self, validated_data):
        recipe = Recipes.objects.create(**validated_data)

        if 'ingredients' in self.initial_data:
            ingredients = self.initial_data.get('ingredients')

            for ingredient in ingredients:
                id = ingredient.get('id')
                amount = ingredient.get('amount')
                current_ingredient = get_object_or_404(Ingredients, pk=id)
                IngredientsAmount.objects.create(
                    ingredient=current_ingredient, recipe=recipe, amount=amount
                )
        if 'tags' in self.initial_data:
            tags = self.initial_data.get('tags')
            for tag in tags:
                recipe.tags.add(tag)
        recipe.save()

        return recipe

    def update(self, instance, validated_data):
        IngredientsAmount.objects.filter(recipe=instance).delete()

        if 'ingredients' in self.initial_data:
            ingredients = self.initial_data.get('ingredients')

            for ingredient in ingredients:
                id = ingredient.get('id')
                amount = ingredient.get('amount')
                current_ingredient = get_object_or_404(Ingredients, pk=id)
                IngredientsAmount.objects.create(
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


class RecipesShortSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенной модели рецептов."""

    class Meta:
        model = Recipes
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(IsSubscribedSerializer):

    recipes_count = serializers.SerializerMethodField()
    recipes = RecipesShortSerializer(many=True, read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count')


class FollowSubscribeSerializer(FollowSerializer):

    def validate(self, data):
        author = self.instance
        user = self.context['user']

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')

        if Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            raise serializers.ValidationError('Нельзя подписаться второй раз')

        return data


class FavoriteSerializer(RecipesShortSerializer):

    def validate(self, data):
        recipe = self.instance
        user = self.context['user']

        if Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Нельзя добавить в избранное второй раз')

        return data


class ShoppingCartSerializer(RecipesShortSerializer):

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
