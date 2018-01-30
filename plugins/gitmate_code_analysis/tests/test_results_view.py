from rest_framework import status

from gitmate_config.enums import Providers
from gitmate_config.tests.test_base import GitmateTestCase
from plugins.gitmate_code_analysis.models import AnalysisResults
from plugins.gitmate_code_analysis.views import get_analysis_result


class TestResultsView(GitmateTestCase):
    def setUp(self):
        super().setUp()
        self.user_detail_url = '/plugin/code_analysis/results'
        self.sha = '1234567890'

    def test_get_matching_result(self):
        AnalysisResults.objects.create(
            repo=self.repo, results={'hello': 'world'},
            sha=self.sha, coafile_location='.coafile')
        data = {'repo': self.repo.identifier,
                'sha': self.sha, 'provider': Providers.GITHUB.value}
        request = self.factory.get(self.user_detail_url, data=data)
        response = get_analysis_result(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'sha': self.sha,
                          'coafile_location': '.coafile',
                          'results': {'hello': 'world'},
                          'repo': self.repo.id})

    def test_get_missing_parameter(self):
        data = {'sha': self.sha, 'provider': Providers.GITHUB.value}
        request = self.factory.get(self.user_detail_url, data=data)
        response = get_analysis_result(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_result_not_found(self):
        data = {'repo': self.repo.identifier,
                'sha': self.sha, 'provider': Providers.GITHUB.value}
        request = self.factory.get(self.user_detail_url, data=data)
        response = get_analysis_result(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
