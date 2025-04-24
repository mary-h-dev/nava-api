from django.urls import path ,include

app_name = 'questions'



urlpatterns = [
    path("",include('django.contrib.auth.urls')),
    path('api/v1/',include('questions.api.v1.urls')),
]
