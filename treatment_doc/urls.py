from django.urls import path, include
from . import views

app_name = "treatment"

urlpatterns = [

    path('api/v1/',include('treatment_doc.api.v1.urls')),
]