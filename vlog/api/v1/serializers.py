from doctors.api.v1.serializers import DoctorSerializer
from doctors.models import Doctor
from vlog.models import Vlog ,Vlog_Category,CommentsVlog
from rest_framework import serializers
from rest_framework.response import Response
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class VlogSerializer(serializers.ModelSerializer):
    # doctor_user = Doctor(many=True, read_only=True, source='full_name')
    writer = DoctorSerializer(read_only=True,many=False,source='doctor')
    class Meta:
        model = Vlog
        fields = '__all__'
        # fields = ('id', 'author', 'is_active', 'description_author', 'update_date')
        # read_only_fields = ('writer',)

    def validate(self, attrs):
        file_obj = attrs.get('file')
        if file_obj and not file_obj.name.endswith('.mp3'):
            raise serializers.ValidationError("Only MP3 files are allowed.")
        return attrs


class VlogCommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = CommentsVlog
        fields = '__all__'


class VlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vlog_Category
        fields = '__all__'
        read_only_fields = ('user', )