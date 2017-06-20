import json
from collections import defaultdict

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from coala_online.task import run_coala_online


@require_http_methods(['POST'])
def coala_online(request):
    """
    Spawns a docker container to run coala and coala-quickstart as specified.

    Documentation on the running modes can be found here,
    https://gitlab.com/hemangsk/coala-incremental-results/blob/master/README.md
    """
    request = json.loads(request.body.decode('utf-8'))

    req = defaultdict(lambda : None)

    req['mode'] = request['mode']
    req['file_content'] = request.get('file_data', None)
    req['language'] = request.get('language', None)
    req['url'] = request.get('url', None)
    req['sections'] = request.get('sections', None)

    response = run_coala_online.delay(req)

    return JsonResponse(response.get(), safe=False)
