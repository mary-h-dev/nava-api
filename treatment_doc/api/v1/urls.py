from rest_framework.routers import DefaultRouter
from django.urls import include, path

from treatment_doc.api.v1.views import (TreatmentViewSet ,TreatmentsCreateApi
,TreatmentsUpdateApi ,TreatmentsDeleteApi,TreatmentsListApi)

router = DefaultRouter()

router.register('treatment-doc', TreatmentViewSet, basename="treatments")


urlpatterns = [
    path('', include(router.urls)),
    path('create/', TreatmentsCreateApi.as_view(), name='doc-create-api'),
    path('list/', TreatmentsListApi.as_view(), name='doc-list-api'),
    path('update/<int:pk>', TreatmentsUpdateApi.as_view(), name='doc-update-api'),
    path('delete/<int:pk>', TreatmentsDeleteApi.as_view(), name='doc-delete-api'),

]