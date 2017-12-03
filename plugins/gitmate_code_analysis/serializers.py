from rest_framework import serializers

from .models import AnalysisResults


class ResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResults
        fields = ('sha', 'coafile_location', 'repo', 'results')
