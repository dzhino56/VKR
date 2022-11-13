from django.urls import path

from . import views

app_name = 'segyviewer'
urlpatterns = [
    path(r'traces', views.trace_view_set),
    path(r'headers', views.headers_view),
    path(r'values', views.column_unique_values),
]
