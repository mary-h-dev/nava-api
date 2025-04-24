from rest_framework import serializers
from accounts.models import Notification, User
from appointment.api.v1.serializers import PatientsSerializer
from cart.models import Wallet, Charge_Wallet
from doctors.api.v1.serializers import DoctorAnswerListSerializer
from podcast.models import PodcastCategory, Podcast
from tag.models import Tag
from .models import CommentReporting, Coupon, CouponType, SmsMessage, SmsTemplates, ReportUser, LibraryBookDoctor, \
    SaleExpert
from appointment.models import AppointmentFinal
from blog.models import BlogCategory, CommentsBlog, Blog
from doctors.models import DoctorComment, DoctorCategory, Doctor
from blog.models import AuthorList

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','Phone_Number']
class DoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
class CheckFinallyAppointmentSerializer(serializers.ModelSerializer):
    doctor_full_name = serializers.SerializerMethodField()
    user_phone = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()


    class Meta:
        model = AppointmentFinal
        fields = ['id','doctor_full_name','user_phone','is_finaly','service_name','week']

    def get_doctor_full_name(self, obj):
        return obj.doctor.full_name
    def get_user_phone(self,obj):
        return obj.user.Phone_Number
    def get_service_name(self,obj):
        return obj.service.name
    def get_week(self,obj):
        return obj.week.day_of_week


class CheckActiveBlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = '__all__'



class CommentReportingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReporting
        fields = '__all__'
        read_only_fields = ('user',)
    def create(self, validated_data):
        # Set the "user" field to the currently authenticated user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
        # read_only_fields = ('user',)

class CouponTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponType
        fields = '__all__'


class CouponCodeSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=100)

#############
class CouponDiscountSerializer(serializers.Serializer):
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    coupon_code = serializers.CharField(max_length=100)


##############
class AddToWalletSerializer(serializers.Serializer):
    # amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    uuid = serializers.UUIDField(required=True)  # Validates the UUID format


    # def validate_amount(self, value):
    #     if value <= 0:
    #         raise serializers.ValidationError("Amount must be positive.")
    #     return value

class CheckValidCommentsSerializers(serializers.ModelSerializer):
    Answer = DoctorAnswerListSerializer(read_only=True)
    class Meta:
        model= DoctorComment
        fields = '__all__'


class CheckValidCommentsBlogSerializers(serializers.ModelSerializer):
    class Meta:
        model= CommentsBlog
        fields = '__all__'

class NotificationlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['user', 'created_at']

class PriceFinalyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge_Wallet
        fields = '__all__'
class SmsSenderSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=500, allow_blank=True, required=False)
    user_sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    message = serializers.CharField(max_length=160)

    class Meta:
        model = SmsMessage
        fields = ['user_sender', 'user_receiver', 'message','title']

    def validate_message(self, value):
        """Optionally, validate the message"""
        if not value:
            raise serializers.ValidationError("Message cannot be empty")
        return value


class SmsSenderSerializerList(serializers.ModelSerializer):
    user_sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_receiver =UserSerializer(many=True)
    message = serializers.CharField(max_length=160)

    class Meta:
        model = SmsMessage
        fields = ['user_sender', 'user_receiver', 'message']
    def validate_message(self, value):
        """Optionally, validate the message"""
        if not value:
            raise serializers.ValidationError("Message cannot be empty")
        return value

class SmsTemplatesSerilizers(serializers.ModelSerializer):
    class Meta:
        model = SmsTemplates
        fields = '__all__'

class ExpertsAppointmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = AppointmentFinal
        fields = '__all__'

class PodcastCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastCategory
        fields = '__all__'
class DoctorCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorCategory
        fields = '__all__'
class DoctorSerializers(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
        ref_name = "DoctorSerializersV1"
class AuthorSerializers(serializers.ModelSerializer):
    class Meta:
        model = AuthorList
        fields = '__all__'

class BlogAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

class PodcastSerializers(serializers.ModelSerializer):
    doctor = DoctorSerializers()  # Remove many=True
    author = AuthorSerializers()  # Keep many=True if author is a ManyToManyField
    class Meta:
        model = Podcast
        fields = '__all__'


class TagAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ReportUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = ReportUser
        fields = '__all__'

class LibraryBookDoctorSerializers(serializers.ModelSerializer):
    class Meta:
        model = LibraryBookDoctor
        fields = '__all__'

class SaleExpertUserSerializers(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = SaleExpert
        fields = '__all__'


class SaleExpertSerializers(serializers.ModelSerializer):
    class Meta:
        model = SaleExpert
        fields = '__all__'
class AppointmentSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(write_only=True, required=False)
    factor_details = serializers.SerializerMethodField()
    coupon_details = serializers.SerializerMethodField()
    doctor = DoctorsSerializer()
    expert_sale = SaleExpertSerializers()
    patient = PatientsSerializer()
    class Meta:
        model = AppointmentFinal
        fields = "__all__"
        read_only_fields = ['days_off','is_finaly','status']
        ref_name = "AppointmentSerializerV1"  # ← اینجا یک نام یکتا قرار دهید
    def get_factor_details(self, obj):
        if obj.factors:
            return {
                "id": obj.factors.id,
                "total_price": obj.factors.total_price,
                "payment_status": obj.factors.payment_status,
                "number_factors": obj.factors.number_factors,
            }
        return None

    def get_coupon_details(self, obj):
        if obj.coupon_submit:
            try:
                return {
                    "coupon_code": obj.coupon_submit.coupon_code,
                    "valid_from": obj.coupon_submit.valid_from,
                    "valid_until": obj.coupon_submit.valid_until,
                }
            except AttributeError as e:
                print(f"Error accessing coupon fields: {e}")
        return {}
    def create(self, validated_data):
        # Extract coupon_code from the request data
        coupon_code = validated_data.pop('coupon_code', None)
        appointment = AppointmentFinal.objects.create(**validated_data)
        return appointment

    def validate_time_slot(self, value):
        if value.is_booked:
            raise serializers.ValidationError("This time slot is already booked.")
        return value