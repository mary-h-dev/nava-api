from django.urls import path, include
from . import views

app_name = "psychological_test"

urlpatterns = [

    path('api/v1/',include('Psychological_test.api.v1.urls')),
]