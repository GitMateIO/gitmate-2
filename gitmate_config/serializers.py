from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.models import User
from gitmate_config.models import Repository


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


class RepositorySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    admins = serializers.SlugRelatedField(many=True, read_only=True,
                                          slug_field='username')

    class Meta:
        model = Repository
        fields = '__all__'
        read_only_fields = ('id', 'admins', 'provider', 'full_name')


class PluginSettingsSerializer(serializers.Serializer):
    repository = serializers.CharField()
    plugins = serializers.ListField()
