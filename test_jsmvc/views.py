import json
from django.http import HttpResponse


def num_gen(request):
    start = int(request.GET.get('start', 1))
    limit = int(request.GET.get('limit', 10))
    nums = [{'num': n} for n in range(start, start+limit)]
    return HttpResponse(json.dumps(nums))
