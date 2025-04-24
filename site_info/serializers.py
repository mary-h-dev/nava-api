from rest_framework import serializers
from .models import AboutUs, Slider, Slide, Tabs, Tags, SectionType, Sections, Banner, Social_Media, SurveySite


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and not request.user.is_staff:
            fields.pop('created_at', None)
            fields.pop('updated_at', None)

        return fields


class SlideSerializer(serializers.ModelSerializer):
    class Meta:

        model = Slide
        fields = '__all__'
        read_only_fields = ('web_image',)

class SliderSerializer(serializers.ModelSerializer):
    slides = SlideSerializer(many=True, read_only=True)  # Add this line

    class Meta:
        model = Slider
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and not request.user.is_staff:
            fields.pop('is_active', None)
            fields.pop('is_published', None)
            fields.pop('created_at', None)
            fields.pop('updated_at', None)
            # fields.pop('id', None)

        return fields

class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social_Media
        fields = '__all__'

class SurveySiteSerializers(serializers.ModelSerializer):
    class Meta:
        model = SurveySite
        fields = '__all__'