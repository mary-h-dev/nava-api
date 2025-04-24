from django.urls import path, include
from . import views

app_name = "blog"

urlpatterns = [

    path('api/v1/',include('blog.api.v1.urls')),
]