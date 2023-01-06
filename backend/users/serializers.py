from pprint import pprint
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from recipes.models import Recipe
from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if not self.context:
            user = obj
        else:
            user = self.context.get('request').user
            if user.is_anonymous:
                return False

        return Follow.objects.filter(user=user, author=obj.id).exists()


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
            return make_password(value, settings.SECRET_KEY)

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        if not check_password(value, self.instance.password):
            raise serializers.ValidationError('Проверьте пароль')
        return value
    
    def validate_new_password(self, value):
        if check_password(value, self.instance.password):
            raise serializers.ValidationError('Пароль не изменился')
        return make_password(value, settings.SECRET_KEY)

    def update(self, instance, validated_data):
        instance.password = validated_data['new_password']
        instance.save()
        return instance


class RecipeShortListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')



class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes'
        )

    def get_recipes(self, obj):
        qset = Recipe.objects.filter(author=obj)
        limiter = self.context.get('recipes_limit')
        qset = qset[:int(limiter)] if limiter else qset

        return RecipeShortListSerializer(qset, many=True).data

