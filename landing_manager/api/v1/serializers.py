from rest_framework import serializers
from landing_manager.models import LandingPage, SubmissionLandingPage, Campaign


class SubmissionLandingPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionLandingPage
        fields = [
            'full_name', 'phone_number', 'utm_source', 'utm_medium',
            'utm_campaign', 'utm_content', 'utm_term', 'ip_address'
        ]

    # Validate phone number or any other custom validations
    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value
class LandingPageSerializers(serializers.ModelSerializer):
    class Meta:
        model = LandingPage
        fields = "__all__"

class CampaignPageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = "__all__"