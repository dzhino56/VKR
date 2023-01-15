from django.conf import settings
BASE_DIR = settings.BASE_DIR
import segyio
from django.core.cache import cache
import pandas as pd


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

    index = trace_headers.index
    values = trace_headers[segyio.tracefield.keys["CDP"]].unique()
    for value in values:
        trace_headers = trace_headers.loc[
            trace_headers[segyio.tracefield.keys["CDP"]] == value
            ]
        index = trace_headers.index
        for i in index:
            return_data = data.append(traces[i].tolist())


def caching_headers():
    filename = BASE_DIR / "templates/CDP_X18_NMO.sgy"
    with segyio.open(filename, ignore_geometry=True) as segyfile:
        if filename in cache:
            serialized_headers = cache.get(filename)
        else:
            headers = segyfile.header
            trace_headers = pd.DataFrame(data=headers, columns=headers[0].keys(), index=range(headers.length))
            serialized_headers = trace_headers.to_json()

        cache.set(filename, serialized_headers)
