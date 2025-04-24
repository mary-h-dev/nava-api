from django.urls import path
from doctors.api.v1.views import (DoctorList, DoctorCreate, DoctorDetail, DoctorDelete, DoctorUpdate,
                                  CommentList, CommentCreate,
                                  CommentDetail, CommentDelete, CommentUpdate,
                                  DoctorCommentsList, DoctorAllRateList, DoctorRateCreate, DoctorRateDetail,
                                  DoctorRateList, ListCoprate,
                                  DoctorCategoryListViews, DoctorCategorycreateViews, DoctorCategoryDetailViews,
                                  DoctorCategoryUpdateViews,
                                  DoctorCategoryDeleteViews, Specializationlist, SpecializationCreate,
                                  SpecializationDelete,
                                  SpecializationDetail, SpecializationUpdate, DoctorVisitCountView, LikeCommentView,
                                  DislikeCommentView, DoctorCommentsUpdate, DoctorListByTagViews, AnswerList,
                                  AnswerCreate, AnswerDetail, AnswerDelete, AnswerUpdate, DislikeAnswerView,
                                  LikeAnswerView, RateDoctorListCreateView, RateDoctorRetrieveUpdateDeleteView,
                                  RateDoctorAveragesByDoctorView, DoctorDetailId, Doctorpatch,
                                  GenerateGoogleMeetLinkAPIView, CooprationsKindCreateView,
                                  CooprationsKindUpdateView
                                  )
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("doctorcomment", views.DoctorCommentModelViewSet, basename="doctor-comment")
urlpatterns = [
    path('', include(router.urls)),
    #doctors
    path("dc/", DoctorList.as_view(), name='doctor-list'),
    path("dctags/<int:tags_id>/", DoctorListByTagViews.as_view(), name='doctor-list-bytags'),#doctor tags
    path("dc/create/", DoctorCreate.as_view(), name='doctor-create'),
    path("dc/<slug>/detail/", DoctorDetail.as_view(), name='doctor-detail'),#detail;doctor
    path("dc/<int:pk>/detailid/", DoctorDetailId.as_view(), name='doctor-detail'),
    path("dc/<int:pk>/delete/", DoctorDelete.as_view(), name='doctor-delete'),
    path("dc/<slug>/update/", DoctorUpdate.as_view(), name='doctor-update'),
    path("dc/<int:pk>/patch/", Doctorpatch.as_view(), name='doctor-patch'),

    #####
    #google generate meet link
    path('dc/<int:doctor_id>/generate-meet-link/', GenerateGoogleMeetLinkAPIView.as_view(),
         name='generate-meet-link'),
    #doctor view'
    path('dcvisit/<int:doctor_id>', DoctorVisitCountView.as_view(), name='product_visit'),
    #doctore categeories
    path("dccategory/list", DoctorCategoryListViews.as_view(), name='doctorcategory-list'),
    path("dccategory/create/", DoctorCategorycreateViews.as_view(), name='doctorcategory-create'),
    path("dccategory/<slug>/", DoctorCategoryDetailViews.as_view(), name='doctorcategory-detail_slug'),
    path("dccategory/<int:pk>/byid/", DoctorCategoryDetailViews.as_view(), name='doctorcategory-detail'),
    path("dccategory/<slug>/delete/", DoctorCategoryDeleteViews.as_view(), name='doctorcategory-delete'),
    path("dccategory/<slug>/update/", DoctorCategoryUpdateViews.as_view(), name='doctorcategory-update'),

    #doctorcomments
    path("dccomment/list/", CommentList.as_view(), name='dccomment-list'),
    path("dccomment/create/", CommentCreate.as_view(), name='dccomment-create'),
    path("dccomment/<int:pk>/", CommentDetail.as_view(), name='dccomment-detail'),
    path("dccomment/<int:pk>/delete/", CommentDelete.as_view(), name='dccomment-delete'),
    path("dccomment/<int:pk>/update/", CommentUpdate.as_view(), name='dccomment-update'),
    ########dc
    path('comments/<int:comment_id>/like/', LikeCommentView.as_view(), name='like_comment'),
    path('comments/<int:comment_id>/dislike/', DislikeCommentView.as_view(), name='dislike_comment'),
    #see comments base the doctor name
    path('dc/<int:doctor_id>/comments/', DoctorCommentsList.as_view(), name='doctor-comments-list'),
    path('dc/<int:doctor_id>/commentsupdate/', DoctorCommentsUpdate.as_view(), name='doctor-comments-update'),
    #DoctorAnswer
    path("dcanswer/list/", AnswerList.as_view(), name='dcanswer-list'),
    path("dcanswer/create/", AnswerCreate.as_view(), name='dcanswer-create'),
    path("dcanswer/<int:pk>/", AnswerDetail.as_view(), name='dcanswer-detail'),
    path("dcanswer/<int:pk>/delete/", AnswerDelete.as_view(), name='dcanswer-delete'),
    path("dcanswer/<int:pk>/update/", AnswerUpdate.as_view(), name='dcanswer-update'),
    # path('answers/create/', DoctorAnswerCreateView.as_view(), name='doctor-answer-create'),
    #like*dislike answer comments
    path('dcanswer/<int:comment_id>/like/', LikeAnswerView.as_view(), name='like_answer'),
    path('dcanswer/<int:comment_id>/dislike/', DislikeAnswerView.as_view(), name='dislike_answer'),
    #rate doctor
    path('ratings/', RateDoctorListCreateView.as_view(), name='rate-doctor-list-create'),
    path('ratings/<int:pk>/', RateDoctorRetrieveUpdateDeleteView.as_view(), name='rate-doctor-detail'),
    path('ratings/doctor/<int:doctor_id>/averages/', RateDoctorAveragesByDoctorView.as_view(), name='rate-doctor-averages-by-doctor'),    # path("rtdc/", DoctorAllRateList.as_view(), name='doctor-list-rate'),
    # path("rtdc/create/", DoctorRateCreate.as_view(), name='doctor-create-rate'),
    # path("rtdc/deatil/<int:pk>", DoctorRateDetail.as_view(), name='doctor-detail-rate'),
    #rate bass only with doctor name
    path('srt/<int:doctor_id>/rtdc/', DoctorRateList.as_view(), name='doctor-srt-list'),
    ##cooprations kind
    path("cooprationkind/list/", ListCoprate.as_view(), name='cooprationkind-list'),
    path("cooprationkind/create", CooprationsKindCreateView.as_view(), name='cooprationkind-create'),
    path("cooprationkind/update/<int:pk>", CooprationsKindUpdateView.as_view(), name='cooprationkind-update'),
    #Specialization
    path("Specialization/list",Specializationlist.as_view(), name='Specialization-list'),
    path("Specialization/create/",SpecializationCreate.as_view(), name='Specialization-create'),
    path("Specialization/update/<int:pk>",SpecializationUpdate.as_view(), name='Specialization-update'),
    path("Specialization/delete/<int:pk>",SpecializationDelete.as_view(), name='Specialization-delete'),
    path("Specialization/detail/<int:pk>",SpecializationDetail.as_view(), name='Specialization-detail'),



]
