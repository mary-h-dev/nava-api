from rest_framework import serializers

from Panel_Admin.models import Coupon
from doctors.api.v1.serializers import DoctorSerializer
from doctors.models import Doctor
from appointment.models import (Patients, OrderVisit, PaymentVisit, PaymentGatewayVisit, StaffMember, AppointmentFinal,
                                AppointmentReminder, PackageService, TimeStamped, OrderPackage, AvailableTimeSlot)
from appointment.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
class DoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
        ref_name = "DoctorsSerializer"

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = '__all__'
    # def validate_phone_number(self, value):
    #     # Ensure phone number contains only digits and is valid
    #     if not value.isdigit():
    #         raise serializers.ValidationError("Phone number must contain only digits.")
    #     if len(value) > 20:
    #         raise serializers.ValidationError("Phone number is too long.")
    #     return value

class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorsSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = AppointmentFinal
        fields = '__all__'

class PaymentGatewayVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayVisit
        fields = '__all__'

class PaymentVisitSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)
    gateway = PaymentGatewayVisitSerializer(read_only=True)

    class Meta:
        model = PaymentVisit
        fields = '__all__'

# class OrderSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = OrderVisit
#         fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderVisit
        fields = '__all__'
        read_only_fields = ['total_amount','user','doctor','patient']
        # read_only_fields = ('')



class OrderPaySerializer(serializers.ModelSerializer):
    # trackId = serializers.ReadOnlyField(source='ordervisit.trackId')
    # order_item = OrderItemSerializer(many=True, read_only=True)
    # total_price = serializers.SerializerMethodField()
    # buy_link = serializers.SerializerMethodField()

    class Meta:
        model = OrderVisit
        fields = '__all__'
        read_only_fields = ('user', )

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['user'] = {
    #         'id': instance.user.id,
    #         'email': instance.user.email
    #     }
    #     return data

    # def get_total_price(self, order):
    #     total = 0
    #     for order_item in order.order_item.all():
    #         # if order_item.producttype.discount_price is not None:
    #         #     total += order_item.qty * order_item.producttype.discount_price
    #         if order_item.producttype.final_price is not None and order_item.producttype.final_price != 0:
    #             total += order_item.qty * order_item.producttype.final_price
    #
    #     return total



class SendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderVisit
        fields = '__all__'
        read_only_fields = ('total_amount','is_paid','payment_date','address','expired_amount','created_at','appointmentfinal')


class AppointmentreqSerializer(serializers.ModelSerializer):
    Phone_Number = serializers.CharField(read_only=True)


    class Meta:
        model = AppointmentFinal
        fields = '__all__'
    def validate_phone_number(self, value):
        if not User.objects.filter(Phone_Number=value).exists():
            raise ValidationError("Phone number does not exist in the database.")
        return value



class AppointmentReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentReminder
        fields = '__all__'
        # read_only_fields = ['sent', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        return AppointmentReminder.objects.create(user=user, **validated_data)

class PackageServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageService
        fields = '__all__'
class AppointmentFinalSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(write_only=True, required=False)
    factor_details = serializers.SerializerMethodField()
    coupon_details = serializers.SerializerMethodField()
    class Meta:
        model = AppointmentFinal
        fields = "__all__"
        read_only_fields = ['days_off','is_finaly','status']
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
#####appfinal by patient

#####
class AppointmentFinalDateDcSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(write_only=True, required=False)
    time_slot_id = serializers.PrimaryKeyRelatedField(source='time_slot', read_only=True)
    time_slot_data = serializers.SerializerMethodField()  # Custom method for displaying time slot date
    doctorname_full_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    class Meta:
        model = AppointmentFinal
        fields = "__all__"
        read_only_fields = ['days_off','is_finaly','status']
    def create(self, validated_data):
        # Extract coupon_code from the request data
        coupon_code = validated_data.pop('coupon_code', None)
        appointment = AppointmentFinal.objects.create(**validated_data)
        return appointment
    def validate_time_slot(self, value):
        if value.is_booked:
            raise serializers.ValidationError("This time slot is already booked.")
        return value
    def get_time_slot_data(self, obj):
        # Return the date from the time_slot object, assuming it has a `date` field
        return obj.time_slot.date if obj.time_slot else None
    def get_doctorname_full_name(self, obj):
        # if obj.doctorname_full_name :
        return obj.doctor.full_name
    def get_patient_name(self, obj):
        return obj.patient.full_name













class AppointmentFinalByDcSerializer(serializers.ModelSerializer):
    # coupon_code = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = AppointmentFinal
        fields = "__all__"
        read_only_fields = ['days_off','is_finaly','status','coupon_code','price_approved']
    def create(self, validated_data):
        # Extract coupon_code from the request data
        appointment = AppointmentFinal.objects.create(**validated_data)
        return appointment
    def validate_time_slot(self, value):
        if value.is_booked:
            raise serializers.ValidationError("This time slot is already booked.")
        return value
####################new
class AppointmentFinalySerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentFinal
        fields = '__all__'  # Include fields as per your requirement

    def validate(self, attrs):
        # Get the selected staff member and package service
        staff_member_id = attrs.get('doctor_available')
        package_service_id = attrs.get('package')

        # Check if the staff member exists
        if staff_member_id:
            try:
                staff_member = StaffMember.objects.get(id=staff_member_id)
            except StaffMember.DoesNotExist:
                raise serializers.ValidationError("Staff member does not exist.")

            # Validate if the selected package service is offered by the staff member
            if package_service_id:
                if not staff_member.services_offered.filter(id=package_service_id).exists():
                    raise serializers.ValidationError("The selected package service is not offered by this staff member.")

        return attrs
class AvailableTimeSlotSerializers(serializers.ModelSerializer):

    class Meta:
        model = AvailableTimeSlot
        fields = '__all__'
class TimeStampedSerializer(serializers.ModelSerializer):
    session_type = serializers.MultipleChoiceField(
        choices=[('online', 'انلاین'),
                 ('person', 'حضوری'),
                 ('call', 'تلفنی')],
        required=True
    )

    def validate_session_type(self, value):
        print(f"Received session_type: {value}")  # برای دیباگ
        return value

    def validate(self, attrs):
        print(f"Attributes before save: {attrs}")  # بررسی مقدار کل
        return super().validate(attrs)

    class Meta:
        model = TimeStamped
        fields = "__all__"
    # def validate(self, attrs):
    #     doctor = attrs.get('doctor')
    #     available_time_slot = attrs.get('available_time_slot')
    #     date = attrs.get('date')
    #
    #     # Check if the current object is being updated (i.e., has an id)
    #     instance = self.instance
    #
    #     # If updating, skip the duplicate check for the current object
    #     if instance:
    #         # Exclude the current instance if we're updating
    #         if TimeStamped.objects.filter(
    #             doctor=doctor,
    #             available_time_slot=available_time_slot,
    #             date=date
    #         ).exclude(id=instance.id).exists():
    #             raise serializers.ValidationError(
    #                 {"non_field_errors": "This time slot is already assigned for this doctor and date."}
    #             )
    #     else:
    #         # If creating a new instance, perform the usual check
    #         if TimeStamped.objects.filter(
    #             doctor=doctor,
    #             available_time_slot=available_time_slot,
    #             date=date
    #         ).exists():
    #             raise serializers.ValidationError(
    #                 {"non_field_errors": "This time slot is already assigned for this doctor and date."}
    #             )
    #
    #     return attrs
    def validate(self, attrs):
        doctor = attrs.get('doctor')
        available_time_slot = attrs.get('available_time_slot')
        date = attrs.get('date')
        session = attrs.get('session')

        # Check if a TimeStamped entry already exists
        if TimeStamped.objects.filter(doctor=doctor, available_time_slot=available_time_slot, date=date,session_type=session).exists():
            raise serializers.ValidationError("This time slot is already taken for the selected doctor on this date.")

        return attrs
    def get_available_time_slot(self, obj):
        time_slots = obj.available_time_slot.all()
        return AvailableTimeSlotSerializers(time_slots, many=True).data

class TimeStampedByDoctorSerializer(serializers.ModelSerializer):
    available_time_slot = AvailableTimeSlotSerializers(many=False, read_only=True)  # Adjust as needed
    class Meta:
        model = TimeStamped
        fields = "__all__"

    def get_available_time_slot(self, obj):
        time_slots = obj.available_time_slot.all()
        return AvailableTimeSlotSerializers(time_slots, many=True).data

class StaffMemberSerializer(serializers.ModelSerializer):
    services_offered = PackageServiceSerializer(many=True, read_only=True)
    time_stamps = TimeStampedSerializer(many=True, read_only=True)

    # time_stamps = serializers.SerializerMethodField()

    class Meta :
        model = StaffMember
        fields = '__all__'
    # def get_time_stamps(self,obj):
    #     return TimeStampedSerializer(obj.TimeStamped.all(),many=True).data

# class StaffMemberCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StaffMember
#         fields = '__all__'

class StaffMemberCreateSerializer0(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = '__all__'

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        services_offered = attrs.get('services_offered')
        time_stamps = attrs.get('time_stamps')

        # Check for unique combination of doctor, time_stamps, and services_offered
        if StaffMember.objects.filter(
            doctor=doctor,
            services_offered__in=services_offered,
            time_stamps__in=time_stamps
        ).exists():
            raise serializers.ValidationError({
                "detail": "A staff member with the same doctor, services, and time slots already exists."
            })

        # Additional check: Ensure there are no duplicates in the provided `time_stamps`
        unique_time_stamps = set()
        for ts in time_stamps:
            if ts.id in unique_time_stamps:
                raise serializers.ValidationError({
                    "time_stamps": "Duplicate time slots are not allowed."
                })
            unique_time_stamps.add(ts.id)

        return attrs
class StaffMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = '__all__'
    def validate(self, attrs):
        doctor = attrs.get('doctor')
        services_offered = attrs.get('services_offered')
        time_stamps = attrs.get('time_stamps')

        # Check for unique combination of doctor, time_stamps, and services_offered
        # if StaffMember.objects.filter(
        #     doctor=doctor,
        #     services_offered__in=services_offered,
        #     time_stamps__in=time_stamps
        # ).exists():
        #     raise serializers.ValidationError({
        #         "detail": "A staff member with the same doctor, services, and time slots already exists."
        #     })

        # Additional check: Ensure there are no duplicates in the provided time_stamps
        unique_time_stamps = set()
        for ts in time_stamps:
            if ts.id in unique_time_stamps:
                raise serializers.ValidationError({
                    "time_stamps": "Duplicate time slots are not allowed."
                })
            unique_time_stamps.add(ts.id)

        return attrs
    # def validate(self, attrs):
    #     doctor = attrs.get('doctor')
    #     services_offered = attrs.get('services_offered')  # ManyToManyField of PackageService
    #     time_stamps = attrs.get('time_stamps')  # ManyToManyField of TimeStamped
    #
    #     # دیکشنری برای ترجمه وضعیت‌های فارسی به انگلیسی
    #     status_translation = {
    #         'حضوری': 'person',
    #         'آنلاین': 'online',
    #         'تلفنی': 'call'
    #     }
    #
    #     # جمع‌آوری تمامی وضعیت‌های مجاز از پکیج‌ها
    #     allowed_visite_types = set()
    #     for service in services_offered:
    #         if service.visite_type:  # اگر `visite_type` تنظیم شده باشد
    #             allowed_visite_types.add(service.visite_type)
    #
    #     for time_stamp in time_stamps:
    #         # تبدیل session_type به معادل انگلیسی
    #         session_types = (
    #             [status_translation.get(type, type) for type in time_stamp.session_type]
    #             if isinstance(time_stamp.session_type, list)
    #             else [status_translation.get(time_stamp.session_type, time_stamp.session_type)]
    #         )
    #
    #         # بررسی اینکه هر session_type باید حداقل در یکی از allowed_visite_types باشد
    #         for session_type in session_types:
    #             if session_type not in allowed_visite_types:
    #                 raise serializers.ValidationError({
    #                     "detail": f"Session type '{session_type}' in TimeStamped is not allowed. Allowed types: {', '.join(allowed_visite_types)}"
    #                 })
    #
    #     # بررسی اینکه آیا ترکیب doctor, services_offered و time_stamps یکتا باشد
    #     if StaffMember.objects.filter(
    #         doctor=doctor,
    #         services_offered__in=services_offered,
    #         time_stamps__in=time_stamps
    #     ).exists():
    #         raise serializers.ValidationError({
    #             "detail": "A staff member with the same doctor, services, and time slots already exists."
    #         })
    #
    #     # بررسی عدم وجود تایم‌اسلات تکراری
    #     unique_time_stamps = set()
    #     for ts in time_stamps:
    #         if ts.id in unique_time_stamps:
    #             raise serializers.ValidationError({
    #                 "time_stamps": "Duplicate time slots are not allowed."
    #             })
    #         unique_time_stamps.add(ts.id)
    #
    #     return attrs

class TimeStampedSerializerByDoctor(serializers.ModelSerializer):
    services_offered = PackageServiceSerializer(many=True, read_only=True)
    time_stamps = TimeStampedSerializer(many=True, read_only=True)
    # time_stamps = serializers.SerializerMethodField()

    class Meta:
        model = StaffMember
        fields = ['id', 'doctor', 'services_offered', 'created_at', 'updated_at', 'is_active','time_stamps']
    # def get_time_stamps(self,obj):
    #     return TimeStampedSerializer(obj.TimeStamped.all(),many=True).data
class StaffMemberByDateSerializerByDoctor(serializers.ModelSerializer):
    services_offered = PackageServiceSerializer(many=True, read_only=True)
    time_stamps = serializers.SerializerMethodField()
    # services_offered = PackageServiceSerializer(many=True, read_only=True)
    # time_stamps = serializers.SerializerMethodField()
    class Meta:
        model = StaffMember
        fields = ['id', 'doctor', 'services_offered', 'created_at', 'updated_at', 'is_active','time_stamps']
    def get_time_stamps(self, obj):
        # Get the 'date' query parameter passed in the context
        date_filter = self.context.get('date', None)

        # Filter the time_stamps based on the date if it's provided
        if date_filter:
            filtered_time_stamps = obj.time_stamps.filter(date=date_filter, is_active=True)
        else:
            # If no date is provided, return all active time_stamps
            filtered_time_stamps = obj.time_stamps.filter(is_active=True)

        # Serialize the filtered time_stamps
        # return TimeStampedSerializer(filtered_time_stamps, many=True).data
        return TimeStampedForStaffmemberSerializer(filtered_time_stamps, many=True).data

class OrderPackageSerializer (serializers.ModelSerializer):
    class Meta:
        model = OrderPackage
        fields = "__all__"


class PatientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = "__all__"

class AvailableTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTimeSlot
        fields = "__all__"

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeStamped
        fields = "__all__"
##############################
#new for appointment list by user
class TimeStampedListSerializer(serializers.ModelSerializer):
    available_time_slot = AvailableTimeSlotSerializer(read_only=True)  # Nested serializer for full available time slot data
    class Meta:
        model = TimeStamped
        fields = "__all__"
class AppointmentFinalByUserSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(write_only=True, required=False)
    # Add fields to get the doctor and patient names
    time_slot = TimeStampedListSerializer(read_only=True)  # Nested serializer for full time slot data
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    class Meta:
        model = AppointmentFinal
        fields = "__all__"
        read_only_fields = ['days_off','is_finaly','status']
    def create(self, validated_data):
        # Extract coupon_code from the request data
        coupon_code = validated_data.pop('coupon_code', None)
        appointment = AppointmentFinal.objects.create(**validated_data)
        return appointment
    def get_doctor_name(self, obj):
        # if obj.doctorname_full_name :
        return obj.doctor.full_name
    def get_patient_name(self, obj):
        return obj.patient.full_name
#####################
#دیدن لیست دکترهایی که کاربر ثبت کرده این عملیات برای پروفایل کاربر ساخته شده است

class AppointmentFinalByUserProfileSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(write_only=True, required=False)
    # Add fields to get the doctor and patient names
    time_slot = TimeStampedListSerializer(read_only=True)  # Nested serializer for full time slot data
    patient_name = serializers.SerializerMethodField()
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = AppointmentFinal
        fields = "__all__"
        read_only_fields = ['days_off','is_finaly','status']
    def create(self, validated_data):
        # Extract coupon_code from the request data
        coupon_code = validated_data.pop('coupon_code', None)
        appointment = AppointmentFinal.objects.create(**validated_data)
        return appointment
    def get_patient_name(self, obj):
        return obj.patient.full_name

###############new for staffmember time and doctor
class TimeStampedForStaffmemberSerializer(serializers.ModelSerializer):
    available_time_slot = AvailableTimeSlotSerializers()  # Nested serializer for available_time_slot
    class Meta:
        model = TimeStamped
        fields = "__all__"

    def get_available_time_slot(self, obj):
        time_slots = obj.available_time_slot.all()
        return AvailableTimeSlotSerializers(time_slots, many=True).data
class StaffMemberTimeSerializer(serializers.ModelSerializer):
    # We will filter time_stamps in this serializer based on the date provided
    services_offered = PackageServiceSerializer(many=True, read_only=True)
    time_stamps = serializers.SerializerMethodField()

    class Meta:
        model = StaffMember
        fields = ['id', 'doctor', 'services_offered', 'time_stamps', 'is_active', 'created_at', 'updated_at']

    def get_time_stamps(self, obj):
        # Get the 'date' query parameter passed in the context
        date_filter = self.context.get('date', None)

        # Filter the time_stamps based on the date if it's provided
        if date_filter:
            filtered_time_stamps = obj.time_stamps.filter(date=date_filter, is_active=True)
        else:
            # If no date is provided, return all active time_stamps
            filtered_time_stamps = obj.time_stamps.filter(is_active=True)

        # Serialize the filtered time_stamps
        # return TimeStampedSerializer(filtered_time_stamps, many=True).data
        return TimeStampedForStaffmemberSerializer(filtered_time_stamps, many=True).data
#####################################
class AppointmentFinalDcSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(write_only=True, required=False)
    # Add fields to get the doctor and patient names
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    patient = PatientSerializer(read_only=True)
    time_slot = TimeStampedListSerializer(read_only=True)
    package = PackageServiceSerializer(read_only=True)

    class Meta:
        model = AppointmentFinal
        fields = "__all__"
        read_only_fields = ['days_off', 'is_finaly', 'status']

    def get_doctor_name(self, obj):
        # Assuming there’s a related `doctor` field on AppointmentFinal that links to a Doctor model
        return obj.doctor.full_name

    def get_patient_name(self, obj):
        # Assuming there’s a related `patient` field on AppointmentFinal that links to a Patient model
        return obj.patient.full_name

    def create(self, validated_data):
        # Extract coupon_code from the request data
        coupon_code = validated_data.pop('coupon_code', None)
        appointment = AppointmentFinal.objects.create(**validated_data)
        return appointment

    def validate_time_slot(self, value):
        if value.is_booked:
            raise serializers.ValidationError("This time slot is already booked.")
        return value