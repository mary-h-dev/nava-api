from django.urls import path, include
from . import views
from .api.v1.views import ChargeWalletRequestView, ChargeWalletVerifyView

app_name = "cart"

urlpatterns = [

    path('api/v1/',include('cart.api.v1.urls')),
]