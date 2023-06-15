import json
import os

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
import segyio
import pandas as pd
import numpy as np
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.segyviewer.models import File
from .serializers import GetFilesSerializer

BASE_DIR = settings.BASE_DIR


def create_file(file, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb+') as dst:
        for chunk in file.chunks():
            dst.write(chunk)


def create_file_path(user_id, file_name):
    return BASE_DIR / 'templates' / str(user_id) / file_name


class FileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        files = File.objects.filter(user=user)
        return Response({'files': GetFilesSerializer(files, many=True).data})

    def post(self, request, format=None):
        user = self.request.user
        file_obj = request.FILES['file']
        file_name = file_obj.name
        try:
            File.objects.get(user=user, name=file_name)
            return Response({'message': 'Please, rename  file. File with such name exists'}, status=412)
        except File.DoesNotExist:
            pass
        user = self.request.user
        file_path = create_file_path(user.id, file_name)
        file = File(
            name=file_name,
            user=user,
            user_file_path=file_path,
            real_file_path=file_path
        )
        file.save()
        create_file(file_obj, file_path)

        return Response({'file': GetFilesSerializer(file, many=False).data}, status=201)

    def patch(self, request):
        return Response()


def parse_trace_headers(segyfile):
    headers = segyfile.header
    trace_headers = pd.DataFrame(data=headers, columns=headers[0].keys(), index=range(headers.length))
    return trace_headers


def get_request_params(get_values):
    trace_settings = {
        "group": {},
        "sort": {}
    }
    for key in get_values:
        if key != 'sort' and key != 'fileId':
            trace_settings['group'][key] = get_values[key]

        elif key == 'sort':
            split_data = get_values[key].split('__', 1)

            trace_settings["sort"][split_data[0]] = split_data[1].lower()

    my_keys = list(trace_settings["group"].keys())
    my_keys.sort()

    sorted_dict = {i: trace_settings["group"][i] for i in my_keys}
    trace_settings["group"] = sorted_dict

    return trace_settings


def try_to_get_from_cache(cache_name):
    if cache_name in cache:
        return cache.get(cache_name)
    else:
        return None


def create_cache_name(real_file_path, request_groups):
    cache_name = real_file_path
    for k, v in request_groups.items():
        cache_name += '_' + k + '=' + v
    return cache_name


def get_return_data(request_params, file):
    trace_headers = get_trace_headers(file)
    for key, value in request_params["group"].items():
        trace_headers = trace_headers.loc[
            trace_headers[segyio.tracefield.keys[key]] == int(value)
            ]

    cache_name = create_cache_name(file.real_file_path, request_params['group'])
    data_from_cache = try_to_get_from_cache(cache_name)

    if data_from_cache is None:
        traces_and_samples = get_trace_raw_and_samples(file)

        traces = traces_and_samples["traces"]
        samples = traces_and_samples["samples"]

        index_and_values = get_sorted_indexes_and_values(request_params, trace_headers)
        sorting_values = index_and_values['values']

        return_data = []
        data_for_cache = {
            "traces": {},
            "samples": [],
            "index": index_and_values['index'].tolist()
        }
        for i in index_and_values["index"]:
            return_data.append(traces[i])
            data_for_cache["traces"][i] = traces[i].tolist()
        data_for_cache["samples"] = samples.tolist()
        print(index_and_values['index'])
        dump = {k: v for k, v in data_for_cache.items()}

        cache.set(cache_name, json.dumps(dump))

    else:
        traces_and_samples = json.loads(data_from_cache)

        traces = traces_and_samples['traces']
        samples = np.array(traces_and_samples["samples"])

        index_and_values = get_sorted_indexes_and_values(request_params, trace_headers)
        sorting_values = index_and_values['values']

        return_data = []
        for i in index_and_values["index"]:
            return_data.append(traces[str(i)])

    np_array = np.array(return_data)
    np_array = np_array.transpose()

    return {
        "traces": np_array,
        "samples": samples,
        "sorting": sorting_values
    }


def get_sorted_indexes_and_values(request_params, trace_headers):
    for key, value in request_params["sort"].items():
        header_for_sorting = segyio.tracefield.keys[key]
        trace_headers = trace_headers.sort_values(
            by=[header_for_sorting],
            ascending=(value.lower() != 'desc')
        )

    return {
        "index": trace_headers.index,
        "values": trace_headers[header_for_sorting].values
    }


def trace_view_set(request):
    file_id = int(request.GET['fileId'])
    file = File.objects.get(pk=file_id)

    request_params = get_request_params(request.GET)
    return_data = get_return_data(request_params, file)

    return HttpResponse(json.dumps({k: v.tolist() for k, v in return_data.items()}))


@permission_classes([IsAuthenticated])
def headers_view(request):
    return JsonResponse(list(segyio.tracefield.keys.keys()), safe=False)


def get_trace_headers(file):
    filename = file.real_file_path
    cache_object_name = filename + "_headers"
    with segyio.open(filename, ignore_geometry=True) as f:
        if cache_object_name in cache:
            serialized_headers = cache.get(cache_object_name)
            trace_headers = pd.read_json(serialized_headers)
            headers = f.header
            trace_headers.columns = headers[0].keys()
        else:
            trace_headers = parse_trace_headers(f)
            serialized_headers = trace_headers.to_json()
            cache.set(cache_object_name, serialized_headers)
    return trace_headers


def get_trace_raw_and_samples(file):
    filename = file.real_file_path
    with segyio.open(filename, ignore_geometry=True) as f:
        samples = f.samples
        return {
            "samples": np.array(
                [
                    samples[0],
                    samples[-1],
                    (samples[-1] - samples[0]) / (samples.size - 1)
                ]),
            "traces": f.trace.raw[:]
        }


def column_unique_values(request):
    file_id = int(request.GET['fileId'])
    file = File.objects.get(pk=file_id)
    trace_headers = get_trace_headers(file)

    values = trace_headers[segyio.tracefield.keys[request.GET['column']]].unique().tolist()
    values.sort()
    return JsonResponse(values, safe=False)
