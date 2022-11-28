from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.http import JsonResponse
import segyio
import pandas as pd

BASE_DIR = settings.BASE_DIR
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def parse_trace_headers(segyfile):
    headers = segyfile.header
    trace_headers = pd.DataFrame(data=headers, columns=headers[0].keys(), index=range(1, headers.length + 1))
    return trace_headers


def trace_view_set(request):
    filename = BASE_DIR / 'templates/CDP_X18_NMO.sgy'
    with segyio.open(filename, ignore_geometry=True) as segyfile:
        trace_headers = parse_trace_headers(segyfile)
        traces = segyfile.trace.raw[:]

    return_headers = []

    for key in request.GET:
        if key != 'sort':
            return_headers.append(key)
            trace_headers = trace_headers.loc[
                trace_headers[segyio.tracefield.keys[key]] == int(request.GET[key])
                ]
        else:
            split_data = request.GET[key].split('_', 1)
            trace_headers = trace_headers.sort_values(
                by=[segyio.tracefield.keys[split_data[0]]],
                ascending=(split_data[1].lower() != 'desc')
            )
            return_headers.append(split_data[0])
    return_data = traces[trace_headers[segyio.tracefield.keys['TraceNumber']].tolist()]

    return JsonResponse(return_data.tolist(), safe=False)


def headers_view(request):
    return JsonResponse(list(segyio.tracefield.keys.keys()), safe=False)


def get_trace_headers():
    filename = BASE_DIR / "templates/CDP_X18_NMO.sgy"
    with segyio.open(filename, ignore_geometry=True) as f:
        if filename in cache:
            serialized_headers = cache.get(filename)
            trace_headers = pd.read_json(serialized_headers)
            headers = f.header
            trace_headers.columns = headers[0].keys()
        else:
            trace_headers = parse_trace_headers(f)
            serialized_headers = trace_headers.to_json()
            cache.set(filename, serialized_headers, timeout=CACHE_TTL)
    return trace_headers


def column_unique_values(request):
    trace_headers = get_trace_headers()

    values = trace_headers[segyio.tracefield.keys[request.GET['column']]].unique().tolist()
    values.sort()
    return JsonResponse(values, safe=False)
