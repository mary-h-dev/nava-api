import os
import zipfile
from django.conf import settings
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from config.permissions import AdminAssistantOrIsAdminOrIsSupporter
from landing_manager.api.v1.serializers import SubmissionLandingPageSerializer, LandingPageSerializers, \
    CampaignPageSerializers
from landing_manager.models import LandingPage, SubmissionLandingPage, Campaign
import re
from django.utils import timezone
from datetime import timedelta
from django.utils.decorators import method_decorator
from .decorators import restrict_ip
from .paginations import DefaultPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status, views
from rest_framework.parsers import MultiPartParser, FormParser
from ...models import LandingPage, AssetUpload
from django.http import JsonResponse
from .utils import normalize_phone_number, get_client_ip


class SubmissionLandingPageView1(APIView):

    def get(self, request, landing_page_id):
        # Fetch landing page or return 404 if not found
        landing_page = get_object_or_404(LandingPage, id=landing_page_id)

        # Extract necessary data from query params
        data = {
            'full_name': request.GET.get('full_name', '').strip(),
            'phone_number': request.GET.get('phone_number', '').strip(),
            'utm_source': request.GET.get('utm_source', '').strip(),
            'utm_medium': request.GET.get('utm_medium', '').strip(),
            'utm_campaign': request.GET.get('utm_campaign', '').strip(),
            'utm_content': request.GET.get('utm_content', '').strip(),
            'utm_term': request.GET.get('utm_term', '').strip(),
            'ip_address': request.META.get('REMOTE_ADDR')
        }

        # Validate the data using the serializer
        serializer = SubmissionLandingPageSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing submission with the same phone number and IP address
        existing_submission = SubmissionLandingPage.objects.filter(
            landing_page=landing_page,
            ip_address=data['ip_address'],
            phone_number=data['phone_number']
        ).first()

        if existing_submission:
            return Response({
                'message': 'This phone number has already been used from this IP address.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create and save the new submission
        submission = SubmissionLandingPage.objects.create(
            landing_page=landing_page,
            full_name=data['full_name'],
            phone_number=data['phone_number'],
            utm_source=data['utm_source'],
            utm_medium=data['utm_medium'],
            utm_campaign=data['utm_campaign'],
            utm_content=data['utm_content'],
            utm_term=data['utm_term'],
            ip_address=data['ip_address'],
            status='pending'  # Default status
        )

        # Return a success response with the created submission data
        return Response({
            'utm_source': data['utm_source'],
            'utm_medium': data['utm_medium'],
            'utm_campaign': data['utm_campaign'],
            'utm_content': data['utm_content'],
            'utm_term': data['utm_term'],
            'full_name': data['full_name'],
            'phone_number': data['phone_number'],
            'landing_page': landing_page.name,
            'ip_address': data['ip_address'],
            'status': submission.status
        }, status=status.HTTP_201_CREATED)

#############2
# class SubmissionLandingPageView(APIView):
from django.utils.timezone import now
from django.db.models import Exists, OuterRef

# class SubmissionLandingPageView(generics.CreateAPIView):
#     serializer_class = SubmissionLandingPageSerializer
#     permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]
#
#     def post(self, request, landing_page_id):
#         # Fetch landing page or return 404 if not found
#         landing_page = get_object_or_404(LandingPage, id=landing_page_id)
#
#         # Extract necessary data from body
#         data = {
#             'full_name': request.data.get('full_name', '').strip(),
#             'phone_number': request.data.get('phone_number', '').strip(),
#             'utm_source': request.data.get('utm_source', '').strip(),
#             'utm_medium': request.data.get('utm_medium', '').strip(),
#             'utm_campaign': request.data.get('utm_campaign', '').strip(),
#             'utm_content': request.data.get('utm_content', '').strip(),
#             'utm_term': request.data.get('utm_term', '').strip(),
#             'ip_address': self.get_client_ip(request)
#         }
#
#         # Normalize phone number
#         try:
#             data['phone_number'] = self.normalize_phone_number(data['phone_number'])
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Validate the data using the serializer
#         serializer = SubmissionLandingPageSerializer(data=data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         # Check if phone number exists in database
#         phone_exists = SubmissionLandingPage.objects.filter(phone_number=data['phone_number']).exists()
#
#         # Set status_number based on whether the phone number exists
#         status_number = "consultation" if phone_exists else "hot"
#
#         # Check for existing submission from the same IP address within the last 24 hours
#         if SubmissionLandingPage.objects.filter(
#             ip_address=data['ip_address'],
#             created_at__gte=now() - timedelta(hours=24)
#         ).exists():
#             return Response({
#                 'message': 'This IP address has already submitted a phone number within the last 24 hours.'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         # Check if phone number already submitted from the same IP
#         if SubmissionLandingPage.objects.filter(
#             landing_page=landing_page,
#             ip_address=data['ip_address'],
#             phone_number=data['phone_number']
#         ).exists():
#             return Response({
#                 'message': 'This phone number has already been used from this IP address.'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             # Create and save the new submission
#             submission = SubmissionLandingPage.objects.create(
#                 landing_page=landing_page,
#                 full_name=data['full_name'],
#                 phone_number=data['phone_number'],
#                 utm_source=data['utm_source'],
#                 utm_medium=data['utm_medium'],
#                 utm_campaign=data['utm_campaign'],
#                 utm_content=data['utm_content'],
#                 utm_term=data['utm_term'],
#                 ip_address=data['ip_address'],
#                 status='pending',  # Default status
#                 status_number=status_number  # Set status_number dynamically
#             )
#
#             # Return a success response with the created submission data
#             return Response({
#                 'utm_source': data['utm_source'],
#                 'utm_medium': data['utm_medium'],
#                 'utm_campaign': data['utm_campaign'],
#                 'utm_content': data['utm_content'],
#                 'utm_term': data['utm_term'],
#                 'full_name': data['full_name'],
#                 'phone_number': data['phone_number'],
#                 'landing_page': landing_page.name,
#                 'ip_address': data['ip_address'],
#                 'status': submission.status,
#                 'status_number': submission.status_number  # Include in response
#             }, status=status.HTTP_201_CREATED)
#
#         except Exception as e:
#             return Response({
#                 'error': 'An error occurred while processing your request.'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#new versions
class SubmissionLandingPageView(generics.CreateAPIView):
    serializer_class = SubmissionLandingPageSerializer
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]

    def post(self, request, landing_page_id):
        """ثبت شماره تلفن همراه با بررسی‌های امنیتی و UTM پارامترها"""
        # دریافت اطلاعات صفحه لندینگ یا نمایش 404 در صورت نبود آن
        landing_page = get_object_or_404(LandingPage, id=landing_page_id)

        # دریافت اطلاعات ورودی و حذف فاصله‌های اضافی
        data = {
            'full_name': request.data.get('full_name', '').strip(),
            'phone_number': request.data.get('phone_number', '').strip(),
            'utm_source': request.data.get('utm_source', '').strip(),
            'utm_medium': request.data.get('utm_medium', '').strip(),
            'utm_campaign': request.data.get('utm_campaign', '').strip(),
            'utm_content': request.data.get('utm_content', '').strip(),
            'utm_term': request.data.get('utm_term', '').strip(),
            'ip_address': get_client_ip(request)
        }

        # بررسی اجباری بودن شماره تلفن
        if not data['phone_number']:
            return Response({'error': 'شماره تلفن الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

        # نرمال‌سازی شماره تلفن (مثلاً تبدیل به فرمت استاندارد)
        try:
            data['phone_number'] = normalize_phone_number(data['phone_number'])
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # بررسی تکراری بودن شماره تلفن در دیتابیس
        phone_exists = SubmissionLandingPage.objects.filter(phone_number=data['phone_number']).exists()
        status_number = "consultation" if phone_exists else "hot"

        # بررسی ثبت شماره از همان IP در 24 ساعت گذشته
        recent_submission = SubmissionLandingPage.objects.filter(
            ip_address=data['ip_address'],
            created_at__gte=now() - timedelta(hours=24)
        ).exists()
        if recent_submission:
            return Response({'message': 'این IP در 24 ساعت گذشته قبلاً شماره‌ای ثبت کرده است.'}, status=status.HTTP_400_BAD_REQUEST)

        # بررسی ثبت شماره از همان IP در همان لندینگ پیج
        duplicate_submission = SubmissionLandingPage.objects.filter(
            landing_page=landing_page,
            ip_address=data['ip_address'],
            phone_number=data['phone_number']
        ).exists()
        if duplicate_submission:
            return Response({'message': 'این شماره قبلاً از این IP ثبت شده است.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ذخیره اطلاعات در دیتابیس
            submission = SubmissionLandingPage.objects.create(
                landing_page=landing_page,
                full_name=data['full_name'],
                phone_number=data['phone_number'],
                utm_source=data['utm_source'],
                utm_medium=data['utm_medium'],
                utm_campaign=data['utm_campaign'],
                utm_content=data['utm_content'],
                utm_term=data['utm_term'],
                ip_address=data['ip_address'],
                status='pending',  # مقدار پیش‌فرض
                status_number=status_number  # تعیین وضعیت شماره
            )

            # پاسخ موفقیت‌آمیز همراه با اطلاعات ثبت‌شده
            return Response({
                'full_name': data['full_name'],
                'phone_number': data['phone_number'],
                'landing_page': landing_page.name,
                'ip_address': data['ip_address'],
                'utm_source': data['utm_source'],
                'utm_medium': data['utm_medium'],
                'utm_campaign': data['utm_campaign'],
                'utm_content': data['utm_content'],
                'utm_term': data['utm_term'],
                'status': submission.status,
                'status_number': submission.status_number
            }, status=status.HTTP_201_CREATED)

        except Exception:
            return Response({'error': 'خطایی در پردازش درخواست رخ داده است.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#################
#auth
class LandingAPIAuthorizationView(APIView):
    """
    Class-based API view protected by IP restriction middleware.
    """
    def get(self, request):
        # Your business logic for the API
        return Response({"message": "Access granted"}, status=status.HTTP_200_OK)

@method_decorator(restrict_ip, name='dispatch')
class LandingAPIAuthorizationView(APIView):
    """
    Class-based API view protected by IP restriction decorator.
    """
    def get(self, request):
        # Your business logic for the API
        return Response({"message": "Access granted"}, status=status.HTTP_200_OK)


class LandingCreateAPIView(generics.CreateAPIView):
    serializer_class = LandingPageSerializers
    queryset = LandingPage.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]


class LandingListAPIView(generics.ListAPIView):
    serializer_class = LandingPageSerializers
    queryset = LandingPage.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at',]
    search_fields = ['name', ]


class LandingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = LandingPageSerializers
    queryset = LandingPage.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]

class LandingUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LandingPageSerializers
    queryset = LandingPage.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]

class LandingDeleteAPIView(generics.DestroyAPIView):
    serializer_class = LandingPageSerializers
    queryset = LandingPage.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]



#campaign
class CampaignCreateAPIView(generics.CreateAPIView):
    serializer_class = CampaignPageSerializers
    queryset = Campaign.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]


class CampaignListAPIView(generics.ListAPIView):
    serializer_class = CampaignPageSerializers
    queryset = Campaign.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at',]
    search_fields = ['name', ]


class CampaignDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CampaignPageSerializers
    queryset = Campaign.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]

class CampaignUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CampaignPageSerializers
    queryset = Campaign.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]

class CampaignDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CampaignPageSerializers
    queryset = Campaign.objects.all()
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]


######################
#assets view for zip and unzip file on server
class AssetUploadView(views.APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        # Get the landing page by primary key
        landing_page = get_object_or_404(LandingPage, pk=pk)

        # Get the uploaded zip file
        zip_file = request.FILES.get('zip_file')
        if not zip_file:
            return JsonResponse({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the uploaded zip file to the model
        asset_upload = AssetUpload(landing_page=landing_page, zip_file=zip_file)
        asset_upload.save()

        # Define the extraction path
        extract_path = os.path.join(settings.MEDIA_ROOT, f"landing_pages/{landing_page.id}")
        os.makedirs(extract_path, exist_ok=True)

        # Extract the contents of the zip file
        zip_file_path = asset_upload.zip_file.path
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        return JsonResponse({"message": "Assets uploaded and extracted successfully!"}, status=status.HTTP_201_CREATED)