from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated ,IsAdminUser
from django.db.models import Count
from config.permissions import IsAdminOrIsDoctorsOrIsSupporter, IsAdminOrNp, IsAdminOrIsSupporter, \
    IsAdminOrIsDoctorsOrIsSupporterOrDcAdmin
from blog.models import Blog, BlogCategory, CommentsBlog, LikeBlogPost, AuthorList
from doctors.api.v1.views import DoctorList
from .paginations import DefaultPagination ,CustomPagination ,CommentsPagination
from .serializers import BlogSerializer, BlogCategorySerializer, BlogCommentSerializers, DoctorBlogSerializer, \
    AuthorBlogSerializers, BlogListSerializer, PostBlogSerializer
from rest_framework import generics
from rest_framework import filters
from accounts.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from blog.api.v1.filters import PostFilter
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend

def pop_fields(fields_list):
    keys_to_remove = ['is_active', 'is_validated', 'slug', 'user']

    # Check if fields_list is a list
    if isinstance(fields_list, list):
        for fields in fields_list:
            for key in keys_to_remove:
                fields.pop(key, None)
    else:
        # If fields_list is a single item
        for key in keys_to_remove:
            fields_list.pop(key, None)


class BlogCategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrNp]
    serializer_class = BlogCategorySerializer
    pagination_class = DefaultPagination
    lookup_field = 'slug'
    def get_queryset(self):
        qs = BlogCategory.objects.all()
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return qs
            return qs.filter(is_active=True, user=self.request.user)

        return qs.filter(is_active=True, is_validated=True)


class BlogCommentsModelListViews(generics.ListAPIView):
    queryset = CommentsBlog.objects.filter(is_active=True)
    serializer_class = BlogCommentSerializers



class BlogCommentsModelCreateViews(generics.CreateAPIView):
    queryset = CommentsBlog.objects.all()
    serializer_class = BlogCommentSerializers
    permission_classes = [IsAuthenticated]
class BlogCommentsModelUpdateViews(generics.UpdateAPIView):
    queryset = CommentsBlog.objects.all()
    serializer_class = BlogCommentSerializers
    permission_classes = [IsAuthenticated]

class BlogCommentsModelDetailViews(generics.RetrieveAPIView):
    queryset = CommentsBlog.objects.all()
    serializer_class = BlogCommentSerializers
    permission_classes = [IsAuthenticated]
########comment detail
class BlogCommentsList(generics.ListAPIView):
    serializer_class = BlogCommentSerializers
    pagination_class = CommentsPagination
    def get_queryset(self):
        blog_id = self.kwargs['blog_id']
        return CommentsBlog.objects.filter(blog_id=blog_id , is_active=True)
###########
class BlogCommentsUpdate(generics.ListAPIView):
    serializer_class = BlogCommentSerializers
    pagination_class = CommentsPagination
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    def get_queryset(self):
        blog_id = self.kwargs['blog_id']
        return CommentsBlog.objects.filter(blog_id=blog_id,is_active=True)
############
############
class BlogActiveCommentsList(generics.ListAPIView):
    serializer_class = BlogCommentSerializers
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]

    def get_queryset(self):
        blog_id = self.kwargs['blog_id']
        queryset = CommentsBlog.objects.filter(blog_id=blog_id, active=True)

        if not queryset.exists():
            raise NotFound(detail="No active comments found for this blog.")

        return queryset
class BlogCommentsDeleteDetail(generics.DestroyAPIView):
    serializer_class = BlogCommentSerializers
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    def get_queryset(self):
        blog_id = self.kwargs['blog_id']
        return CommentsBlog.objects.filter(blog_id=blog_id)

class BlogCreateViews(generics.CreateAPIView):
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporterOrDcAdmin]
    queryset = Blog.objects.all()
    serializer_class =PostBlogSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', ]
    ordering_fields = '__all__'
    ordering = ('created_date',)




class BlogListViews(generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class =BlogSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    # ordering_fields = ['like_count',]
    search_fields = ['title', ]
    filterset_fields = [
        'like_count','view_count','created_date',

    ]
    def get_queryset(self):
        queryset = Blog.objects.filter(is_active=True,is_validated=True)
        return queryset

class BlogListByTagViews(generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class =BlogSerializer
    pagination_class = DefaultPagination
    ordering_fields = ['created_date', 'view_count','like_count']
    filterset_class = PostFilter
    def get_queryset(self):
        tags_id = self.kwargs['tags_id']
        return Blog.objects.filter(tags=tags_id)

class BlogListByCategoryViews(generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class =BlogSerializer
    pagination_class = DefaultPagination
    ordering_fields = ['created_date', 'view_count','like_count']
    filterset_class = PostFilter
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Blog.objects.filter(category_id=category_id)
class BlogListBySlugCategoryViews(generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class =BlogSerializer
    pagination_class = DefaultPagination
    ordering_fields = ['created_date', 'view_count','like_count']
    filterset_class = PostFilter
    lookup_field = 'slug'

class BlogDetailViews(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'slug'
class BlogDetailIdViews(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer




class BlogUpdateViews(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    queryset = Blog.objects.all()
    serializer_class =BlogSerializer
    # lookup_field = 'slug'



class BlogVisitCountView(APIView):
    # permission_classes = [IsAuthenticated]
    # pagination_class = DefaultPagination

    def get(self, request,blog_id):
        if not blog_id:
            return Response({'error': 'Blog ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        if blog.view_count is None:
            blog.view_count = 0
        blog.view_count += 1
        blog.save()

        return Response({'success': 'Visit number incremented successfully'}, status=status.HTTP_200_OK)


#like only

class BlogLikeCountView(APIView):
    def get(self, request, blog_id):
        if not blog_id:
            return Response({'error': 'Blog ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_authenticated:
            return Response({'error': 'برای لایک باید وارد حساب کاربری شوید'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Check if the user has already liked the blog
            like = LikeBlogPost.objects.get(blog=blog, user=request.user)
            return Response({'error': 'شما قبلا این بلاگ را لایک کرده اید'}, status=status.HTTP_400_BAD_REQUEST)
        except LikeBlogPost.DoesNotExist:
            # Create a new like object
            like = LikeBlogPost(blog=blog, user=request.user)
            try:
                like.save()
            except IntegrityError:
                # Handle the case where the like was created by another request in the meantime
                return Response({'error': 'You have already liked this blog'}, status=status.HTTP_400_BAD_REQUEST)

            # Increment the like count
            blog.like_count += 1
            blog.save()

            return Response({'success': 'LIKE number incremented successfully'}, status=status.HTTP_200_OK)
        # return Response({'error': 'you are not login'}, status=status.HTTP_401_UNAUTHORIZED)



class DoctorBlogList(generics.ListAPIView):
    serializer_class = DoctorBlogSerializer
#this field for make another endpoint for doctor id name
#query for list of doctor blog only show doctor id
    def get_queryset(self):
        #anotate filter for blog count
        query_list = User.objects.filter(is_doctor=True).annotate(blog_count=Count('blog'))
        return query_list

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AuthorBlogList(generics.ListAPIView):
    serializer_class = AuthorBlogSerializers
    queryset = AuthorList.objects.all()

class AuthorBlogCreate(generics.CreateAPIView):
    serializer_class = AuthorBlogSerializers
    queryset = AuthorList.objects.all()
    permission_classes = [IsAdminOrIsSupporter]

class AuthorBlogUpdate(generics.UpdateAPIView):
    serializer_class = AuthorBlogSerializers
    queryset = AuthorList.objects.all()
    permission_classes = [IsAdminOrIsSupporter]


class AuthorBlogDelete(generics.DestroyAPIView):
    serializer_class = AuthorBlogSerializers
    queryset = AuthorList.objects.all()
    permission_classes = [IsAdminOrIsSupporter]



class AuthorBlogDetail(generics.RetrieveAPIView):
    serializer_class = AuthorBlogSerializers
    queryset = AuthorList.objects.all()
    permission_classes = [IsAdminOrIsSupporter]



class BlogByDoctorList(generics.ListAPIView):
    serializer_class = BlogListSerializer
    queryset = Blog.objects.all()

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Blog.objects.filter(doctorname_id=doctor_id)

class BlogByTagsList(generics.ListAPIView):
    serializer_class = BlogListSerializer
    def get_queryset(self):
        tag_id = self.kwargs['tag_id']
        return Blog.objects.filter(tags__id=tag_id)