from django.urls import include, path

from landing_manager.api.v1.views import SubmissionLandingPageView, LandingAPIAuthorizationView, LandingCreateAPIView, \
    LandingListAPIView, LandingDetailAPIView, LandingUpdateAPIView, LandingDeleteAPIView, CampaignCreateAPIView, \
    CampaignListAPIView, CampaignDetailAPIView, CampaignUpdateAPIView, CampaignDeleteAPIView, AssetUploadView

urlpatterns = [
    # path('fn/create', FainanceCreateViews.as_view(), name='finance-create'),
    path('submit/<int:landing_page_id>/', SubmissionLandingPageView.as_view(), name='landing-page'),
    path('landing_api_authorization/', LandingAPIAuthorizationView.as_view(), name='landing_api_authorization'),
    #landing
    path('landing/create', LandingCreateAPIView.as_view(), name='landing-create'),
    path('landing/list', LandingListAPIView.as_view(), name='landing-list'),
    path('landing/<int:pk>/detail', LandingDetailAPIView.as_view(), name='landing-detail'),
    path('landing/<int:pk>/update', LandingUpdateAPIView.as_view(), name='landing-update'),
    path('landing/<int:pk>/delete', LandingDeleteAPIView.as_view(), name='landing-delete'),
    #campaign
    path('campaign/create', CampaignCreateAPIView.as_view(), name='campaign-create'),
    path('campaign/list', CampaignListAPIView.as_view(), name='campaign-list'),
    path('campaign/<int:pk>/detail', CampaignDetailAPIView.as_view(), name='campaign-detail'),
    path('campaign/<int:pk>/update', CampaignUpdateAPIView.as_view(), name='campaign-update'),
    path('campaign/<int:pk>/delete', CampaignDeleteAPIView.as_view(), name='campaign-delete'),
#
    path("landing-pages/<int:pk>/upload-assets/", AssetUploadView.as_view(), name="upload_assets"),
]