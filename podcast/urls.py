from django.urls import path, include
from . import views

app_name = "podcast"

urlpatterns = [

    path('api/v1/',include('podcast.api.v1.urls')),
]