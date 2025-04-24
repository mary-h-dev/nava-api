from django.urls import path ,include



app_name = 'Psychology_workshops'



urlpatterns = [
    path("",include('django.contrib.auth.urls')),
    path('api/v1/',include('Psychology_workshops.api.v1.urls')),
]
