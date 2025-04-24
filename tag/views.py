from django_filters import rest_framework as filters
from .paginations import DefaultPagination
from config.permissions import IsAdminOrIsDoctorsOrIsSupporter
from .models import Tag
from .serializers import TagSerializer
from rest_framework import generics
# Create your views here.
class TagFilter(filters.FilterSet):
    class Meta:
        model = Tag
        fields = {
            'name': ['exact', 'icontains'],
        }
class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TagFilter
    pagination_class = DefaultPagination


class TagPost(generics.CreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]

class TagDetail(generics.RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'


class TagDelete(generics.DestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagUpdate(generics.UpdateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
