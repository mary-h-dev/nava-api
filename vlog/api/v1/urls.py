from rest_framework.routers import DefaultRouter
from django.urls import include, path

from vlog.api.v1.views import  (VlogListViews, VlogDetailViews, VlogCreateViews,
VlogUpdateViews,VlogVisitCountView,VlogCommentsModelCreateViews,VlogCommentsModelListViews,VlogCategoryModelViewSet)


router = DefaultRouter()

router.register('Vlog-category', VlogCategoryModelViewSet, basename="Vlog_cat")

urlpatterns = [
    path('', include(router.urls)),
    path('vlg/create', VlogCreateViews.as_view(), name='vlog-create'),
    path('vlg/list', VlogListViews.as_view(), name='vlog-list'),
    path("vlg/update/<int:pk>/", VlogUpdateViews.as_view(), name='vlog-update'),
    path("vlg/<int:pk>/", VlogDetailViews.as_view(), name='vlog-detail'),
#comments
    path('blog-comments/list',VlogCommentsModelListViews.as_view(), name='Vlog-comments-list'),
    path('Vlg-comments/create',VlogCommentsModelCreateViews.as_view(), name='Vlog-comments'),
#like&view
    path('vlogvisit/<int:vlog_id>', VlogVisitCountView.as_view(), name='vlog_visit'),
#     path('bloglike/<int:blog_id>', BlogLikeCountView.as_view(), name='product_like'),

]