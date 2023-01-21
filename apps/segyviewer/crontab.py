from django.conf import settings
import segyio
from django.core.cache import cache
import pandas as pd
import numpy as np

BASE_DIR = settings.BASE_DIR


def caching_traces():
    filename = BASE_DIR / "templates/CDP_X18_NMO.sgy"
    with segyio.open(filename, ignore_geometry=True) as segyfile:
        if filename in cache:
            serialized_headers = cache.get(filename)
            trace_headers = pd.read_json(serialized_headers)
            headers = segyfile.header
            trace_headers.columns = headers[0].keys()
        else:
            headers = segyfile.header
            trace_headers = pd.DataFrame(data=headers, columns=headers[0].keys(), index=range(headers.length))
            serialized_headers = trace_headers.to_json()
            cache.set(filename, serialized_headers)
        traces = segyfile.trace.raw[:]

    values = trace_headers[segyio.tracefield.keys["CDP"]].unique()
    for value in values:
        trace_headers_by_value = trace_headers.loc[
            trace_headers[segyio.tracefield.keys["CDP"]] == value
            ]
        index = trace_headers_by_value.index
        return_data = []
        for i in index:
            return_data.append(traces[i].tolist())
        return_data = np.array(return_data)
        cache.set(filename + '__' + 'CDP' + value, return_data.dumps())

def caching_headers():
    filename = BASE_DIR / "templates/CDP_X18_NMO.sgy"
    with segyio.open(filename, ignore_geometry=True) as file:
        if filename in cache:
            serialized_headers = cache.get(filename)
        else:
            headers = file.header
            trace_headers = pd.DataFrame(data=headers, columns=headers[0].keys(), index=range(headers.length))
            serialized_headers = trace_headers.to_json()

        cache.set(filename, serialized_headers)
