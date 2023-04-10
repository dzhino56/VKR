from django.urls import path, include

from account.views import registration_view, GetCSRFToken, LoginView

app_name = 'segyviewer'
urlpatterns = [
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('register', registration_view, name='register'),
    path('csrf_cookie', GetCSRFToken.as_view()),
    path('login', LoginView.as_view()),
]
