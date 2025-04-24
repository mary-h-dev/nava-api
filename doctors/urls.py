from django.urls import path ,include

from accounts import admin

app_name = 'doctors'



urlpatterns = [
    path("",include('django.contrib.auth.urls')),
    path('api/v1/',include('doctors.api.v1.urls')),
]
