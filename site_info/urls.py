from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path
from site_info.views import (AboutUsModelPostView, AboutUsModelListView, AboutUsModelDeleteView, AboutUsModelUpdateView,
                             SliderModelPostView, SliderModelListView, SliderModelDeleteView, SliderModelUpdateView,
                             SlideListView, SlideCreateView, SlideDetailView, SlideUpdateView, SlideDeleteView,
                             SocialListView, SocialCreateView, SocialDetailView, SocialUpdateView, SocialDeleteView,
                             SurveySiteListView, SurveySiteCreateView, SurveySiteDetailView, SurveySiteUpdateView,
                             SurveySiteDeleteView

                             )

router = DefaultRouter()
router.register("slide", views.SlideModelViewSet, basename="Slide")

urlpatterns = [
    path('AboutUs/', AboutUsModelListView.as_view(), name='AboutUs-list'),
    path('AboutUs/create/', AboutUsModelPostView.as_view(), name='AboutUs-create'),
    path('AboutUs/delete/<int:pk>/', AboutUsModelDeleteView.as_view(), name='recruitment-delete'),
    path('AboutUs/update/<int:pk>/', AboutUsModelUpdateView.as_view(), name='recruitment-update'),
    #slider site info
    path('slider/', SliderModelListView.as_view(), name='slider-list'),
    path('slider/create/', SliderModelPostView.as_view(), name='slider-create'),
    path('slider/delete/<int:pk>/', SliderModelDeleteView.as_view(), name='slider-delete'),
    path('slider/update/<int:pk>/', SliderModelUpdateView.as_view(), name='slider-update'),
    # slide site info
    path('slide/', SlideListView.as_view(), name='slide-list'),
    path('slide/create/', SlideCreateView.as_view(), name='slide-create'),
    path('slide/delete/<int:pk>/', SlideDeleteView.as_view(), name='slide-delete'),
    path('slide/update/<int:pk>/', SlideUpdateView.as_view(), name='slide-update'),
    path('slide/detail/<int:pk>/', SlideDetailView.as_view(), name='slide-detail'),

    #social media
    path('social/', SocialListView.as_view(), name='social-list'),
    path('social/create/', SocialCreateView.as_view(), name='social-create'),
    path('social/delete/<int:pk>/', SocialDeleteView.as_view(), name='social-delete'),
    path('social/update/<int:pk>/', SocialUpdateView.as_view(), name='social-update'),
    path('social/detail/<int:pk>/', SocialDetailView.as_view(), name='social-detail'),
    #survey form
    path('surveyform/list/', SurveySiteListView.as_view(), name='survey-form-list'),
    path('surveyform/create/', SurveySiteCreateView.as_view(), name='survey-form-create'),
    path('surveyform/detail/<int:pk>/', SurveySiteDetailView.as_view(), name='survey-form-detail'),
    path('surveyform/update/<int:pk>/', SurveySiteUpdateView.as_view(), name='survey-form-update'),
    path('surveyform/delete/<int:pk>/', SurveySiteDeleteView.as_view(), name='survey-form-delete'),
]

