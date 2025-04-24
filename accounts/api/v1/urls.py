from django.urls import path ,include
from accounts.api.v1 import views
from rest_framework.routers import DefaultRouter
from accounts.api.v1.views import CustomTokenRefreshView, OtpEmailLoginRequestView, OtpEmailLoginVerifyView, \
    NotificationByUser, RegisterSaleExpertView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import NotificationViewSet
router = DefaultRouter()
router.register("profile", views.ProfileViewSet, basename="Profile")
# router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)



urlpatterns = [
    path('', include(router.urls)),

    #register otp
    path(
        "signup/registration-otp/",
        views.Registration_Otp_ApiView.as_view(),
        name="registration_otp",
    ),
    #register expert sales
    path(
        "signup/register-customer/", RegisterSaleExpertView.as_view(),
         name='register_customer'
    ),
    # activation register
    path(
        "activation/confirm/",
        views.ActivationApiView.as_view(),
        name="activation",
    ),
    #login
    path(
        "jwt/otp-login/",
        views.OtpLoginRequestView.as_view(),
        name="jwt-otp_create",
    ),

    path(
        "jwt/otp-confirm/",
        views.OtpLoginConfirmView.as_view(),
        name="jwt-otp_confirm",
    ),
    #email login
    path('otp/email/login/request/', OtpEmailLoginRequestView.as_view(), name='otp-email-login-request'),
    path('otp/email/login/verify/', OtpEmailLoginVerifyView.as_view(), name='otp-email-login-verify'),
    # profile
    # path(
    #     "user/profile/",
    #     views.ProfileViewSet.as_view(),
    #     name="user_profile"
    # ),
    #panel admin login
    path(
        "jwt/panel-login/",
        views.PanelOtpLoginRequestView.as_view(),
        name="jwt-panel_create",
    ),

    path(
        "jwt/panel-confirm/",
        views.PanelOtpLoginConfirmView.as_view(),
        name="jwt-panel_confirm",
    ),

#list all user for front dev
    path(
        "user/all-user-otp/",
        views.UserListViews.as_view(),
        name="all-user",
    ),
    path(
        "user/admin-user-list/",
        views.UserAdminListViews.as_view(),
        name="alladmin-user",
    ),
    path(
        "user/panel/update/<int:pk>",
        views.UserUpdateViews.as_view(),
        name="all-userpanelupdate",
    ),
    path(
        "user/panel/detail/<int:pk>",views.UserDetailViews.as_view(),name="userpanel-detail"
    ),
    #logout
    path(
        "user/logout/",
        views.LogoutView.as_view(),
        name="logout"
    ),
   #update#
    path(
        "user/updateps/<int:pk>",
        views.UpdateProfilveiew.as_view(),
        name="change phone"
    ),
    path(
        "user/updatelist/<int:user_id>/",
        views.ProfileUserList.as_view(),
        name="profilelist"
    ),
    path("jwt/refresh/", CustomTokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/refresh1/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
##########################list user by id and permmision for front developer
    #its for notifacations
    path("notificationbyuser/<int:user_id>/", NotificationByUser.as_view(), name="notifications-by-user"),

]
