from django.urls import path, include
from . import views

app_name = "appointment"

urlpatterns = [

    path('api/v1/',include('appointment.api.v1.urls')),

]