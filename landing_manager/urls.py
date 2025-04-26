from django.urls import path, include
from . import views

app_name = "landing_manager"

urlpatterns = [

    path('api/v1/',include('landing_manager.api.v1.urls')),
]