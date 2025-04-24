from django_filters import rest_framework as filters
from podcast.models import Podcast


class PostFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__name', lookup_expr='icontains')

    class Meta:
        model = Podcast
        fields = ['tags']