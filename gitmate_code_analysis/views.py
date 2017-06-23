from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import AnalysisResults
from .serializers import ResultSerializer


@api_view(['GET'])
def get_analysis_results(request, repo, sha): # pragma: no cover
    """
    Returns the analysis results for the matching repository and commit sha.
    """
    results = AnalysisResults.objects.filter(repo=repo, sha=sha).first()
    if not results:
        raise Http404
    return Response(ResultSerializer(results).data, status.HTTP_200_OK)
