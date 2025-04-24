from django.shortcuts import render
from django.views.generic import ListView
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from filemanager.models import FileManagers
from rest_framework import generics, authentication
from .serializers import FileManagerSerializer




class FileCreateView(generics.CreateAPIView):
    queryset = FileManagers.objects.all()
    serializer_class = FileManagerSerializer
    permission_classes = [IsAuthenticated]


class FileListView(generics.ListAPIView):
    queryset = FileManagers.objects.all()
    serializer_class = FileManagerSerializer
    permission_classes = [IsAuthenticated]


class FileDetailView(generics.RetrieveAPIView):
    queryset = FileManagers.objects.all()
    serializer_class = FileManagerSerializer
    permission_classes = [IsAuthenticated]

class FileUpdateView(generics.UpdateAPIView):
    queryset = FileManagers.objects.all()
    serializer_class = FileManagerSerializer
    permission_classes = [IsAuthenticated]

class FileDeleteView(generics.DestroyAPIView):
    queryset = FileManagers.objects.all()
    serializer_class = FileManagerSerializer
    permission_classes = [IsAuthenticated]
