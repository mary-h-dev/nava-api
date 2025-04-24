from django.urls import path, include

app_name = "vlog"

urlpatterns = [

    path('api/v1/',include('vlog.api.v1.urls')),
]