from rest_framework import generics
from config.permissions import IsAdminOrIsDoctorsOrIsSupporter
from .serializers import PodcastSerializer, PodcastCategorySerializer, PodcastCommentSerializer, PodcastListSerializer, \
    PodcastCreateSerializer
from ...models import Podcast, PodcastCategory, CommentsPodcast, LikePodcastPost
from .paginations import DefaultPagination ,CommentsPagination
from rest_framework import filters
from podcast.api.v1.filters import PostFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.db import IntegrityError, transaction
from django.db.models import F


##################################
class PodcastCategoryCreateViews(generics.CreateAPIView):
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    queryset = PodcastCategory.objects.all()
    serializer_class = PodcastCategorySerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    ordering_fields = '__all__'
    lookup_field = 'slug'
    ordering = ('created_at',)

class PodcastCategoryListViews(generics.ListAPIView):
    queryset = PodcastCategory.objects.all()
    serializer_class = PodcastCategorySerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ('created_at',)

    def get_queryset(self):
        queryset = PodcastCategory.objects.filter(is_active=True)
        return queryset

class PodcastCategoryDetailViews(generics.RetrieveAPIView):
    queryset = PodcastCategory.objects.all()
    serializer_class = PodcastCategorySerializer
    lookup_field = 'slug'



class PodcastCategoryUpdateViews(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    queryset = PodcastCategory.objects.all()
    serializer_class = PodcastCategorySerializer

class PodcastCategoryDeleteViews(generics.DestroyAPIView):
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    queryset = PodcastCategory.objects.all()
    serializer_class = PodcastCategorySerializer
#############################################
class PodcastCommentsModelListViews(generics.ListAPIView):
    queryset = CommentsPodcast.objects.filter(is_active=True)
    serializer_class = PodcastCommentSerializer
    pagination_class = DefaultPagination

class PodcastCommentsModelCreateViews(generics.CreateAPIView):
    queryset = CommentsPodcast.objects.all()
    serializer_class = PodcastCommentSerializer
    permission_classes = [IsAuthenticated]

class PodcastCommentsModelUpdateViews(generics.UpdateAPIView):
    queryset = CommentsPodcast.objects.all()
    serializer_class = PodcastCommentSerializer
    permission_classes = [IsAuthenticated]

class PodcastCommentsModelDetailViews(generics.RetrieveAPIView):
    queryset = CommentsPodcast.objects.all()
    serializer_class = PodcastCommentSerializer
    permission_classes = [IsAuthenticated]

class PodcastCommentsList(generics.ListAPIView):
    serializer_class = PodcastCommentSerializer
    pagination_class = CommentsPagination
    def get_queryset(self):
        Podcast_id = self.kwargs['Podcast_id']
        return CommentsPodcast.objects.filter(podcast=Podcast_id , is_active=True)

class PodcastCommentsUpdate(generics.ListAPIView):
    serializer_class = PodcastCommentSerializer
    pagination_class = CommentsPagination
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    def get_queryset(self):
        Podcast_id = self.kwargs['Podcast_id']
        return CommentsPodcast.objects.filter(Podcast_id=Podcast_id,is_active=True)
class PodcastCommentsDeleteDetail(generics.DestroyAPIView):
    serializer_class = PodcastCommentSerializer
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    def get_queryset(self):
        Podcast_id = self.kwargs['Podcast_id']
        return CommentsPodcast.objects.filter(Podcast_id=Podcast_id)
#############################################
class PodcastCreateViews(generics.CreateAPIView):
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    queryset = Podcast.objects.all()
    serializer_class = PodcastCreateSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    ordering_fields = '__all__'
    ordering = ('created_date',)



class PodcastListViews(generics.ListAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastListSerializer
    pagination_class = DefaultPagination
    ordering_fields = ['created_date', 'view_count','like_count']
    search_fields = ['title']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter,]
    filterset_class = PostFilter


class PodcastDetailViews(generics.RetrieveAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    lookup_field = 'slug'

class PodcastUpdateViews(generics.UpdateAPIView):
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer


class PodcastDeleteViews(generics.DestroyAPIView):
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer


class PodcastLikeCountView(APIView):
    def post(self, request, podcast_id):
        try:
            podcast = Podcast.objects.get(id=podcast_id)
        except Podcast.DoesNotExist:
            return Response({'error': 'Podcast not found'}, status=status.HTTP_404_NOT_FOUND)

        # بررسی اینکه کاربر قبلاً این پادکست را لایک کرده یا نه
        if LikePodcastPost.objects.filter(podcast=podcast, user=request.user).exists():
            return Response({'error': 'You have already liked this podcast'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # ایجاد لایک جدید
                LikePodcastPost.objects.create(podcast=podcast, user=request.user)
                # افزایش تعداد لایک‌ها به صورت امن در سطح دیتابیس
                Podcast.objects.filter(id=podcast_id).update(like_count=F('like_count') + 1)

            return Response({'success': 'Like added successfully'}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({'error': 'You have already liked this podcast'}, status=status.HTTP_400_BAD_REQUEST)



class PodcastVisitCountView(APIView):
    permission_classes = [IsAuthenticated]
    # pagination_class = DefaultPagination

    def get(self, request,podcast_id):
        if not podcast_id:
            return Response({'error': 'Podcast ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            podcast = Podcast.objects.get(id=podcast_id)
        except Podcast.DoesNotExist:
            return Response({'error': 'Podcast not found'}, status=status.HTTP_404_NOT_FOUND)
        if podcast.view_count is None:
            podcast.view_count = 0
        podcast.view_count += 1
        podcast.save()

        return Response({'success': 'Visit number incremented successfully'}, status=status.HTTP_200_OK)


class PodcastIdCategoryView(generics.ListAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    pagination_class = DefaultPagination
    def get_queryset(self):
        cat_id = self.kwargs['cat_id']
        queryset = Podcast.objects.filter(category_id=cat_id)
        return queryset

