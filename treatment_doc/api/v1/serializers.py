from rest_framework import serializers

from treatment_doc import models
from treatment_doc.models import Treatments


class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatments
        fields = '__all__'
        search_fields = ['Phone_number']

