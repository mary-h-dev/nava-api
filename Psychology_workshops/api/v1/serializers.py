from rest_framework import serializers

from Psychology_workshops.models import WorkShop, WorkshopCategory, RegisterWorkshop


class WorkshopCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = WorkshopCategory
        fields = '__all__'

class WorkShopSerializers(serializers.ModelSerializer):
    class Meta:
        model = WorkShop
        fields = '__all__'

class RegisterWorkshopSerializers(serializers.ModelSerializer):
    class Meta:
        model = RegisterWorkshop
        fields = '__all__'