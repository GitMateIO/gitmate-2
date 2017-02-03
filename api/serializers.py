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
        fields = ('user', 'provider', 'full_name', 'active')
