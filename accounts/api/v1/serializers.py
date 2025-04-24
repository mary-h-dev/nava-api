from django.conf import settings
from rest_framework import serializers
from accounts.models import User, Profile, Notification
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken ,TokenError
from django.core.exceptions import ValidationError
from django.utils.text import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from appointment.api.v1.serializers import PatientSerializer
from appointment.models import Patients
from ...models import Token
class PatientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = ['full_name', 'age', 'gender', 'address']
class Registration_otp_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["Phone_Number"]


    def validate(self, attrs):

        if not attrs.get("Phone_Number") or attrs.get("Phone_Number") is None:
            raise serializers.ValidationError({"Phone_Number": "شماره تلفن الزامی میباشد."})
            # raise serializers.ValidationError({"Phone_Number": "Phone_Number is required."})
        return super().validate(attrs)

    def create(self, validated_data):
        Phone_Number = validated_data["Phone_Number"]
        user = User.objects.create_user(Phone_Number=Phone_Number, password=None)
        return user
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    patient = PatientRegisterSerializer()  # سریالایزر برای اطلاعات بیمار
    class Meta:
        model = User
        fields = ['Phone_Number', 'is_active','patient']
        extra_kwargs = {
            # 'role': {'default': 'customer', 'read_only': True},
            'is_active': {'default': True, 'read_only': True},
        }
    def create(self, validated_data):
        # استخراج داده‌های بیمار
        patient_data = validated_data.pop('patient', None)
        # بررسی اینکه آیا کاربر با این شماره تلفن از قبل وجود دارد
        if User.objects.filter(Phone_Number=validated_data['Phone_Number']).exists():
            raise ValidationError({'Phone_Number': 'کاربری با این شماره تلفن قبلاً ثبت شده است.'})
        # ایجاد کاربر

        user = User.objects.create(

            Phone_Number=validated_data['Phone_Number'],  # فقط داده‌های کاربر
            email=validated_data.get('email', None),
            is_active=True
        )
        user.set_unusable_password()  # غیرفعال کردن رمز عبور
        user.save()

        # ایجاد بیمار (Patients) و اتصال آن به کاربر
        if patient_data:
            Patients.objects.create(
                user=user,
                phone_number=user.Phone_Number,  # شماره تلفن بیمار از کاربر گرفته می‌شود
                **patient_data
            )

        return user

class ActivationSerializer(serializers.Serializer):
    Phone_Number = serializers.CharField()
    confirm_otp = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        Phone_Number = data.get("Phone_Number")
        try:
            confirm_otp = (data.get("confirm_otp"))
            confirm_otp = int(confirm_otp)
        except ValueError:
            raise serializers.ValidationError("کد تایید اشتباه است.")
        # confirm_otp = int(data.get("confirm_otp"))

        user_obj = User.objects.filter(Phone_Number=Phone_Number).first()

        if not user_obj:
            raise serializers.ValidationError("کاربری با این شماره همراه یافت نشد.")
            # raise serializers.ValidationError("User with this phone_number does not exist.")

        if user_obj.is_verified:
            raise serializers.ValidationError("اکانت کاربری شما فعال شد.")
            # raise serializers.ValidationError("Your account has already been activated.")

        if user_obj.confirm_otp != confirm_otp:
            raise serializers.ValidationError("شماره ی تایید شما اشتباه است.")
            # raise serializers.ValidationError("Invalid confirmation code.")

        if user_obj.confirm_otp_expiration < timezone.now():
            raise serializers.ValidationError("کد تایید شما منقضی شده است.")
            # raise serializers.ValidationError("Confirmation code has expired.")

        return data

    def to_representation(self, instance):
        user_obj = User.objects.get(Phone_Number=instance["Phone_Number"])
        user_obj.is_verified = True
        user_obj.is_active = True
        user_obj.confirm_otp = None
        user_obj.confirm_otp_expiration = None
        user_obj.save()

        # Create refresh and access tokens for the user
        # refresh = RefreshToken.for_user(user_obj)
        # access = refresh.access_token
        # access = str(refresh.access_token)
        return {"detail": "حساب شما با موفقیت فعال شد."}
        # return {"detail": "Your account has been activated successfully."}


#*************************
class OTPLoginConfirmSerializer(serializers.Serializer):
    Phone_Number = serializers.CharField()
    otp = serializers.CharField(write_only=True)
    # class Meta:
    #     model = User
    #     fields = "__all__"

    def validate(self, attrs):
        Phone_Number = attrs.get('Phone_Number')
        otp = attrs.get('otp')
        # otp = int(otp)

        try:
            otp = int(otp)
            if otp < 0:
                raise ValueError
        except:

            raise serializers.ValidationError({"details": "کد تایید شما اشتباه است."})
            # raise serializers.ValidationError({"details": "Invalid OTP"})

        try:
            user = User.objects.get(Phone_Number=Phone_Number)
        except User.DoesNotExist:
            raise serializers.ValidationError({"phone_number": "کاربری بااین شماره همراه یافت نشد."})
            # raise serializers.ValidationError({"phone_number": "User with this phone_number does not exist."})
        ############################
        if not user.confirm_otp == otp or user.confirm_otp_expiration < timezone.now():
            raise serializers.ValidationError({"otp": "کد تایید شما اشتباه یا منقضی شده است."})

        # Set the user as active and verified
        user.is_active = True
        user.is_verified = True
        user.save()

        # Generate access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        request = self.context.get('request')
        user_agent = request.META.get('HTTP_USER_AGENT')

        if 'iOS' in user_agent:
            device_type = 'ios'
        elif 'Android' in user_agent:
            device_type = 'android'
        else:
            device_type = 'web'

        # refresh = RefreshToken.for_user(user)
        # access = AccessToken.for_user(user)


        # token = Token.objects.create(user=user, access_token=str(access), refresh_token=str(refresh))
        data = {
            'device_type': device_type,
            'Phone_Number': user.Phone_Number,
            'user_id': user.id,
            'refresh': str(refresh),
            'access': str(access),
        }
        # Set token expiration based on SIMPLE_JWT settings
        access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

        # token.access_token_expiration = timezone.now() + access_token_lifetime
        # token.refresh_token_expiration = timezone.now() + refresh_token_lifetime
        # token.save()

        return data



class OtpLoginRequestSerializer(serializers.Serializer):
    Phone_Number = serializers.CharField()

    def validate_phone_number(self, value):
        if not User.objects.filter(Phone_Number=value).exists():
            raise ValidationError("Phone number does not exist in the database.")
        return value


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class UserSerializerList(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','Phone_Number' ,'email'
            , 'date_joined', 'last_login', 'is_superuser','is_staff','is_active','is_doctor','is_supporter','is_admin_assistant','is_doctoradmin','is_seo','is_expert'
                  ,'updated_date']

        read_only_fields =('password',)


class ProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='user.Phone_Number', read_only=True)
    # get_number = serializers.CharField(source='user.get_number')
    class Meta:
        model = Profile
        fields = (
            "id", "user", "email", "phone_number", "image", "full_name","deaf","hard_hearing","hearing",
             "created_date", "updated_date", "national_code", "subject",
        )
        read_only_fields = ('user', 'created_date', 'updated_date','phone_number')
    def validate_full_name(self, value):
        if any(char.isdigit() for char in value):
            raise ValidationError("لطفا در نام خانوادگی عدد وارد نکنید.")
        if not value:
            raise serializers.ValidationError("لطفا نام و نام خانوادگی را وارد نمایید")
        return value
    def validate_subject(self, value):
        if not value:
            raise serializers.ValidationError("موضوع مشاوره را انتخاب نمایید")
        return value

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = attrs['refresh']
        refresh_token = RefreshToken(refresh)

        # Check if the refresh token is valid
        try:
            refresh_token.verify()
        except:
            raise serializers.ValidationError({"details": "Invalid refresh token"})

        # Obtain the user ID from the refresh token payload
        user_id = refresh_token.payload.get('user_id')  # Replace 'user_id' with the appropriate key from your payload

        # Obtain the user object using the user ID
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"details": "User does not exist"})

        # Obtain a new access token for the user
        # Update the existing access token for the user
        access = AccessToken.for_user(user)
        token = Token.objects.get(refresh_token=refresh)
        token.access_token = str(access)
        token.save()

        # Add any additional data you want to include in the response
        data = {
            'access': str(access),
            'refresh': str(refresh_token),
        }

        access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']

        token.access_token_expiration = timezone.now() + access_token_lifetime
        token.save()

        return data
#################

# class CustomTokenRefreshSerializer(TokenRefreshSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)
#         refresh_token = RefreshToken(attrs['refresh'])
#
#         # Add custom claims back to the refreshed access token
#         user_id = refresh_token.payload.get('user_id')
#         if user_id:
#             try:
#                 from accounts.models import User  # Replace 'myapp' with your app name
#                 user = User.objects.get(id=user_id)
#                 payload = custom_jwt_payload(user)
#                 for key, value in payload.items():
#                     refresh_token.access_token[key] = value
#             except User.DoesNotExist:
#                 raise serializers.ValidationError({"details": "User not found."})
#
#         data['access'] = str(refresh_token.access_token)
#         return data

# class OtpEmailLoginRequestSerializer(serializers.Serializer):
#     Phone_Number = serializers.CharField()
#     email = serializers.EmailField()


#################################################
#################################################
#################################################
#login with email
class OTPEmailLoginConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp_code = serializers.IntegerField(required=True)

class OtpEmailLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    Phone_Number = serializers.IntegerField(required=True)
    # def validate(self, attrs):
    #     email = attrs.get('email')
    #     phone_number = attrs.get('Phone_Number')
    #
    #     # Assuming you have a model `User` with fields `email` and `phone_number`
    #     email_exists = User.objects.filter(email=email).exists()
    #     phone_exists = User.objects.filter(Phone_Number=phone_number).exists()

        # if email_exists or phone_exists:
        #     raise serializers.ValidationError({
        #         "details": "ایمیل یا شماره تلفن در سیستم موجود است."
        #     })

        # return attrs


class OtpEmailLoginVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirm_otp = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('confirm_otp')
        # otp = int(otp)

        try:
            otp = int(otp)
            if otp < 0:
                raise ValueError
        except:

            raise serializers.ValidationError({"details": "کد تایید شما اشتباه است."})
            # raise serializers.ValidationError({"details": "Invalid OTP"})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "کاربری بااین ایمیل یافت نشد."})
            # raise serializers.ValidationError({"phone_number": "User with this phone_number does not exist."})
        ############################
        if not user.confirm_otp == otp or user.confirm_otp_expiration < timezone.now():
            raise serializers.ValidationError({"otp": "کد تایید شما اشتباه یا منقضی شده است."})

        # Set the user as active and verified
        user.is_active = True
        user.is_verified = True
        user.save()

        # Generate access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        request = self.context.get('request')
        # user_agent = request.META.get('HTTP_USER_AGENT')
        #
        # if 'iOS' in user_agent:
        #     device_type = 'ios'
        # elif 'Android' in user_agent:
        #     device_type = 'android'
        # else:
        #     device_type = 'web'

        # refresh = RefreshToken.for_user(user)
        # access = AccessToken.for_user(user)


        # token = Token.objects.create(user=user, access_token=str(access), refresh_token=str(refresh))
        data = {
            # 'device_type': device_type,
            'Phone_Number': user.Phone_Number,
            'email': user.email,
            'user_id': user.id,
            'refresh': str(refresh),
            'access': str(access),
        }
        # Set token expiration based on SIMPLE_JWT settings
        access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

        # token.access_token_expiration = timezone.now() + access_token_lifetime
        # token.refresh_token_expiration = timezone.now() + refresh_token_lifetime
        # token.save()

        return data
###################################################
###################################################
##################################################
#panel login
class PanelOtpLoginRequestSerializer(serializers.Serializer):
    Phone_Number = serializers.CharField()

    def validate_phone_number(self, value):
        if not User.objects.filter(Phone_Number=value).exists():
            raise ValidationError("Phone number does not exist in the database.")
        return value


class PanelOTPLoginConfirmSerializer(serializers.Serializer):
    Phone_Number = serializers.CharField()
    otp = serializers.CharField(write_only=True)
    # class Meta:
    #     model = User
    #     fields = "__all__"

    def validate(self, attrs):
        Phone_Number = attrs.get('Phone_Number')
        otp = attrs.get('otp')
        # otp = int(otp)

        try:
            otp = int(otp)
            if otp < 0:
                raise ValueError
        except:

            raise serializers.ValidationError({"details": "کد تایید شما اشتباه است."})
            # raise serializers.ValidationError({"details": "Invalid OTP"})

        try:
            user = User.objects.get(
                Phone_Number=Phone_Number,
                is_superuser=True  # Check for superuser
            ) or User.objects.get(
                Phone_Number=Phone_Number,
                is_doctor=True  # Check for doctor
            ) or User.objects.get(
                Phone_Number=Phone_Number,
                is_staff=True  # Check for staff
            ) or User.objects.get(Phone_Number=Phone_Number,
                                  is_supporter=True )
        except User.DoesNotExist:
            raise serializers.ValidationError({"phone_number": "کاربری بااین شماره همراه مجاز برای ورود مجاز نیست ."})
            # raise serializers.ValidationError({"phone_number": "User with this phone_number does not exist."})
        ############################
        if not user.confirm_otp == otp or user.confirm_otp_expiration < timezone.now():
            raise serializers.ValidationError({"otp": "کد تایید شما اشتباه یا منقضی شده است."})

        # Set the user as active and verified
        user.is_active = True
        user.is_verified = True
        user.save()

        # Generate access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        request = self.context.get('request')
        user_agent = request.META.get('HTTP_USER_AGENT')

        if 'iOS' in user_agent:
            device_type = 'ios'
        elif 'Android' in user_agent:
            device_type = 'android'
        else:
            device_type = 'web'

        # refresh = RefreshToken.for_user(user)
        # access = AccessToken.for_user(user)


        # token = Token.objects.create(user=user, access_token=str(access), refresh_token=str(refresh))
        data = {
            'device_type': device_type,
            'Phone_Number': user.Phone_Number,
            'user_id': user.id,
            'refresh': str(refresh),
            'access': str(access),
        }
        # Set token expiration based on SIMPLE_JWT settings
        access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

        # token.access_token_expiration = timezone.now() + access_token_lifetime
        # token.refresh_token_expiration = timezone.now() + refresh_token_lifetime
        # token.save()

        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['user', 'created_at']