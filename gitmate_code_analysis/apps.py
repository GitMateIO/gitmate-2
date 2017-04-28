from django.apps import AppConfig


class GitmateCodeAnalysisConfig(AppConfig):
    name = 'gitmate_code_analysis'
    verbose_name = 'Code Analysis'
    description = 'Uses coala on the source code. Only new results will be ' \
                  'shown directly in the Pull Request/Merge Request. A ' \
                  '.coafile can be used to configure the analysis.'
