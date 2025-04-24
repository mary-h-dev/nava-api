from django.urls import path
from filemanager.views import FileListView,FileCreateView,FileDetailView,FileDeleteView,FileUpdateView


urlpatterns = [
    #doctors
    path("fl/", FileListView.as_view(), name='file-list'),
    path("fl/create/", FileCreateView.as_view(), name='file-create'),
    path("fl/<int:pk>/", FileDetailView.as_view(), name='file-detail'),
    path("fl/<int:pk>/delete/", FileDeleteView.as_view(), name='file-delete'),
    path("fl/<int:pk>/update/", FileUpdateView.as_view(), name='file-update'),
]