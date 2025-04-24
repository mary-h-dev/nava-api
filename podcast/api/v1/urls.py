from django.urls import include, path
from podcast.api.v1.views import PodcastCreateViews, PodcastListViews, PodcastDetailViews, PodcastDeleteViews, \
    PodcastUpdateViews, PodcastCommentsModelListViews, PodcastCommentsModelCreateViews, PodcastCommentsModelUpdateViews, \
    PodcastCommentsList, PodcastCommentsModelDetailViews, PodcastLikeCountView, PodcastVisitCountView, \
    PodcastCategoryCreateViews, PodcastCategoryListViews, PodcastCategoryUpdateViews, PodcastCategoryDetailViews, \
    PodcastCategoryDeleteViews, PodcastIdCategoryView

urlpatterns = [
    path('pdc/create', PodcastCreateViews.as_view(), name='podcast-create'),
    path('pdc/list', PodcastListViews.as_view(), name='podcast-list'),
    path('pdc/detail/<slug>/', PodcastDetailViews.as_view(), name='podcast-detail'),
    path('pdc/delete/<int:pk>/', PodcastDeleteViews.as_view(), name='podcast-delete'),
    path("pdc/update/<int:pk>/", PodcastUpdateViews.as_view(), name='podcast-update'),
    path("pdc/listbyid/<int:cat_id>/", PodcastIdCategoryView.as_view(), name='podcast-id-category'),
    #category
    path('category/create',PodcastCategoryCreateViews.as_view(), name='podcast-category-create'),
    path('category/list',PodcastCategoryListViews.as_view(), name='podcast-category-list'),
    path('category/update/<int:pk>/',PodcastCategoryUpdateViews.as_view(), name='podcast-category-update'),
    path('category/detail/<slug>/',PodcastCategoryDetailViews.as_view(), name='podcast-category-detail'),
    path('category/delete/<int:pk>/',PodcastCategoryDeleteViews.as_view(), name='podcast-category-delete'),
#comments
    path('comments/list',PodcastCommentsModelListViews.as_view(), name='Podcast-comments-list'),
    path('comments/create',PodcastCommentsModelCreateViews.as_view(), name='Podcast-comments'),
    path('comments/update/<int:pk>/',PodcastCommentsModelUpdateViews.as_view(), name='Podcast-comments-Update'),
    path('comments/detail/<int:pk>/',PodcastCommentsModelDetailViews.as_view(), name='Podcast-comments-detail'),
    path('comments/<int:Podcast_id>/comments/', PodcastCommentsList.as_view(), name='Podcast-commentspdc-list'),
#like&view
    path('visitcount/<int:podcast_id>', PodcastVisitCountView.as_view(), name='product_visit'),
    path('likecount/<int:podcast_id>', PodcastLikeCountView.as_view(), name='product_like'),
]