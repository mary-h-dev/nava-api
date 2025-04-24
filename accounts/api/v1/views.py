import re
from rest_framework import generics, viewsets, permissions, status, request, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
import random
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from config.permissions import AdminAssistantOrIsAdmin, IsDoctorOrAdmin, IsAdminOrIsDoctorsOrIsSupporter, \
    IsAdminOrIsSupporter, AdminAssistantOrIsAdminOrIsSupporter
from accounts.api.v1.serializers import (Registration_otp_Serializer, ActivationSerializer,
                                         UserSerializerList, RefreshTokenSerializer
, OtpLoginRequestSerializer, OTPLoginConfirmSerializer, ProfileSerializer, CustomTokenRefreshSerializer,
                                         OtpEmailLoginRequestSerializer, OTPEmailLoginConfirmSerializer,
                                         OtpEmailLoginVerifySerializer
, PanelOtpLoginRequestSerializer, NotificationSerializer, CustomerRegistrationSerializer)
from accounts.models import User, Profile, Notification
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import mixins
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from kavenegar import *
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.core.mail import send_mail
from accounts.api.v1.paginations import UserPagination, DefaultPagination
from rest_framework import filters
from rest_framework.decorators import action
from .tasks import send_otp_email_task
class Registration_Otp_ApiView(generics.GenericAPIView):
    serializer_class = Registration_otp_Serializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = Registration_otp_Serializer(data=request.data)
        if serializer.is_valid():
            # if User:
            #     return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            Phone_Number = serializer.validated_data["Phone_Number"]

            # Generate a random 6-digit OTP
            confirm_otp = random.randint(10000, 99999)

            user_obj = get_object_or_404(User, Phone_Number=Phone_Number)
            user_obj.confirm_otp = confirm_otp

            # Calculate expiration time for confirm code (2 minutes from now)
            expiration_time = timezone.now() + timezone.timedelta(minutes=1)
            user_obj.confirm_otp_expiration = expiration_time
            user_obj.save()

            # Send the OTP via SMS
            ##kaveh negar
            api = KavenegarAPI(
                '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D')
            params = {'sender': '90009809', 'receptor': Phone_Number, 'message': str(confirm_otp)}
            api.sms_send(params)
            return Response({"message": "کد تایید ارسال شد."})

            response_data = response.json()
            if response.status_code != 200:
                # print(response_data)
                return Response({'error': response_data}, status=500)
            if response.status_code == 200:
                data = {
                    "Phone_Number": Phone_Number,
                    "detail": "حساب کاربری شما باموفقیت ایجاد شد.برای فعالسازی حساب کاربری لطفا کد تایید را وارد نمایید.",
                    # "detail": "User profile has been successfully created. To activate the account, enter the code sent to your phone number",
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                # Failed to send OTP via SMS
                # Handle the error accordingly
                return Response(
                    {"error": "Failed to send OTP via SMS"},
                    # {"error": "Failed to send OTP via SMS"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterSaleExpertView(generics.GenericAPIView):
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "مخاطب با موفقیت ثبت شد."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ActivationApiView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):#برای  وریفاییی ثبت نام@
    serializer_class = ActivationSerializer
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=ActivationSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
###################################
class OtpLoginRequestView(TokenObtainPairView):#درخواست otpبرای لاگین@@@@@@@@
    permission_classes = [AllowAny]
    serializer_class = OtpLoginRequestSerializer
    # throttle_classes = [OTPRateThrottle]
    # queryset = User.objects.all()
    # queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        Phone_Number = request.data.get("Phone_Number")
        # Check if the Phone_Number exists in the database
        # try:
        #     user_obj = User.objects.get(Phone_Number=Phone_Number)
        # except User.DoesNotExist:
        #     return Response({"error": "شماره تلفن وارد شده در سیستم وجود ندارد."},
        #                     status=status.HTTP_400_BAD_REQUEST)
        #validate enter phone number -field
        if Phone_Number == "":
            return Response({"error": "لطفا جای خالی را پر کنید"},status=status.HTTP_400_BAD_REQUEST)
        if len(Phone_Number) < 8:
            return Response({"error": "لطفا شماره تلفن را صحیح وارد نمایید"},status=status.HTTP_400_BAD_REQUEST)

        # mobile_regex = "^09(1[0-9]|9[0-2]|2[0-2]|0[1-5]|41|3[0,3,5-9])\d{7}$"
        # if not re.match(mobile_regex, Phone_Number):
        #     return Response({"error": "شماره تلفن صحیح وارد نمایید"}, status=status.HTTP_400_BAD_REQUEST)
        #


        # Generate a random 6-digit OTP
        confirm_otp = random.randint(10000, 99999)

        # Save the OTP and expiration tipy
        # You can use a model or any other storage mechanism of your choice
        # For simplicity, let's assume you have a User model
        user_obj, created = User.objects.get_or_create(Phone_Number=Phone_Number)
        user_obj.confirm_otp = confirm_otp
        user_obj.confirm_otp_expiration = timezone.now() + timezone.timedelta(minutes=2)

        user_obj.save()

        # Send the OTP via SMS
        api = KavenegarAPI(
            '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D')
        params = {'sender': '90009809', 'receptor': Phone_Number, 'message': str(confirm_otp)}
        api.sms_send(params)
        return Response({"message": "کد تایید ارسال شد."})
        response_data = response.json()
        if response.status_code != 200:
            return Response({'error': response_data}, status=500)
        if response.status_code == 200:
            data = {
                "Phone_Number": Phone_Number,
                "detail": "درخواست شما با موفقیت انجام شد."
                # "detail": "Your request to enter the site has been successfully completed "
                          "برای وارد شدن به حساب کاربری لطفا کد تایید ارسال شده را وارد نمایید",
                          # "To log in to your account, enter the otp sent to your phone number",
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            # Failed to send OTP via SMS
            # Handle the error accordingly
            return Response(
                {"error": "Failed to send OTP via SMS"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, )


class OtpLoginConfirmView(TokenObtainPairView):#این برای کانفریمم @@@@@@@@@@@@@@@@@@@@@@@
    serializer_class = OTPLoginConfirmSerializer
    # throttle_classes = [IPSignUpThrottle]
    def to_representation(self, instance):
        # user_obj = User.objects.get(email=instance["email"])
        user_obj = User.objects.get(Phone_Number="Phone_Number")
        user_obj.is_verified = True
        user_obj.is_active = True
        user_obj.confirm_otp = None
        user_obj.confirm_otp_expiration = None
        user_obj.save()

        return {"detail": "حساب شما با موفقیت فعال شد."}


class UserListViews(generics.ListAPIView):
    serializer_class = UserSerializerList
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["Phone_Number"]

class UserAdminListViews(generics.ListAPIView):
    serializer_class = UserSerializerList
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["Phone_Number"]

    def get_queryset(self):
        return User.objects.filter(is_staff=True ,is_superuser=True) | User.objects.filter(is_supporter=True) | User.objects.filter(is_doctor=True)


class UserDetailViews(generics.RetrieveAPIView):
    serializer_class = UserSerializerList
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class UserUpdateViews(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializerList
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    http_method_names = ['get','patch','delete']

    def get_queryset(self):
        qs = Profile.objects.all()
        if self.request.user.is_authenticated:
            return qs.filter(is_active=True, user=self.request.user)

    def perform_create(self, serializer):
        user_profile_exists = Profile.objects.filter(user=self.request.user).exists()
        if user_profile_exists:
            raise PermissionDenied("User already has a profile.")
        serializer.save(user=self.request.user)
    def validate_full_name(self, full_name):
        if full_name.strip() == "":
            raise serializers.ValidationError("لطفا نام و نام خانوادگی را پر کنید")

        if full_name == int:
            raise serializers.ValidationError("لطفا نام و نام خانوادگی را پر کنید")
    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        profile = self.get_object()
        user = profile.user
        user.email = serializer.validated_data['email']
        user.save()
        serializer.save()
#######
#profile update
class UpdateProfilveiew(generics.UpdateAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    def get_queryset(self):
        qs = Profile.objects.all()
        if self.request.user.is_authenticated:
            return qs.filter(is_active=True, user=self.request.user)

    def perform_create(self, serializer):
        user_profile_exists = Profile.objects.filter(user=self.request.user).exists()
        if user_profile_exists:
            raise PermissionDenied("User already has a profile.")
        serializer.save(user=self.request.user)
    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        profile = self.get_object()
        user = profile.user
        user.email = serializer.validated_data['email']
        user.save()
        serializer.save()

###################################
class LogoutView(GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args):
        sz = self.get_serializer(data=request.data)
        sz.is_valid(raise_exception=True)
        sz.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class OtpPhoneLoginConfirmView(TokenObtainPairView):
    serializer_class = OTPEmailLoginConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = OTPLoginConfirmSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data["phone_number"]
            otp_code = serializer.validated_data["otp_code"]

            user_obj = get_object_or_404(User, phone_number=phone_number)

            if user_obj.confirm_otp == otp_code and user_obj.confirm_otp_expiration > timezone.now():
                user_obj.is_verified = True
                user_obj.is_active = True
                user_obj.confirm_otp = None
                user_obj.confirm_otp_expiration = None
                user_obj.save()

                refresh = RefreshToken.for_user(user_obj)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                return Response({"access_token": access_token, "refresh_token": refresh_token}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


####################################
####################################
####################################
#login wih email for login exept iran
class OtpEmailLoginRequestView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = OtpEmailLoginRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        Phone_Number = serializer.validated_data['Phone_Number']

        # Generate a random 6-digit OTP
        confirm_otp = random.randint(10000, 99999)

        try:
            # Attempt to create a new user
            user_obj = User.objects.create(
                email=email,
                Phone_Number=Phone_Number,
                confirm_otp=confirm_otp,
                confirm_otp_expiration=timezone.now() + timezone.timedelta(minutes=2),
            )
        except IntegrityError:
            # If a user with the same email exists, update their OTP
            user_obj = User.objects.get(email=email)
            user_obj.confirm_otp = confirm_otp
            user_obj.confirm_otp_expiration = timezone.now() + timezone.timedelta(minutes=2)
            user_obj.save()

        # Send OTP via email
        self.send_otp_via_email(email, confirm_otp)

        return Response({"message": "OTP has been sent to your email."})

    def send_otp_via_email(self, email, confirm_otp):
        subject = 'Your One-Time Password (OTP)'
        message = f'Your OTP is: {confirm_otp}'
        from_email = settings.EMAIL_BACKEND
        recipient_list = [email]

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            # Handle email sending errors
            print(f'Error sending email: {e}')
class OtpEmailLoginRequestView1(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = OtpEmailLoginRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        Phone_Number = serializer.validated_data['Phone_Number']

        # Check if the email is registered
        # if  User.objects.filter(email=email,Phone_Number=Phone_Number).exists():
        #     return Response({"error": "The email address is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a random 6-digit OTP
        confirm_otp = random.randint(10000, 99999)

        # Save the OTP and expiration time
        user_obj, created = User.objects.get_or_create(email=email,Phone_Number=Phone_Number)
        user_obj.confirm_otp = confirm_otp
        user_obj.confirm_otp_expiration = timezone.now() + timezone.timedelta(minutes=2)
        user_obj.save()

        def send_otp_via_email(email, confirm_otp):
            subject = 'Your One-Time Password (OTP)'
            message = f'Your OTP is: {confirm_otp}'
            # from_email = settings.DEFAULT_FROM_EMAIL
            from_email = settings.EMAIL_BACKEND
            recipient_list = [email]

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
            except Exception as e:
                # Handle any exceptions that may occur during email sending
                print(f'Error sending email: {e}')
                # You can also log the error or raise a custom exception her
        # Send the OTP via email
        send_otp_via_email(email, confirm_otp)
        # Send OTP asynchronously
        # send_otp_email_task.delay(email, confirm_otp)
        return Response({"message": "OTP has been sent to your email."})



class OtpEmailLoginVerifyView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = OtpEmailLoginVerifySerializer
    def to_representation(self, instance):
        user_obj = User.objects.get(email=instance["email"])
        # pro_obj = Profile.objects.get(email=instance["email"])
        # pro_obj = Profile.objects.get(email=instance["email"])
        # user_obj = User.objects.get(Phone_Number="Phone_Number")
        user_obj.is_verified = True
        user_obj.is_active = True
        user_obj.is_abroad = True
        user_obj.confirm_otp = None
        user_obj.confirm_otp_expiration = None
        # user_obj.email = pro_obj.email
        user_obj.save()
        # pro_obj.save()


        return {"detail": "حساب شما با موفقیت فعال شد."}

##########################
###########################
##########################
#panel login

class PanelOtpLoginRequestView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = PanelOtpLoginRequestSerializer

    HTTP_400_BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    HTTP_403_FORBIDDEN = status.HTTP_403_FORBIDDEN
    HTTP_201_CREATED = status.HTTP_201_CREATED
    HTTP_500_INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("Phone_Number")

        # Validate phone number
        validation_error = self.validate_phone_number(phone_number)
        if validation_error:
            return Response(validation_error, status=self.HTTP_400_BAD_REQUEST)

        confirm_otp = random.randint(10000, 99999)

        user_obj, created = User.objects.get_or_create(Phone_Number=phone_number)

        if created:
            # New user needs admin approval
            return Response({"massage": "منتظر تایید ادمین باشید."}, status=self.HTTP_201_CREATED)

        # User exists; check if they are staff or doctor
        # User exists; check if they are staff or doctor
        if user_obj.is_staff or user_obj.is_doctor or user_obj.is_supporter or user_obj.is_superuser:
            user_obj.confirm_otp = confirm_otp
            user_obj.confirm_otp_expiration = timezone.now() + timezone.timedelta(minutes=2)
            user_obj.save()
            # self.save_otp(user_obj, confirm_otp)
            api = KavenegarAPI(
                '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D')
            params = {'sender': '90009809', 'receptor': phone_number, 'message': str(confirm_otp)}
            api.sms_send(params)
            return Response({"message": "کد تایید ارسال شد."})
            response_data = response.json()
            if response.status_code != 200:
                return Response({'error': response_data}, status=500)
            if response.status_code == 200:
                data = {
                    "Phone_Number": Phone_Number,
                    "detail": "درخواست شما با موفقیت انجام شد."
                    # "detail": "Your request to enter the site has been successfully completed "
                              "برای وارد شدن به حساب کاربری لطفا کد تایید ارسال شده را وارد نمایید",
                    # "To log in to your account, enter the otp sent to your phone number",
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                # Failed to send OTP via SMS
                # Handle the error accordingly
                return Response(
                    {"error": "Failed to send OTP via SMS"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, )

            return Response({"message": "کد تایید ارسال شد."}, status=self.HTTP_201_CREATED)

        # User exists but is not staff or doctor
        return Response({"message": "منتظر تایید ادمین باشید."}, status=self.HTTP_201_CREATED)

    def validate_phone_number(self, phone_number):
        if not phone_number:
            return {"error": "لطفا جای خالی را پر کنید"}
        if len(phone_number) < 8:
            return {"error": "لطفا شماره تلفن را صحیح وارد نمایید"}

        mobile_regex = r"^09(1[0-9]|9[0-2]|2[0-2]|0[1-5]|41|3[0-3,5-9])\d{7}$"
        if not re.match(mobile_regex, phone_number):
            return {"error": "شماره تلفن صحیح وارد نمایید"}

        return None

    def save_otp(self, user_obj, confirm_otp):
        user_obj.confirm_otp = confirm_otp
        user_obj.confirm_otp_expiration = timezone.now() + timezone.timedelta(minutes=2)
        user_obj.save()

    # def send_otp_via_sms(phone_number, confirm_otp):
    #     api = KavenegarAPI('31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D')  # Replace with your actual API key
    #     params = {
    #         'sender': 'YOUR_SENDER_NUMBER',  # Replace with your sender number
    #         'receptor': phone_number,
    #         'message': str(confirm_otp)
    #     }
    #
    #     try:
    #         response = api.sms_send(params)
    #         return response.status_code == 200
    #     except Exception as e:
    #         print(f"Error sending SMS: {e}")
    #         return False

class PanelOtpLoginConfirmView(TokenObtainPairView):#این برای کانفریمم @@@@@@@@@@@@@@@@@@@@@@@
    serializer_class = OTPLoginConfirmSerializer
    # throttle_classes = [IPSignUpThrottle]
    def to_representation(self, instance):
        user_obj = User.objects.get(Phone_Number="Phone_Number")
        user_obj.is_verified = True
        user_obj.is_active = True
        user_obj.confirm_otp = None
        user_obj.confirm_otp_expiration = None
        user_obj.save()

        return {"detail": "حساب شما ثبت شد لطفا منتظر ادمین باشید"}

###################
#notifications
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        # Only return notifications for the authenticated user
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a single notification as read."""
        notification = self.get_object()
        if notification.user != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def send_notification(self, request):
        """Send a new notification to a user."""
        user = request.user
        message = request.data.get('message', None)

        if not message:
            return Response({"detail": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

        notification = Notification.objects.create(user=user, message=message)
        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
###############notifications by user
class NotificationByUser(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        # Only return notifications for the authenticated user
        user_id = self.kwargs['user_id']

        return Notification.objects.filter(user_id=user_id)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a single notification as read."""
        notification = self.get_object()
        if notification.user != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def send_notification(self, request):
        """Send a new notification to a user."""
        user = request.user
        message = request.data.get('message', None)

        if not message:
            return Response({"detail": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

        notification = Notification.objects.create(user=user, message=message)
        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)

class ProfileUserList(generics.ListAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    def get_queryset(self):
        uesr_id = self.kwargs['user_id']
        return Profile.objects.filter(user_id=uesr_id)