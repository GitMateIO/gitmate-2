from rest_framework import serializers

from gitmate_config.models import Repository


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class RepositorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Repository
        fields = '__all__'
        read_only_fields = ('id', 'user', 'provider', 'full_name')


class PluginSettingsSerializer(serializers.Serializer):
    repository = serializers.CharField()
    plugins = serializers.ListField()
