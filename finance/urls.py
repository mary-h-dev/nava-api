from django.urls import path, include
from . import views

app_name = "finance"

urlpatterns = [

    path('api/v1/',include('finance.api.v1.urls')),
]