"""Сериалайзеры приложения users."""

from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.serializers.nested import RecipeShortReadSerializer
from users.models import User, Subscribe


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    is_subscribed = serializers.SerializerMethodField('is_subscribed_user')

    class Meta:
        """Мета класс пользователя."""

        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
        }
        model = User

    def validate_username(self, value):
        """Валидация имени пользователя."""
        if value == 'me':
            raise ValidationError('Имя пользователя "me" запрещено.')
        return value

    def is_subscribed_user(self, obj):
        """Проверка подписки пользователя."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.subscribing.filter(user=user).exists()
        )

    def create(self, validated_data):
        """Создание пользователя."""
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для подписок."""

    recipes = RecipeShortReadSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        """Мета класс сериализатора для подписок."""

        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def validate(self, data):
        author = data['subscribing']
        user = data['subscriber']
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError('Нельзя подписаться дважды!')
        return data

    def create(self, validated_data):
        subscribe = Subscribe.objects.create(**validated_data)
        subscribe.save()
        return subscribe

    def get_recipes_count(self, obj):
        """Получение количества рецептов."""
        return obj.recipes.count()
