from rest_framework.routers import DefaultRouter
from django.urls import include, path

from finance.api.v1.views import  (FainanceCreateViews,FainanceListViews,
                                   FainanceUpdateViews,FainancedeleteViews,UserBalanceListViews)

urlpatterns = [
    path('fn/create', FainanceCreateViews.as_view(), name='finance-create'),
    path('fn/list', FainanceListViews.as_view(), name='finance-list'),
    path('fn/update/<int:pk>', FainanceUpdateViews.as_view(), name='finance-update'),
    path('fn/delete/<int:pk>', FainancedeleteViews.as_view(), name='finance-delete'),
    #user balance
    path('userbalance/list', UserBalanceListViews.as_view(), name='user-balance-list')

]