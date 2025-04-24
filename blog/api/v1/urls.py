from rest_framework.routers import DefaultRouter
from django.urls import include, path
from blog.api.v1.views import (BlogListViews, BlogCategoryModelViewSet, BlogVisitCountView
, BlogCommentsModelCreateViews, BlogCommentsModelListViews, DoctorBlogList,
                               BlogCreateViews, BlogUpdateViews, BlogLikeCountView, BlogDetailViews, BlogCommentsList,
                               BlogCommentsDeleteDetail, BlogActiveCommentsList, BlogCommentsModelUpdateViews,
                               BlogCommentsModelDetailViews, AuthorBlogList, AuthorBlogCreate, AuthorBlogUpdate,
                               AuthorBlogDelete, AuthorBlogDetail, BlogByDoctorList, BlogListByCategoryViews,
                               BlogListByTagViews, BlogDetailIdViews, BlogListBySlugCategoryViews, BlogByTagsList)

router = DefaultRouter()

# router.register('blog', BlogModelViewSet, basename="blog")
router.register('blog-category', BlogCategoryModelViewSet, basename="blog_cat")

urlpatterns = [
    path('', include(router.urls)),
    path('bg/create', BlogCreateViews.as_view(), name='blog-create'),
    path('bg/list', BlogListViews.as_view(), name='blog-list'),
    path('bg/list/<int:tags_id>/', BlogListByTagViews.as_view(), name='blog-list-tags'),
    path('bg/listbycategory/<int:category_id>/', BlogListByCategoryViews.as_view(), name='blog-list-by-category'),
    path('bg/listbycategory/<slug>/', BlogListBySlugCategoryViews.as_view(), name='blog-list-by-slugcategory'),
    path('blogdoctor/<int:doctor_id>/lists/', BlogByDoctorList.as_view(), name='blogs-by-doctor'),
    path("bg/update/<int:pk>/", BlogUpdateViews.as_view(), name='blog-update'),
    path("bg/detail/<slug>/", BlogDetailViews.as_view(), name='blog-detail'),
    path("bg/detailbyid/<int:pk>/", BlogDetailIdViews.as_view(), name='blog-detailid'),
    path("bg/tagslist/<int:tag_id>/", BlogByTagsList.as_view(), name='blog-listtags'),
    path("bg-author/list/", AuthorBlogList.as_view(),name='author-list'),
    path("bg-author/create/", AuthorBlogCreate.as_view(),name='author-create'),
    path("bg-author/update/<int:pk>/", AuthorBlogUpdate.as_view(),name='author-update'),
    path("bg-author/delete/<int:pk>/", AuthorBlogDelete.as_view(),name='author-delete'),
    path("bg-author/detail/<int:pk>/", AuthorBlogDetail.as_view(),name='author-detail'),
#comments
    path('bg-comments/list',BlogCommentsModelListViews.as_view(), name='blog-comments-list'),
    path('bg-comments/create',BlogCommentsModelCreateViews.as_view(), name='blog-comments'),
    path('bg-comments/update/<int:pk>/',BlogCommentsModelUpdateViews.as_view(), name='blog-comments-Update'),
    path('bg-comments/detail/<int:pk>/',BlogCommentsModelDetailViews.as_view(), name='blog-comments-detail'),
    path('bg-comments/<int:blog_id>/comments/', BlogCommentsList.as_view(), name='blog-commentsblog-list'),
    path('bg-comments/<int:blog_id>/comments/be_active', BlogActiveCommentsList.as_view(), name='blog-commentsblog-list'),
    path('bg-comments/<int:blog_id>/comments/<int:pk>', BlogCommentsDeleteDetail.as_view(), name='blog-commentsblog-delete'),

#like&view
    path('blogvisit/<int:blog_id>', BlogVisitCountView.as_view(), name='product_visit'),
    path('bloglike/<int:blog_id>', BlogLikeCountView.as_view(), name='product_like'),
#only doctor blog name
    path('sblg/<int:blog_id>/lblg/', DoctorBlogList.as_view(), name='blog-user-list'),

]