from rest_framework import serializers, request
import os

from config import settings
from doctors.api.v1.serializers import DoctorSerializer
from blog.api.v1.serializers import AuthorBlogSerializers
from podcast.models import Podcast ,PodcastCategory ,CommentsPodcast

class PodcastCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastCategory
        fields = '__all__'


class PodcastListSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    author = AuthorBlogSerializers(read_only=True)
    class Meta:
        model = Podcast
        fields = '__all__'

class PodcastCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = '__all__'

class PodcastSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer()
    category = PodcastCategorySerializer()
    class Meta:
        model = Podcast
        fields = '__all__'

    def validate_file(self, value):
        max_size = getattr(settings, 'MAX_FILE_SIZE', 10 * 1024 * 1024)
        allowed_extensions = ['.mp3', '.wav', '.aac']

        # بررسی اندازه
        if value.size > max_size:
            raise serializers.ValidationError(f"File size must not exceed {max_size / (1024 * 1024)} MB.")

        # بررسی فرمت
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}")

        return value




class PodcastCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentsPodcast
        fields = '__all__'