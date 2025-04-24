from requests import Response
from rest_framework import viewsets, status, permissions, generics

from treatment_doc.api.v1 import serializers
from treatment_doc.models import Treatments
from config import settings

User = settings.AUTH_USER_MODEL


class TreatmentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TreatmentSerializer
    queryset = Treatments.objects.all()



class TreatmentsCreateApi(generics.CreateAPIView):
    serializer_class = serializers.TreatmentSerializer
    queryset = Treatments.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class TreatmentsUpdateApi(generics.UpdateAPIView):
    serializer_class = serializers.TreatmentSerializer
    queryset = Treatments.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class TreatmentsDeleteApi(generics.DestroyAPIView):
    queryset = Treatments.objects.all()
    serializer_class = serializers.TreatmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class TreatmentsListApi(generics.ListAPIView):
    serializer_class = serializers.TreatmentSerializer
    queryset = Treatments.objects.all()
    permission_classes = [permissions.IsAuthenticated]
