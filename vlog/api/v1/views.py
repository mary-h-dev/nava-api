from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .paginations import DefaultPagination
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import filters
from vlog.api.v1.serializers import VlogSerializer ,VlogCommentSerializers,VlogCategorySerializer
from vlog.models import  Vlog ,CommentsVlog ,Vlog_Category



class VlogCategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = VlogCategorySerializer
    pagination_class = DefaultPagination
    # throttle_classes = [UserRateThrottle]

    # queryset = BlogCategory.objects.all()
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        vqs = Vlog_Category.objects.all()
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return vqs
            return vqs.filter(is_active=True, user=self.request.user)

        return vqs.filter(is_active=True, is_validated=True)



class VlogCreateViews(generics.CreateAPIView):
    queryset = Vlog.objects.all()
    serializer_class =VlogSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', ]
    ordering_fields = '__all__'
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data.get('voice')
        if file_obj and not file_obj.name.endswith('.mp3'):
            return Response({'error': 'Only MP3 files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        vlog = serializer.save()

        if vlog.free_status:
            download_url = request.build_absolute_uri(vlog.file.url)
            return Response({'download_url': download_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_201_CREATED)






class VlogListViews(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Vlog.objects.all().select_related('category__user__doctor')
    serializer_class =VlogSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content','author_full_name' ]
    ordering_fields = '__all__'




class VlogDetailViews(generics.RetrieveAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Vlog.objects.all()
    serializer_class =VlogSerializer
    ordering_fields = '__all__'


class VlogUpdateViews(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vlog.objects.all()
    serializer_class =VlogSerializer



class VlogVisitCountView(APIView):
    permission_classes = [IsAuthenticated]
    # pagination_class = DefaultPagination

    def get(self, request,vlog_id):
        if not vlog_id:
            return Response({'error': 'vlog ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vlog = Vlog.objects.get(id=vlog_id)
        except Vlog.DoesNotExist:
            return Response({'error': 'vlog not found'}, status=status.HTTP_404_NOT_FOUND)
        if vlog.view_count is None:
            vlog.view_count = 0
        vlog.view_count += 1
        vlog.save()

        return Response({'success': 'Visit number incremented successfully'}, status=status.HTTP_200_OK)

class VlogCommentsModelListViews(generics.ListAPIView):
    queryset = CommentsVlog.objects.all()
    serializer_class = VlogCommentSerializers



class VlogCommentsModelCreateViews(generics.CreateAPIView):
    queryset = CommentsVlog.objects.all()
    serializer_class = VlogCommentSerializers

