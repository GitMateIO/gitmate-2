from urllib.parse import unquote_plus

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from gitmate_config.models import Repository

from .models import AnalysisResults
from .serializers import ResultsSerializer


@api_view(['GET'])
def get_analysis_result(request):
    """
    Retrieves the analysis report for a given commit. Do provide the `repo`,
    `provider` and `sha` GET parameters.
    """
    repo = unquote_plus(request.GET.get('repo', ''))
    provider = request.GET.get('provider')
    sha = request.GET.get('sha')
    if not all((repo, sha, provider)):
        return Response(
            data={
                'detail': '`repo`, `provider` or `sha` GET parameter missing'
            },
            status=HTTP_400_BAD_REQUEST)
    db_repo = get_object_or_404(
        Repository,
        Q(full_name=repo) | Q(identifier=repo if repo.isdigit() else 0),
        provider=provider)
    result = get_object_or_404(AnalysisResults, repo=db_repo, sha=sha)
    return Response(data=ResultsSerializer(result).data)
