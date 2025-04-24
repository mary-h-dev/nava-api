from django.urls import path
from .views import CommentReportingViewSet, ApplyCouponView, CouponApplyView, WalletView, DoctorCommentCheckListViews, \
    BlogCommentCheckListViews, NotificationUnread, SmsSenderPostView, SmsSenderListView, SmsBySenderListView, \
    SmsTemplatesCreateView, SmsTemplatesListView, SmsTemplatesDetailView, CouponListByUser, \
    ExpertsByIdAppointment, CheckActivePodcastCategoryViewSet, CheckActiveDoctorCategoryViewSet, CheckActiveBlogList, \
    CheckActivePodcastList, CheckActiveDoctorList, CheckActiveTagList, ReportUserCreateViewset, ReportUserListViewset, \
    ReportUserDetailViewset, ReportUserDeleteViewset, ReportUserUpdateViewset, LibraryBooksListView, \
    LibraryBooksCreateView, LibraryBooksDetailView, LibraryBooksUpdateView, LibraryBooksDeleteView, \
    TreatmentProcessCreateViewset, TreatmentProcessListViewset, TreatmentProcessDetailViewset, \
    TreatmentProcessUpdateViewset, TreatmentProcessDeleteViewset, SaleExpertCreateView, SaleExpertListView, \
    SaleExpertDetailView, SaleExpertUpdateView, SaleExpertDeleteView, ExpertAppointmentByUserView, \
    PackageServiceExpertList, PackageServiceAllList, ExpertAppointmentListView
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("appointment-reporting", views.CheckValidProductViewSet, basename="appointmentReporting")
router.register("comment-reporting", views.CommentReportingViewSet, basename="CommentReporting")

router.register("blogcategory-admin", views.CheckActiveCategoryViewSet, basename="blogcatactive")
router.register("coupon-active", views.CouponViewSet, basename="coupon-create")
router.register("coupon-type", views.CouponTypeViewSet, basename="coupon-type")
urlpatterns = [
    path('', include(router.urls)),
    path('apply-coupon/<int:package_service_id>/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('apply-coupon/', CouponApplyView.as_view(), name='apply-coupon'),
    path('couponbylist/<int:user_id>/', CouponListByUser.as_view(), name='coupon-bylist'),
    path('expert-list/<int:expert_id>/',ExpertsByIdAppointment.as_view(), name='expert-id-list'),
    path('wallet/add/<int:user_id>/', WalletView.as_view(), name='add_to_wallet'),
    path('DoctorCommentCheck/<int:doctor_id>/', DoctorCommentCheckListViews.as_view(), name='DoctorCommentCheck_list'),
    path('BlogCommentCheck/<int:blog_id>/', BlogCommentCheckListViews.as_view(), name='blogCommentCheck_list'),
    path('notificationunread/list/<int:user_id>/', NotificationUnread.as_view(), name='notificationsunread_list'),
    path('api/sms_messages/', SmsSenderPostView.as_view(), name='sms_sender_post'),
    path('api/sms_messages/list/', SmsSenderListView.as_view(), name='sms_sender_list'),
    path('api/sms_templates/create/', SmsTemplatesCreateView.as_view(), name='sms_templates_create'),
    path('api/sms_templates/detail/<int:pk>/', SmsTemplatesDetailView.as_view(), name='sms_templates_detail'),
    path('api/sms_templates/list/', SmsTemplatesListView.as_view(), name='sms_templates_list'),
    path('api/sms_senderid/list/<int:sender_id>/', SmsBySenderListView.as_view(), name='sms_senderid_list'),
    path('podcastcategory-admin',CheckActivePodcastCategoryViewSet.as_view(), name='podcastcategory_admin'),
    path('doctorcategory-admin',CheckActiveDoctorCategoryViewSet.as_view(), name='doctorcategory_admin'),
    path('bloglist-admin',CheckActiveBlogList.as_view(), name='blog_admin'),
    path('podcast-admin/list',CheckActivePodcastList.as_view(), name='admin-podcast-list'),
    path('doctor-admin/list',CheckActiveDoctorList.as_view(), name='admin-doctor-list'),
    path('tag-admin/list',CheckActiveTagList.as_view(), name='admin-tag-list'),
    #note booke
    path('reportuser/create', ReportUserCreateViewset.as_view(), name='reportuser-create'),
    path('reportuser/list/<int:user_id>', ReportUserListViewset.as_view(), name='reportuser-list'),
    path('reportuser/detail/<int:pk>', ReportUserDetailViewset.as_view(), name='reportuser-detail'),
    path('reportuser/update/<int:pk>', ReportUserUpdateViewset.as_view(), name='reportuser-update'),
    path('reportuser/delete/<int:pk>', ReportUserDeleteViewset.as_view(), name='reportuser-delete'),
    #TreatmentProcess
    path('reportuser/create', TreatmentProcessCreateViewset.as_view(), name='treatmentProcess-create'),
    path('reportuser/list/<int:user_id>', TreatmentProcessListViewset.as_view(), name='treatmentProcess-list'),
    path('reportuser/detail/<int:pk>', TreatmentProcessDetailViewset.as_view(), name='treatmentProcess-detail'),
    path('reportuser/update/<int:pk>', TreatmentProcessUpdateViewset.as_view(), name='treatmentProcess-update'),
    path('reportuser/delete/<int:pk>', TreatmentProcessDeleteViewset.as_view(), name='treatmentProcess-delete'),
    #book library
    path('book-library/list',LibraryBooksListView.as_view(), name='library-book-list'),
    path('book-library/create',LibraryBooksCreateView.as_view(), name='library-book-create'),
    path('book-library/detail/<int:pk>',LibraryBooksDetailView.as_view(), name='library-book-detail'),
    path('book-library/update/<int:pk>',LibraryBooksUpdateView.as_view(), name='library-book-update'),
    path('book-library/delete/<int:pk>',LibraryBooksDeleteView.as_view(), name='library-book-delete'),
    #expert sale
    path('expert-sale/create',SaleExpertCreateView.as_view(), name='expert-sale-create'),
    path('expert-sale/list',SaleExpertListView.as_view(), name='expert-sale-list'),
    path('expert-sale/list-appointment/<int:user_id>',ExpertAppointmentByUserView.as_view(), name='expert-sale-appointment'),
    path('expert-sale/appointment',ExpertAppointmentListView.as_view(), name='sale-appointment'),
    path('expert-sale/detail/<int:pk>',SaleExpertDetailView.as_view(), name='expert-sale-detail'),
    path('expert-sale/update/<int:pk>',SaleExpertUpdateView.as_view(), name='expert-sale-update'),
    path('expert-sale/delete/<int:pk>',SaleExpertDeleteView.as_view(), name='expert-sale-delete'),
    #expert package list
    path('expert-sale/package-list',PackageServiceExpertList.as_view(), name='expert-sale-package'),
    path('package-list/all',PackageServiceAllList.as_view(), name='list-all-package'),
]
