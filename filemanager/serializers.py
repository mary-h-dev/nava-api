from rest_framework import serializers
from filemanager.models import FileManagers

class FileManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileManagers
        fields = '__all__'