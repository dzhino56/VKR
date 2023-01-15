from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
import segyio
import pandas as pd
import time
import numpy as np

BASE_DIR = settings.BASE_DIR


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def parse_trace_headers(segyfile):
    headers = segyfile.header
    trace_headers = pd.DataFrame(data=headers, columns=headers[0].keys(), index=range(headers.length))
    return trace_headers


def trace_view_set(request):
    start = time.time()
    trace_headers = get_trace_headers()
    end = time.time()
    print("Чтение заголовков заняло: ", end - start)
    start = time.time()
    traces = get_trace_raw()
    end = time.time()
    print("Чтение всех трасс заняло: ", end - start)

    return_headers = []

    for key in request.GET:
        if key != 'sort':
            return_headers.append(key)
            trace_headers = trace_headers.loc[
                trace_headers[segyio.tracefield.keys[key]] == int(request.GET[key])
                ]
        else:
            split_data = request.GET[key].split('__', 1)
            trace_headers = trace_headers.sort_values(
                by=[segyio.tracefield.keys[split_data[0]]],
                ascending=(split_data[1].lower() != 'desc')
            )
            return_headers.append(split_data[0])
    index = trace_headers.index
    return_data = []
    for i in index:
        return_data.append(traces[i].tolist())

    np_array = np.array(return_data)
    np_array = np_array.transpose()

    # pseudo_buffer = Echo()
    # writer = csv.writer(pseudo_buffer)
    # return StreamingHttpResponse(
    #     (writer.writerow(row) for row in np_array),
    #     content_type="text/csv",
    #     headers={'Content-Disposition': 'attachment; filename="somefilename.csv"'},
    # )

    return JsonResponse(np_array.tolist(), safe=False)


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
            cache.set(filename, serialized_headers)
    return trace_headers


def get_trace_raw():
    filename = BASE_DIR / "templates/CDP_X18_NMO.sgy"
    with segyio.open(filename, ignore_geometry=True) as f:
        return f.trace.raw[:]


def column_unique_values(request):
    start = time.time()
    trace_headers = get_trace_headers()
    end = time.time()
    print("Чтение заголовков заняло: ", end - start)

    values = trace_headers[segyio.tracefield.keys[request.GET['column']]].unique().tolist()
    values.sort()
    return JsonResponse(values, safe=False)
