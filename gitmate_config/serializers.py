"""
This module contains the serializers for all models in gitmate core.
"""
from django.contrib.auth.models import User
from rest_framework.serializers import CharField
from rest_framework.serializers import ListField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.serializers import SlugRelatedField
from rest_framework.serializers import StringRelatedField

from gitmate_config.models import Installation
from gitmate_config.models import Repository


class UserSerializer(ModelSerializer):
    """
    A serializer for User model.
    """
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


class InstallationSerializer(ModelSerializer):
    """
    A serializer for Installation model.
    """
    admins = SlugRelatedField(many=True, read_only=True, slug_field='username')

    class Meta:
        model = Installation
        fields = '__all__'


class RepositorySerializer(ModelSerializer):
    """
    A serializer for Repository model.
    """
    user = SlugRelatedField(slug_field='username', queryset=User.objects.all())
    admins = StringRelatedField(many=True, read_only=True)
    org = StringRelatedField(read_only=True)
    installation = InstallationSerializer(read_only=True)

    class Meta:
        model = Repository
        fields = '__all__'
        read_only_fields = ('id', 'admins', 'provider', 'full_name')


class PluginSettingsSerializer(Serializer):
    """
    A serializer for plugin Settings.
    """
    repository = CharField()
    plugins = ListField()
