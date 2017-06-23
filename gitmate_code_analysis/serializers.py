from rest_framework.serializers import ModelSerializer

from gitmate_code_analysis.models import AnalysisResults
from gitmate_config.serializers import RepositorySerializer


class ResultSerializer(ModelSerializer):
    repo = RepositorySerializer(read_only=True)

    class Meta:
        model = AnalysisResults
        fields = '__all__'
