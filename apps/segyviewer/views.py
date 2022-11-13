from django.http import JsonResponse
import segyio
import pandas as pd


def parse_trace_headers(segyfile):
    headers = segyfile.header
    trace_headers = pd.DataFrame(data=headers, columns=headers[0].keys(), index=range(1, headers.length + 1))
    return trace_headers


def trace_view_set(request):
    filename = 'G:/Programms/PycharmProjects/VKR/templates/CDP_X18_NMO.sgy'
    with segyio.open(filename, ignore_geometry=True) as segyfile:
        trace_headers = parse_trace_headers(segyfile)

    return_headers = []

    for key in request.GET:
        if key != 'sort':
            return_headers.append(key)
            trace_headers = trace_headers.loc[trace_headers[segyio.tracefield.keys[key]] == int(request.GET[key])]
        else:
            split_data = request.GET[key].split('_', 1)
            trace_headers = trace_headers.sort_values(
                by=[segyio.tracefield.keys[split_data[0]]],
                ascending=(split_data[1].lower() != 'desc')
            )
            return_headers.append(split_data[0])
    return_headers.append('TraceNumber')
    return_data = {}
    for header in return_headers:
        return_data[header] = trace_headers[segyio.tracefield.keys[header]].tolist()

    return JsonResponse(return_data, safe=False)


def headers_view(request):
    return JsonResponse(list(segyio.tracefield.keys.keys()), safe=False)


def column_unique_values(request):
    with segyio.open('G:/Programms/PycharmProjects/VKR/templates/CDP_X18_NMO.sgy', ignore_geometry=True) as f:
        trace_headers = parse_trace_headers(f)

        values = trace_headers[segyio.tracefield.keys[request.GET['column']]].unique().tolist()
        values.sort()
        return JsonResponse(values, safe=False)
