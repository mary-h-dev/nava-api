from django.urls import path, include
from . import views
from .views import WorkShopCreateAPIView, WorkShopListAPIView, WorkShopDetailAPIView, WorkShopUpdateAPIView, \
    WorkShopDeleteAPIView, WorkshopCategoryCreateAPIView, WorkshopCategoryListAPIView, WorkshopCategoryDetailAPIView, \
    WorkshopCategoryUpdateAPIView, WorkshopCategoryDeleteAPIView, RegisterWorkShopCreateAPIView, \
    RegisterWorkShopListAPIView, RegisterWorkShopDetailAPIView, RegisterWorkShopUpdateAPIView, \
    RegisterWorkShopDeleteAPIView

urlpatterns = (
    # workshopcategory
    path('WorkshopCategory/create/', WorkshopCategoryCreateAPIView.as_view(), name='WorkShopCreateAPIView'),
    path('WorkshopCategory/list/', WorkshopCategoryListAPIView.as_view(), name='WorkShopListAPIView'),
    path('WorkshopCategory/detail/<slug>/', WorkshopCategoryDetailAPIView.as_view(), name='WorkShopDetailAPIView'),
    path('WorkshopCategory/update/<int:pk>/', WorkshopCategoryUpdateAPIView.as_view(), name='WorkShopUpdateAPIView'),
    path('WorkshopCategory/delete/<int:pk>/', WorkshopCategoryDeleteAPIView.as_view(), name='WorkShopDeleteAPIView'),
    # workshop
    path('workshops/create/', WorkShopCreateAPIView.as_view(), name='WorkShopCreateAPIView'),
    path('workshops/list/', WorkShopListAPIView.as_view(), name='WorkShopListAPIView'),
    path('workshops/detail/<slug>/', WorkShopDetailAPIView.as_view(), name='WorkShopDetailAPIView'),
    path('workshops/update/<int:pk>/', WorkShopUpdateAPIView.as_view(), name='WorkShopUpdateAPIView'),
    path('workshops/delete/<int:pk>/', WorkShopDeleteAPIView.as_view(), name='WorkShopDeleteAPIView'),
    #register workshop
    path('register/create/', RegisterWorkShopCreateAPIView.as_view(), name='RegisterWorkShopCreateAPIView'),
    path('register/list/', RegisterWorkShopListAPIView.as_view(), name='RegisterWorkShopListAPIView'),
    path('register/detail/<int:pk>/', RegisterWorkShopDetailAPIView.as_view(), name='RegisterWorkShopDetailAPIView'),
    path('register/update/<int:pk>/', RegisterWorkShopUpdateAPIView.as_view(), name='RegisterWorkShopUpdateAPIView'),
    path('register/delete/<int:pk>/', RegisterWorkShopDeleteAPIView.as_view(), name='RegisterWorkShopDeleteAPIView'),
)
