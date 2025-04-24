from django_filters import rest_framework as filters
from blog.models import Blog
class PostFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__name', lookup_expr='icontains')

    class Meta:
        model = Blog
        fields = ['tags']