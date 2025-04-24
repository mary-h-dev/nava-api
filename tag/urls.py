from django.urls import path
from .views import TagList, TagPost,TagUpdate, TagDetail, TagDelete

urlpatterns = [
    path('api/tags/', TagList.as_view(), name='tag-list'),
    path('api/tags/post/', TagPost.as_view(), name='tag-post'),
    path('api/tags/detail/<slug>', TagDetail.as_view(), name='tag-detail'),
    path('api/tags/delete/<int:pk>', TagDelete.as_view(), name='tag-delete'),
    path('api/tags/update/<int:pk>', TagUpdate.as_view(), name='tag-update'),
]