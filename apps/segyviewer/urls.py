from django.urls import path, include

from . import views
from .views import FileAPIView

app_name = 'segyviewer'
urlpatterns = [
    path(r'traces', views.trace_view_set),
    path(r'headers', views.headers_view),
    path(r'values', views.column_unique_values),
    path(r'files', FileAPIView.as_view()),
    # path(r'shapes', views.trace_view_length),
]
