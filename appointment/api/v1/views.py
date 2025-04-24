from config.permissions import IsDoctorOrAdminDoctor, IsSaleExpertOrAdmin
from accounts.models import Notification
from appointment.api.v1.tasks import send_sms_task
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from Panel_Admin.models import Coupon, SaleExpert
from appointment.models import OrderVisit, PaymentVisit, StaffMember, AppointmentFinal, AppointmentReminder, \
    PackageService, TimeStamped, AvailableTimeSlot
from cart.models import Wallet, PurchaseOrder
from doctors.models import Doctor
from .paginations import CommentsPagination
from .paginations import DefaultPagination
from .serializers import (PaymentVisitSerializer, OrderSerializer, TimeStampedSerializerByDoctor, SendRequestSerializer,
                          AppointmentreqSerializer,
                          PatientsSerializer, PackageServiceSerializer, OrderPackageSerializer
, AppointmentFinalSerializer, StaffMemberSerializer, TimeStampedSerializer, AppointmentSerializer,
                          AvailableTimeSlotSerializer, AppointmentFinalySerializer, TimeStampedByDoctorSerializer,
                          AppointmentFinalByDcSerializer, AppointmentFinalDcSerializer,
                          AppointmentFinalDateDcSerializer, AppointmentFinalByUserSerializer,
                          AppointmentFinalByUserProfileSerializer, StaffMemberCreateSerializer,
                          StaffMemberTimeSerializer, StaffMemberByDateSerializerByDoctor)
from rest_framework import generics
from kavenegar import *
from ...models import OrderPackage
import logging
from rest_framework import filters
from appointment.models import Patients
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import NotFound
from django.utils import timezone
from datetime import date, datetime, timedelta
from datetime import date
from django.db.models import F
from khayyam import JalaliDatetime
from cart.models import MyFactors
from django.db.models import Max
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

############################# zarin pal visit
MERCHANT  =  "6144f600-49e2-4391-9990-b39a6b0c8ccc"
ZP_API_REQUEST = f"https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://www.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://www.zarinpal.com/pg/StartPay/"
sandbox = False
amount = 1000  # Rial / Required
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
phone = 'YOUR_PHONE_NUMBER'  # Optional
# Important: need to edit for realy server.
CallbackURL = 'http://localhost:8000/order/payment/'

###############################

class AppointmentList(generics.ListAPIView):
    queryset = AppointmentFinal.objects.all()
    serializer_class = AppointmentreqSerializer
    pagination_class = DefaultPagination



class AppointmentCreateView(generics.CreateAPIView):
    queryset = AppointmentFinal.objects.all()
    serializer_class = AppointmentreqSerializer
    # permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        ###############start validate doctor book
        # Get patient, appointment time, and doctor from validated data
        patient = serializer.validated_data['patient']
        appointment_time = serializer.validated_data['days']
        doctor = serializer.validated_data['doctor']

        # Define the day and week range for checking conflicts
        start_of_day = appointment_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = appointment_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Check for conflicting appointments for that doctor on the same day
        conflicting_appointments = AppointmentFinal.objects.filter(
            doctor=doctor,
            days__range=(start_of_day, end_of_day)
        ).filter(

        ).exclude(is_paid=True)

        if conflicting_appointments.exists():
            return Response(
                {"error": "This doctor is already booked for that day."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the appointment if no conflicts are found

        ############end doctor vistit book
        # Get the phone number of the associated user
        user = serializer.instance.patient.user
        phone_number = user.Phone_Number
        # APPM = AppointmentFinal.doctor.full_name
        message = f'تبریک! ملاقات شما با پزشک به ثبت رسید لطفا برای تکمیل فرایند به درگاه پرداخت بروید در صورت عدم پرداخت رزرو شما لغو محسوب میشود .'

        api = KavenegarAPI(
            '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D')
        params = {'sender': '90009809', 'receptor': phone_number, 'message': str(message)}
        api.sms_send(params)

        headers = self.get_success_headers(serializer.data)
        # self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    queryset = AppointmentFinal.objects.all()
    serializer_class = AppointmentreqSerializer

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()
        wallet = request.user.wallet

        if appointment.is_paid:
            return Response({'error': 'Already paid.'}, status=status.HTTP_400_BAD_REQUEST)

        service_price = appointment.package.price  # Assuming `price` exists in Service model

        if wallet.balance >= service_price:
            wallet.balance -= service_price
            wallet.save()
            appointment.is_paid = True
            appointment.save()
            return Response({'message': 'Payment successful.', 'balance': wallet.balance}, status=status.HTTP_200_OK)

        return Response({'error': 'Insufficient funds in wallet.'}, status=status.HTTP_400_BAD_REQUEST)
class PackageServiceCreate(generics.CreateAPIView):
    queryset = PackageService.objects.all()
    serializer_class = PackageServiceSerializer

class PackageServiceList(generics.ListAPIView):
    # queryset = PackageService.objects.all()
    serializer_class = PackageServiceSerializer
    pagination_class = CommentsPagination
    def get_queryset(self):
        queryset = PackageService.objects.filter(client=True)
        return queryset


class PackageServiceSeoList(generics.ListAPIView):
    # queryset = PackageService.objects.all()
    serializer_class = PackageServiceSerializer
    pagination_class = CommentsPagination
    def get_queryset(self):
        queryset = PackageService.objects.filter(seo=True)
        return queryset


class PackageServiceByIdList(generics.ListAPIView):
    serializer_class = PackageServiceSerializer
    def get_queryset(self):
        package_services_id = self.kwargs['id']
        return PackageService.objects.filter(id=package_services_id)


class PackageServiceDelete(generics.DestroyAPIView):
    queryset = PackageService.objects.all()
    serializer_class = PackageServiceSerializer

class PackageServiceUpdate(generics.UpdateAPIView):
    queryset = PackageService.objects.all()
    serializer_class = PackageServiceSerializer
class PackageServiceDetail(generics.RetrieveAPIView):
    queryset = PackageService.objects.all()
    serializer_class = PackageServiceSerializer

logger = logging.getLogger(__name__)


#############################
class AppointmentFinalCreate(generics.CreateAPIView):
    queryset = AppointmentFinal.objects.all()
    serializer_class = AppointmentFinalSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Retrieve the patient user
        user = request.user
        # Fetch the last unfinalized appointment for the patient
        # Assuming 'created_at' is a field in AppointmentFinal
        # Save the serializer to create the instance
        appointment_instance = serializer.save()

        # Retrieve the patient user
        user = appointment_instance.patient.user
        coupon_code = request.data.get('coupon_code', None)
        # Fetch the user's wallet
        wallet = get_object_or_404(Wallet, user=user)
        try:
            # Fetch patient and appointment details
            patient = get_object_or_404(Patients, user_id=user)
            # package_price = appointment_instance.package.price
            ######new for test
            package_price = appointment_instance.package_order.price
        except AttributeError:
            return Response({"error": "Package not found for the user."}, status=status.HTTP_400_BAD_REQUEST)
        final_price = package_price  # Start with the initial price
        if coupon_code:
            # Fetch the coupon
            coupon = get_object_or_404(Coupon, coupon_code=coupon_code, is_active=True)
            # Check if the package is valid for the coupon
            if not appointment_instance.package in coupon.valid_products.all():
                return Response({"error": "This package is not valid with the provided coupon."},
                                status=status.HTTP_400_BAD_REQUEST)
            # Check if the user has already used the coupon
            if coupon.valid_users.filter(id=user.id).exists():
                return Response({"error": "You have already used this coupon."},
                                status=status.HTTP_400_BAD_REQUEST)
            # Validate coupon eligibility
            now = timezone.now()
            if coupon.valid_from <= now <= coupon.valid_until:
                # Check if the coupon is for the current user (if applicable)
                if coupon.valid_users.exists() and user not in coupon.valid_users.all():
                    return Response({"error": "This coupon is not valid for your account."},
                                    status=status.HTTP_400_BAD_REQUEST)
                # Check usage limits
                if coupon.num_uses <= 0:
                    return Response({"error": "This coupon has been used up."},
                                    status=status.HTTP_400_BAD_REQUEST)
                if coupon.limit_user > 0:
                    user_uses = coupon.valid_users.filter(id=user.id).count()
                    if user_uses >= coupon.limit_user:
                        return Response({"error": "You have exceeded the coupon usage limit."},
                                        status=status.HTTP_400_BAD_REQUEST)
                    # Apply discount: Subtract the coupon's value from the package price
                discount_value = coupon.max_price  # Assuming max_price is the discount value
                final_price = max(0, package_price - discount_value)

                # Apply the final approved price in the AppointmentFinal instance
                appointment_instance.price_approved = final_price
                appointment_instance.is_coupon = True
                appointment_instance.coupon_code = coupon.coupon_code
                appointment_instance.save()

            else:
                return Response({"error": "This coupon is expired or not yet valid."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            # No coupon, so price_approved equals the package price
            appointment_instance.price_approved = package_price
            appointment_instance.save()


        # Check if wallet has enough balance
        # Lock the time slot
        time_slot = serializer.validated_data['time_slot']
        if time_slot.is_booked or not time_slot.is_active:
            return Response({"error": "This time slot is either booked or inactive."},
                            status=status.HTTP_400_BAD_REQUEST)


        # Check wallet balances
        if wallet.balance < final_price:
            return Response({"error": "کیف پول شما به میزان کافی شارژ نیست ."}, status=status.HTTP_400_BAD_REQUEST)

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Deduct the package price from the wallet balance

            wallet.balance -= final_price
            wallet.save()

            # Lock the time slot
            time_slot.is_booked = True
            time_slot.save()
            last_unfinalized_appointment = AppointmentFinal.objects.filter(
                is_finaly=False,
                patient__user=user.id
            ).last()

            last_unfinalized_appointment.is_finaly = True
            last_unfinalized_appointment.save()
            # Get user phone number and doctor name
            # Decrease coupon usage and add the user to the list of valid users
            if coupon_code:
                coupon.num_uses -= 1
                coupon.save()
                coupon.valid_users.add(user)
        OrderPackage.objects.create(
            appointment=appointment_instance,  # Assuming you have a ForeignKey to AppointmentFinal in OrderPackage
            total_amount=final_price,
            user=appointment_instance.patient.user  # Adjust as necessary
        )
        phone_number = user.Phone_Number
        doctor_name = appointment_instance.doctor.full_name
        # Message to be sent
        # message = f"تبریک! ملاقات شما با پزشک {doctor_name} در زمان  به ثبت رسید."
        message = f"تبریک!! نوبت ویزیت شما با دکتر{doctor_name} ثبت شد."

        # Send SMS
        api_key = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'  # Use a secure method to store your API key
        api = KavenegarAPI(api_key)
        params = {'sender': '90009809', 'receptor': phone_number, 'message': str(message)}
        api.sms_send(params)
        print("time is :")
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#####################################
#مدل بهبود یافته قرار نهایی پزشک
def generate_unique_factor_number():
    """Generate a unique factor number starting from 100."""
    BASE_NUMBER = 1000  # Starting point
    latest_number = MyFactors.objects.aggregate(Max('number_factors')).get('number_factors__max') or (BASE_NUMBER - 1)
    # اطمینان از اینکه مقدار عددی باشد
    try:
        latest_number = int(latest_number) if latest_number else (BASE_NUMBER - 1)
    except ValueError:
        latest_number = BASE_NUMBER - 1
    return latest_number + 1
class AppointmentFinalCreateOptimize1(generics.CreateAPIView):
    queryset = AppointmentFinal.objects.select_related(
        'patient__user', 'doctor', 'doctor_available'
    ).prefetch_related(
        'doctor_available__services_offered', 'patient'
    )
    serializer_class = AppointmentFinalSerializer
    permission_classes = [IsAuthenticated]

    INSUFFICIENT_BALANCE_MSG = "کیف پول شما به میزان کافی شارژ نیست."
    TIME_SLOT_UNAVAILABLE_MSG = "این تایم قبلا رزور شده است"
    COUPON_INACTIVE_MSG = "این کپن منقضی شده یا صحیح نمی باشد"
    PACKAGE_NOT_OFFERED_MSG = "این پکیج برای دکتر فعال نیست"
    INVALID_STAFF_MEMBER_MSG = "The selected staff member does not correspond to the chosen doctor."
    INVALID_SESSION_TYPE_MSG = "نوع جلسه با زمان انتخاب‌شده مطابقت ندارد."

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ذخیره اولیه داده‌ها
        appointment_instance = serializer.save()
        user = appointment_instance.patient.user
        wallet = get_object_or_404(Wallet.objects.select_related('user'), user=user)
        time_slot = serializer.validated_data.get('time_slot', None)
        coupon_code = request.data.get('coupon_code', None)

        # اعتبارسنجی پکیج و تایم‌اسلات
        validation_error = self.validate_package_and_time_slot(appointment_instance, time_slot)
        if validation_error:
            return self.error_response(validation_error)

        # مدیریت قیمت و کوپن
        final_price, coupon_or_error = self.handle_coupon_and_price(coupon_code, user, appointment_instance)
        if final_price is None:
            return self.error_response(coupon_or_error)

        # اعتبارسنجی موجودی کیف پول
        if wallet.balance < final_price:
            return self.error_response(self.INSUFFICIENT_BALANCE_MSG, status.HTTP_402_PAYMENT_REQUIRED)

        # نهایی‌سازی نوبت
        self.finalize_appointment(appointment_instance, wallet, final_price, time_slot, coupon_or_error)

        # ارسال پیامک و نوتیفیکیشن
        self.send_notifications(appointment_instance, time_slot)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def validate_package_and_time_slot(self, appointment_instance, time_slot):
        """Validate package and time slot availability."""
        if not isinstance(time_slot, TimeStamped) or not time_slot.is_active:
            return self.TIME_SLOT_UNAVAILABLE_MSG

        if time_slot.is_booked:
            return self.TIME_SLOT_UNAVAILABLE_MSG

        if appointment_instance.package and not appointment_instance.doctor_available.services_offered.filter(
                id=appointment_instance.package.id).exists():
            return self.PACKAGE_NOT_OFFERED_MSG

        if appointment_instance.doctor_available.doctor != appointment_instance.doctor:
            return self.INVALID_STAFF_MEMBER_MSG

        return None

    def handle_coupon_and_price(self, coupon_code, user, appointment_instance):
        """Process coupon and calculate final price."""
        package_price = appointment_instance.get_package_price()

        # اگر کد تخفیفی وارد نشده باشد
        if not coupon_code:
            return package_price, None

        # دریافت و اعتبارسنجی کد تخفیف
        coupon = self.get_valid_coupon(coupon_code, user, appointment_instance)
        if isinstance(coupon, str):  # اگر اعتبارسنجی کوپن خطا داشت
            return None, coupon

        # محاسبه تخفیف
        discount_value = min(coupon.max_price, package_price) if coupon.max_price else package_price
        final_price = max(0, package_price - discount_value)

        return final_price, coupon

    def get_valid_coupon(self, coupon_code, user, appointment_instance):
        """Retrieve and validate coupon."""
        try:
            coupon = Coupon.objects.prefetch_related('valid_products', 'invalid_users').get(
                coupon_code=coupon_code, is_active=True
            )
        except Coupon.DoesNotExist:
            return self.COUPON_INACTIVE_MSG

        now = timezone.now()
        if not (coupon.valid_from <= now <= coupon.valid_until):
            return self.COUPON_INACTIVE_MSG

        if appointment_instance.package not in coupon.valid_products.all():
            return "این پکیج برای این کپن معتبر نیست."

        if coupon.invalid_users.filter(id=user.id).exists():
            return "شما قبلاً از این کپن استفاده کرده‌اید."

        if coupon.num_uses <= 0:
            return "این کپن تمام شده است."

        return coupon

    @transaction.atomic
    def finalize_appointment(self, appointment_instance, wallet, final_price, time_slot, coupon):
        """Finalize appointment with all necessary updates."""
        # Deduct wallet balance
        wallet.balance = F('balance') - final_price
        wallet.save()

        # Update time slot
        time_slot.is_booked = True
        time_slot.save()

        # Mark previous unfinalized appointments
        AppointmentFinal.objects.filter(
            is_finaly=False, patient__user=appointment_instance.patient.user
        ).update(is_finaly=True)

        # Update package order
        OrderPackage.objects.filter(
            user=appointment_instance.patient.user,
            package=appointment_instance.package,
            doctor=appointment_instance.doctor,
            is_paid=False
        ).update(is_paid=True)

        # Update coupon usage if applicable
        if coupon:
            self.update_coupon_usage(coupon, appointment_instance.patient.user)

        # Save appointment
        appointment_instance.is_finaly = True
        appointment_instance.price_approved = final_price
        appointment_instance.save()

        # Create purchase order and factor
        self.create_purchase_order(appointment_instance, final_price)
        self.create_factor(appointment_instance, final_price)

    def update_coupon_usage(self, coupon, user):
        """Update coupon usage."""
        coupon.num_uses = F('num_uses') - 1
        coupon.invalid_users.add(user)
        coupon.save()

    def create_purchase_order(self, appointment_instance, final_price):
        """Create a purchase order."""
        PurchaseOrder.objects.get_or_create(
            user=appointment_instance.patient.user,
            service_type="قرار ملاقات با پزشک",
            final_price=final_price,
            appointment=appointment_instance
        )

    def create_factor(self, appointment_instance, final_price):
        """Create a financial factor."""
        unique_number = generate_unique_factor_number()
        package_price = appointment_instance.get_package_price()
        discount_value = package_price - final_price

        factor = MyFactors.objects.create(
            user=appointment_instance.patient.user,
            title=f"ویزیت دکتر {appointment_instance.doctor.full_name}",
            total_price=package_price,
            number_factors=unique_number,
            final_pay_price=final_price,
            discounted_price=discount_value,
            payment_status="پرداخت شد.",
            is_paid=True,
            order_item_data={"appointment_id": appointment_instance.id},
        )
        appointment_instance.factors = factor
        appointment_instance.save()

    def send_notifications(self, appointment_instance, time_slot):
        """Send SMS and notifications to user and doctor."""
        user = appointment_instance.patient.user
        doctor_name = appointment_instance.doctor.full_name

        # Convert time_slot to Persian DateTime
        appointment_date_persian = JalaliDatetime(time_slot.date).strftime('%Y/%m/%d')
        appointment_time_persian = time_slot.available_time_slot.start_time.strftime('%H:%M')
        appointment_time = f"{appointment_date_persian} ساعت {appointment_time_persian}"

        # Send SMS and notifications
        if not user.is_abroad:
            self.send_sms(
                user.Phone_Number,
                f"تبریک!! نوبت ویزیت شما با دکتر {doctor_name} در تاریخ {appointment_time} ثبت شد."
            )

        self.send_notification(
            user.id, f"قرار ملاقات شما با دکتر {doctor_name} در تاریخ {appointment_time} با موفقیت ثبت شد."
        )
        self.send_notification(
            appointment_instance.doctor.user.id,
            f"شما یک قرار ملاقات با درمانجو {appointment_instance.patient.full_name} دارید."
        )

    def send_sms(self, phone_number, message):
        """Send an SMS message."""
        try:
            api_key = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'
            api = KavenegarAPI(api_key)
            params = {'sender': '90009809', 'receptor': phone_number, 'message': str(message)}
            api.sms_send(params)
        except (APIException, HTTPException) as e:
            print(f"Error sending SMS: {str(e)}")

    def send_notification(self, user_id, message):
        """Save a notification to the database."""
        Notification.objects.create(user_id=user_id, message=message)

    def error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        """Return a standardized error response."""
        return Response({"error": message}, status=status_code)

class AppointmentFinalCreateOptimize(generics.CreateAPIView):
    queryset = AppointmentFinal.objects.select_related(
        'patient__user', 'doctor', 'doctor_available'
    ).prefetch_related(
        'doctor_available__services_offered', 'patient'
    )
    serializer_class = AppointmentFinalSerializer
    permission_classes = [IsAuthenticated]

    INSUFFICIENT_BALANCE_MSG = "کیف پول شما به میزان کافی شارژ نیست."
    TIME_SLOT_UNAVAILABLE_MSG = "این تایم قبلا رزور شده است"
    COUPON_INACTIVE_MSG = "این کپن منقضی شده یا صحیح نمی باشد"
    PACKAGE_NOT_OFFERED_MSG = "این پکیج برای دکتر فعال نیست"
    INVALID_STAFF_MEMBER_MSG = "The selected staff member does not correspond to the chosen doctor."
    INVALID_SESSION_TYPE_MSG = "نوع جلسه با زمان انتخاب‌شده مطابقت ندارد."
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ذخیره اولیه داده‌ها
        appointment_instance = serializer.save()
        user = appointment_instance.patient.user
        wallet = get_object_or_404(Wallet.objects.select_related('user'), user=user)
        time_slot = serializer.validated_data.get('time_slot', None)
        coupon_code = request.data.get('coupon_code', None)
        # مقداردهی و اعتبارسنجی effective_date
        #هنوز هندل نشده
        # Retrieve and validate time_slot
        if not isinstance(time_slot, TimeStamped):  # بررسی نوع time_slot
            raise AttributeError("time_slot باید یک نمونه معتبر از مدل TimeStamped باشد.")


        # اعتبارسنجی پکیج و تایم‌اسلات
        validation_error = self.validate_package_and_time_slot(appointment_instance, time_slot)
        if validation_error:
            return self.error_response(validation_error)

        # مدیریت قیمت و کوپن
        final_price, coupon_or_error = self.handle_coupon_and_price(
            coupon_code, user, appointment_instance
        )
        if final_price is None:
            return self.error_response(coupon_or_error)

        # اعتبارسنجی موجودی کیف پول
        if wallet.balance < final_price:
            return self.error_response(self.INSUFFICIENT_BALANCE_MSG, status.HTTP_402_PAYMENT_REQUIRED)


        appointment_instance.price_approved = final_price
        if coupon_or_error:
            appointment_instance.is_coupon = True
            appointment_instance.coupon_code = coupon_or_error.coupon_code

        # نهایی‌سازی نوبت
        self.finalize_appointment(appointment_instance, wallet, final_price, time_slot, coupon_or_error)

        # ارسال پیامک و نوتیفیکیشن
        self.send_notifications(appointment_instance,time_slot)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def validate_package_and_time_slot(self, appointment_instance, time_slot):
        """Validate package and time slot availability."""
        if appointment_instance.package and not appointment_instance.doctor_available.services_offered.filter(
                id=appointment_instance.package.id).exists():
            return self.PACKAGE_NOT_OFFERED_MSG

        if time_slot.is_booked or not time_slot.is_active:
            return self.TIME_SLOT_UNAVAILABLE_MSG

        if appointment_instance.doctor_available.doctor != appointment_instance.doctor:
            return self.INVALID_STAFF_MEMBER_MSG
        return None

    def submit_coupon(self, appointment_instance, coupon):
        """
        ثبت کوپن معتبر و لینک دادن آن به نوبت.
        """
        # ثبت اطلاعات کوپن در نوبت
        appointment_instance.coupon_submit = coupon  # ذخیره شی کپن
        appointment_instance.is_coupon = True
        appointment_instance.coupon_code = coupon.coupon_code
        appointment_instance.save()

        # به‌روزرسانی تعداد استفاده و اضافه کردن کاربر به کاربران غیرمجاز
        # coupon.num_uses = F('num_uses') - 1
        coupon.invalid_users.add(appointment_instance.patient.user)
        coupon.save()

    def handle_coupon_and_price(self, coupon_code, user, appointment_instance):
        """Process coupon and calculate final price."""
        package_price = appointment_instance.get_package_price()

        # اگر کد تخفیفی وارد نشده باشد
        if not coupon_code:
            return package_price, None

        # دریافت و اعتبارسنجی کد تخفیف
        coupon = get_object_or_404(Coupon.objects.prefetch_related('valid_products', 'invalid_users'),
                                   coupon_code=coupon_code, is_active=True)

        # بررسی اینکه محصول موردنظر در لیست محصولات مجاز کپن باشد
        if appointment_instance.package not in coupon.valid_products.all():
            return None, "این پکیج برای این کپن معتبر نیست."

        # بررسی اینکه آیا کاربر قبلاً از این کپن استفاده کرده است
        if coupon.invalid_users.filter(id=user.id).exists():
            return None, "شما قبلاً از این کپن استفاده کرده‌اید."

        # بررسی تاریخ اعتبار کپن
        now = timezone.now()
        if not (coupon.valid_from <= now <= coupon.valid_until):
            return None, self.COUPON_INACTIVE_MSG

        # بررسی تعداد باقی‌مانده از کپن
        if coupon.num_uses <= 0:
            return None, "این کپن تمام شده است."

        # محاسبه تخفیف
        discount_value = min(coupon.max_price, package_price) if coupon.max_price else package_price
        final_price = max(0, package_price - discount_value)
        wallet = get_object_or_404(Wallet.objects.select_related('user'), user=user)
        # ثبت کپن در نوبت

        if wallet.balance < final_price:
            # اگر ولت شارژ کافی نداشت، کوپن را به لیست invalid_users اضافه نکنیم
            return None, self.INSUFFICIENT_BALANCE_MSG
        self.submit_coupon(appointment_instance, coupon)
        return final_price, coupon
    @transaction.atomic
    def finalize_appointment(self, appointment_instance, wallet, final_price, time_slot, coupon):
        """Finalize appointment with all necessary updates."""
        # Deduct wallet balance
        wallet.balance = F('balance') - final_price
        wallet.save()

        # Update time slot
        time_slot.is_booked = True
        time_slot.save()

        # Mark previous unfinalized appointments
        # AppointmentFinal.objects.filter(
        #     is_finaly=False, patient__user=appointment_instance.patient.user
        # ).update(is_finaly=True)
        # فقط نوبت جاری را نهایی کنیم
        appointment_instance.is_finaly = True
        appointment_instance.save()
        # Update package order
        OrderPackage.objects.filter(
            user=appointment_instance.patient.user,
            package=appointment_instance.package,
            doctor=appointment_instance.doctor,
            is_paid=False
        ).update(is_paid=True)
        # Update coupon usage if applicable
        # if coupon:
        #     self.update_coupon_usage(coupon, appointment_instance.patient.user)
        # Update coupon usage if applicable
        if coupon:
            coupon.num_uses = F('num_uses') - 1
            coupon.invalid_users.add(appointment_instance.patient.user)
            coupon.save()
        # appointment_instance.coupon_code = coupon.coupon_code
        # Save appointment instance
        appointment_instance.is_finaly = True
        appointment_instance.save()

        # Create purchase order
        self.create_PurchaseOrder(
            appointment_instance.patient.user,
            appointment_instance,
            final_price
        )
        unique_number = str(generate_unique_factor_number())
    # Create or update a MyFactors instance
        doctor_name = appointment_instance.doctor.full_name
        # Calculate discount value safely
        discount_value = 0  # Default discount value
        package_price = appointment_instance.get_package_price()  # Retrieve package price
        if coupon:
            discount_value = min(coupon.max_price, package_price) if coupon.max_price else package_price

        final_price = max(0, package_price - discount_value)
        factor = MyFactors.objects.create(
            user=appointment_instance.patient.user,
            # title= f"مرا",
            title= f" ویزیت دکتر  با پزشک {doctor_name}",
            # total_price=final_price,
            total_price=package_price,
            number_factors=unique_number,  # مقدار شماره فاکتور
            final_pay_price=final_price,
            discounted_price=discount_value,
            payment_status="پرداخت شد.",
            is_paid=True,
            order_item_data={"appointment_id": appointment_instance.id},
        )
        # Link the factor to the appointment
        appointment_instance.factors = factor
        appointment_instance.save()

    def create_PurchaseOrder(self, user, appointment_instance, final_price):
        """Create a purchase order for the finalized appointment."""
        service_type = "قرار ملاقات با پزشک"  # Example: 'قرار ملاقات با پزشک'

        # Check if a purchase order already exists for this appointment
        existing_order = PurchaseOrder.objects.filter(
            user=user,
            service_type=service_type,
            appointment=appointment_instance
        ).exists()

        if existing_order:
            return  # If the order exists, do nothing

        # Create a new purchase order
        PurchaseOrder.objects.create(
            user=user,
            service_type=service_type,
            final_price=final_price,
            appointment=appointment_instance  # Save reference to the appointment
        )
    def send_notifications(self, appointment_instance,time_slot):
        """Send SMS and notifications to user and doctor."""
        user = appointment_instance.patient.user
        doctor = appointment_instance.doctor.user
        doctor_name = appointment_instance.doctor.full_name
        # Convert time_slot to Persian DateTime
        appointment_date_persian = JalaliDatetime(time_slot.date).strftime('%Y/%m/%d')  # تاریخ ملاقات
        appointment_time_persian = time_slot.available_time_slot.start_time.strftime('%H:%M')  # زمان ملاقات
        appointment_time = f"{appointment_date_persian} ساعت {appointment_time_persian}"
        message_user = f"تبریک!! نوبت ویزیت شما با دکتر {doctor_name} در تاریخ {appointment_time} ثبت شد."
        message_doctor = f"شما یک قرار ملاقات با درمانجو {appointment_instance.patient.full_name} دارید."

        # Send SMS
        if user.is_abroad:
            self.send_email(
                to=user.email,
                subject="تایید نوبت ویزیت",
                message=message_user
            )
        else:
            self.send_sms(user, appointment_instance, time_slot)
        # Send notifications
        self.send_notification(
            user.id,
            # f"قرار ملاقات شما با دکتر {doctor_name} با موفقیت ثبت شد."
            f"قرار ملاقات شما با دکتر {doctor_name} در تاریخ {appointment_time} با موفقیت ثبت شد."
        )
        self.send_notification(
            doctor.id,
            f"شما یک قرار ملاقات با درمانجو {appointment_instance.patient.full_name} دارید."
        )

    def send_email(self, to, subject, message):
        """Send an email to the user."""
        from_email = settings.EMAIL_BACKEND
        recipient_list = [to]
        if not to:
            print("No email address provided.")
            return

        try:
            send_mail(
                subject,
                message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
    def send_sms(self, user, appointment_instance, time_slot):
        phone_number = user.Phone_Number
        doctor_name = appointment_instance.doctor.full_name
        appointment_date_persian = JalaliDatetime(time_slot.date).strftime('%Y/%m/%d')
        appointment_time_persian = time_slot.available_time_slot.start_time.strftime('%H:%M')
        appointment_time = f"{appointment_date_persian} ساعت {appointment_time_persian}"
        message = f"تبریک!! نوبت ویزیت شما با دکتر {doctor_name} در تاریخ {appointment_time} ثبت شد."

        api_key = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'
        api = KavenegarAPI(api_key)
        params = {'sender': '90009809', 'receptor': phone_number, 'message': str(message)}
        api.sms_send(params)

    # def send_sms(self, phone_number, message):
    #     """Send an SMS asynchronously using Celery."""
    #     send_sms_task.delay(phone_number, message)
    def send_notification(self, user_id, message):
        """Save a notification to the database."""
        Notification.objects.create(
            user_id=user_id,
            message=message
        )

    def error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        """Return a standardized error response."""
        return Response({"error": message}, status=status_code)
#appointment by doctor for patient

class AppointmentFinalByDoctorCreateOptimize0(generics.CreateAPIView):
    queryset = AppointmentFinal.objects.all()
    serializer_class = AppointmentFinalByDcSerializer
    permission_classes = [IsDoctorOrAdminDoctor]
    # Constants for error messages
    TIME_SLOT_UNAVAILABLE_MSG = "این تایم قبلا رزور شده است"
    PACKAGE_NOT_OFFERED_MSG = "این پکیج برای دکتر فعال نیست"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        origin = request.META.get('HTTP_ORIGIN')

        appointment_instance = serializer.save()
        user = appointment_instance.patient.user
        time_slot = serializer.validated_data['time_slot']
        # Validate package and time slot
        validation_error = self.validate_package_and_time_slot(appointment_instance, time_slot)
        if validation_error:
            return self.error_response(validation_error)

        # Transaction for wallet deduction, time slot booking, and coupon updates
        with transaction.atomic():
            try:
                time_slot.is_booked = True
                time_slot.save()

                last_unfinalized_appointment = AppointmentFinal.objects.filter(
                    is_finaly=False,
                    patient__user=user.id
                ).last()
                if last_unfinalized_appointment:
                    last_unfinalized_appointment.is_finaly = True
                    last_unfinalized_appointment.save()

            except Exception as e:
                return self.error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send SMS notification asynchronously
        self.send_sms(user, appointment_instance, time_slot)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def validate_package_and_time_slot(self, appointment_instance, time_slot):
        """Validate package and time slot availability."""
        if appointment_instance.package and not appointment_instance.doctor_available.services_offered.filter(
                id=appointment_instance.package.id).last():
            return self.PACKAGE_NOT_OFFERED_MSG

        if time_slot.is_booked or not time_slot.is_active:
            return self.TIME_SLOT_UNAVAILABLE_MSG

        if appointment_instance.doctor_available.doctor != appointment_instance.doctor:
            return "The selected staff member does not correspond to the chosen doctor."
        return None

    def send_sms(self, user, appointment_instance, time_slot):
        """Send SMS notification for the appointment asynchronously using Celery."""
        phone_number = user.Phone_Number  # Ensure the field name matches your User model
        doctor_name = appointment_instance.doctor.full_name
        appointment_date_persian = JalaliDatetime(time_slot.date).strftime('%Y/%m/%d')  # تاریخ ملاقات
        appointment_time_persian = time_slot.available_time_slot.start_time.strftime('%H:%M')  # زمان ملاقات
        appointment_time = f"{appointment_date_persian} ساعت {appointment_time_persian}"
        message = f"تبریک!! نوبت ویزیت شما با دکتر {doctor_name} در تاریخ {appointment_time} ثبت شد."

        # send_sms.delay(phone_number, message)  # Queue the task with Celery
        api_key = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'  # Use a secure method to store your API key
        api = KavenegarAPI(api_key)
        params = {'sender': '90009809', 'receptor': phone_number, 'message': str(message)}
        api.sms_send(params)

    def error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        """Return a standardized error response."""
        return Response({"error": message}, status=status_code)

class AppointmentFinalByDoctorCreateOptimize(generics.CreateAPIView):
    queryset = AppointmentFinal.objects.all()
    serializer_class = AppointmentFinalByDcSerializer
    permission_classes = [IsDoctorOrAdminDoctor]

    TIME_SLOT_UNAVAILABLE_MSG = "این تایم قبلا رزرو شده است"
    PACKAGE_NOT_OFFERED_MSG = "این پکیج برای دکتر فعال نیست"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment_instance = serializer.save()
        user = appointment_instance.patient.user
        time_slot = serializer.validated_data['time_slot']

        # Validate package and time slot
        validation_error = self.validate_package_and_time_slot(appointment_instance, time_slot)
        if validation_error:
            return self.error_response(validation_error)

        # Finalizing only the current appointment
        with transaction.atomic():
            try:
                # Set the current appointment as finalized
                appointment_instance.is_finaly = True
                appointment_instance.save()

                # Mark the selected time slot as booked
                time_slot.is_booked = True
                time_slot.save()

            except Exception as e:
                return self.error_response(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send SMS notification asynchronously
        self.send_sms(user, appointment_instance, time_slot)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def validate_package_and_time_slot(self, appointment_instance, time_slot):
        if appointment_instance.package and not appointment_instance.doctor_available.services_offered.filter(
                id=appointment_instance.package.id).exists():
            return self.PACKAGE_NOT_OFFERED_MSG

        if time_slot.is_booked or not time_slot.is_active:
            return self.TIME_SLOT_UNAVAILABLE_MSG

        if appointment_instance.doctor_available.doctor != appointment_instance.doctor:
            return "The selected staff member does not correspond to the chosen doctor."
        return None

    def send_sms(self, user, appointment_instance, time_slot):
        phone_number = user.Phone_Number
        doctor_name = appointment_instance.doctor.full_name
        appointment_date_persian = JalaliDatetime(time_slot.date).strftime('%Y/%m/%d')
        appointment_time_persian = time_slot.available_time_slot.start_time.strftime('%H:%M')
        appointment_time = f"{appointment_date_persian} ساعت {appointment_time_persian}"
        message = f"تبریک!! نوبت ویزیت شما با دکتر {doctor_name} در تاریخ {appointment_time} ثبت شد."

        api_key = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'
        api = KavenegarAPI(api_key)
        params = {'sender': '90009809', 'receptor': phone_number, 'message': str(message)}
        api.sms_send(params)

    def error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({"error": message}, status=status_code)
###################


class AppointmentSalesExpertViewSet(generics.CreateAPIView):
    queryset = AppointmentFinal.objects.select_related(
        'patient__user', 'doctor', 'doctor_available'
    ).prefetch_related(
        'doctor_available__services_offered', 'patient'
    )
    serializer_class = AppointmentFinalSerializer
    permission_classes = [IsAuthenticated]

    INSUFFICIENT_BALANCE_MSG = "کیف پول شما به میزان کافی شارژ نیست."
    TIME_SLOT_UNAVAILABLE_MSG = "این تایم قبلا رزور شده است"
    COUPON_INACTIVE_MSG = "این کپن منقضی شده یا صحیح نمی باشد"
    PACKAGE_NOT_OFFERED_MSG = "این پکیج برای دکتر فعال نیست"
    INVALID_STAFF_MEMBER_MSG = "The selected staff member does not correspond to the chosen doctor."
    INVALID_SESSION_TYPE_MSG = "نوع جلسه با زمان انتخاب‌شده مطابقت ندارد."

    def check_if_sale_expert(self, request):
        """
        Check if the user is a Sale Expert.
        """
        try:
            sale_expert = SaleExpert.objects.get(user=request.user)
            return sale_expert  # Return SaleExpert object if found
        except SaleExpert.DoesNotExist:
            return Response({'detail': 'کاربر باید کارشناس فروش باشد.'}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        # Check if request is made by a Sale Expert
        sale_expert = self.check_if_sale_expert(request)
        if isinstance(sale_expert, Response):
            return sale_expert  # If not a Sale Expert, return error response

        # Validate the input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Initial save of appointment data
        appointment_instance = serializer.save()
        user = appointment_instance.patient.user
        wallet = get_object_or_404(Wallet.objects.select_related('user'), user=user)
        time_slot = serializer.validated_data.get('time_slot', None)
        coupon_code = request.data.get('coupon_code', None)

        # Validate the time slot
        if not isinstance(time_slot, TimeStamped):
            raise AttributeError("time_slot باید یک نمونه معتبر از مدل TimeStamped باشد.")

        # Validate package and time slot
        validation_error = self.validate_package_and_time_slot(appointment_instance, time_slot)
        if validation_error:
            return self.error_response(validation_error)

        # Handle coupon and calculate final price
        final_price, coupon_or_error = self.handle_coupon_and_price(coupon_code, user, appointment_instance)
        if final_price is None:
            return self.error_response(coupon_or_error)

        # Check if the user has sufficient balance
        if wallet.balance < final_price:
            return self.error_response(self.INSUFFICIENT_BALANCE_MSG, status.HTTP_402_PAYMENT_REQUIRED)

        # Update the appointment with the approved price and coupon details
        appointment_instance.price_approved = final_price
        if coupon_or_error:
            appointment_instance.is_coupon = True
            appointment_instance.coupon_code = coupon_or_error.coupon_code

        # Finalize the appointment
        self.finalize_appointment(appointment_instance, wallet, final_price, time_slot, coupon_or_error)

        # Send notifications (email, SMS, etc.)
        self.send_notifications(appointment_instance, time_slot)

        # Return the success response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def validate_package_and_time_slot(self, appointment_instance, time_slot):
        """بررسی اعتبار پکیج و تایم‌اسلات"""
        if appointment_instance.package and not appointment_instance.doctor_available.services_offered.filter(
                id=appointment_instance.package.id).exists():
            return self.PACKAGE_NOT_OFFERED_MSG

        if time_slot.is_booked or not time_slot.is_active:
            return self.TIME_SLOT_UNAVAILABLE_MSG

        if appointment_instance.doctor_available.doctor != appointment_instance.doctor:
            return self.INVALID_STAFF_MEMBER_MSG
        return None

    def handle_coupon_and_price(self, coupon_code, user, appointment_instance):
        """مدیریت کپن و محاسبه قیمت نهایی"""
        package_price = appointment_instance.get_package_price()

        if not coupon_code:
            return package_price, None

        # گرفتن و اعتبارسنجی کپن
        coupon = get_object_or_404(Coupon.objects.prefetch_related('valid_products', 'invalid_users'),
                                   coupon_code=coupon_code, is_active=True)

        if appointment_instance.package not in coupon.valid_products.all():
            return None, "این پکیج برای این کپن معتبر نیست."

        if coupon.invalid_users.filter(id=user.id).exists():
            return None, "شما قبلاً از این کپن استفاده کرده‌اید."

        now = timezone.now()
        if not (coupon.valid_from <= now <= coupon.valid_until):
            return None, self.COUPON_INACTIVE_MSG

        if coupon.num_uses <= 0:
            return None, "این کپن تمام شده است."

        # محاسبه تخفیف
        discount_value = min(coupon.max_price, package_price) if coupon.max_price else package_price
        final_price = max(0, package_price - discount_value)

        # چک کردن موجودی کیف پول
        wallet = get_object_or_404(Wallet.objects.select_related('user'), user=user)
        if wallet.balance < final_price:
            return None, self.INSUFFICIENT_BALANCE_MSG

        self.submit_coupon(appointment_instance, coupon)
        return final_price, coupon

    def submit_coupon(self, appointment_instance, coupon):
        """ثبت کپن و ارتباط آن با نوبت"""
        appointment_instance.coupon_submit = coupon
        appointment_instance.is_coupon = True
        appointment_instance.coupon_code = coupon.coupon_code
        appointment_instance.save()

        # به‌روزرسانی استفاده از کپن و افزودن کاربر به لیست کاربران غیرمعتبر
        coupon.invalid_users.add(appointment_instance.patient.user)
        coupon.save()

    @transaction.atomic
    def finalize_appointment(self, appointment_instance, wallet, final_price, time_slot, coupon):
        """نهایی‌سازی نوبت با تمام به‌روزرسانی‌های لازم"""
        wallet.balance = F('balance') - final_price
        wallet.save()

        time_slot.is_booked = True
        time_slot.save()
        # فقط نوبت جاری را نهایی کنیم
        appointment_instance.is_finaly = True
        appointment_instance.booke_by_expert = True
        appointment_instance.save()

        # به‌روزرسانی نوبت‌های قبلی که نهایی نشده‌اند
        # AppointmentFinal.objects.filter(
        #     is_finaly=False, patient__user=appointment_instance.patient.user
        # ).update(is_finaly=True)

        # ایجاد سفارش خرید
        self.create_PurchaseOrder(appointment_instance.patient.user, appointment_instance, final_price)

        # ایجاد یا به‌روزرسانی MyFactors
        unique_number = str(generate_unique_factor_number())
        factor = MyFactors.objects.create(
            user=appointment_instance.patient.user,
            title=f"ویزیت دکتر {appointment_instance.doctor.full_name}",
            total_price=appointment_instance.get_package_price(),
            number_factors=unique_number,
            final_pay_price=final_price,
            discounted_price=0,
            payment_status="پرداخت شد.",
            is_paid=True,
            order_item_data={"appointment_id": appointment_instance.id},
        )

        appointment_instance.factors = factor
        appointment_instance.save()

    def create_PurchaseOrder(self, user, appointment_instance, final_price):
        """ایجاد سفارش خرید برای نوبت نهایی‌شده"""
        service_type = "قرار ملاقات با پزشک"

        # اگر سفارش قبلاً ایجاد شده، ایجاد نکنیم
        existing_order = PurchaseOrder.objects.filter(
            user=user,
            service_type=service_type,
            appointment=appointment_instance
        ).exists()

        if existing_order:
            return

        PurchaseOrder.objects.create(
            user=user,
            service_type=service_type,
            final_price=final_price,
            appointment=appointment_instance
        )
    def send_notifications(self, appointment_instance, time_slot):
        """ارسال پیامک و نوتیفیکیشن"""
        user = appointment_instance.patient.user
        doctor = appointment_instance.doctor.user
        doctor_name = appointment_instance.doctor.full_name

        self.send_notification(user.id, f"قرار ملاقات شما با دکتر {doctor_name} ثبت شد.")
        self.send_notification(doctor.id, f"شما یک قرار ملاقات جدید دارید.")

    def send_notification(self, user_id, message):
        """ایجاد نوتیفیکیشن"""
        Notification.objects.create(user_id=user_id, message=message)

    def send_sms(self, user, appointment_instance, time_slot):
        """ارسال پیامک نوبت ویزیت به کاربر"""
        try:
            phone_number = user.Phone_Number  # اطمینان از وجود مقدار
            if not phone_number:
                raise ValueError("شماره تلفن کاربر مشخص نشده است.")

            doctor_name = appointment_instance.doctor.full_name
            appointment_date_persian = JalaliDatetime(time_slot.date).strftime('%Y/%m/%d')  # تاریخ به شمسی
            appointment_time_persian = time_slot.available_time_slot.start_time.strftime('%H:%M')  # ساعت ملاقات
            appointment_time = f"{appointment_date_persian} ساعت {appointment_time_persian}"
            message = f"تبریک! نوبت ویزیت شما با دکتر {doctor_name} در {appointment_time} ثبت شد."

            api_key = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'
            api = KavenegarAPI(api_key)

            params = {
                'sender': '90009809',
                'receptor': phone_number,
                'message': message
            }

            response = api.sms_send(params)
            print("پیامک با موفقیت ارسال شد:", response)

        except ValueError as e:
            print("خطا در مقداردهی متغیرها:", str(e))

        except APIException as e:
            print("خطای API:", str(e))

        except HTTPException as e:
            print("خطای ارتباطی با سرور Kavenegar:", str(e))

        except Exception as e:
            print("خطای نامشخص:", str(e))
    def error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        """ارسال پیام خطا"""
        return Response({"detail": message}, status=status_code)

class AppointmentListByCupoun(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    queryset = AppointmentFinal.objects.all()
    pagination_class = DefaultPagination
    def get_queryset(self):
        usr_copoun = self.kwargs['usr_copoun']
        date = self.kwargs['date']
        # Parse the incoming date string to a datetime object
        try:
            parsed_date = datetime.strptime(date, '%Y-%m-%d')  # Adjust format if needed
            # Format the date to match the model's `created_at` field format (e.g., date-only)
            formatted_date = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("فرمت تاریخ اشتباه است: YYYY-MM-DD")
        # return AppointmentFinal.objects.filter(coupon_submit__user__id=usr_copoun, created_at=formatted_date)
        return AppointmentFinal.objects.filter(coupon_submit__user__id=usr_copoun, created_at__date=formatted_date)

class AppointmentListViewSet(generics.ListAPIView):
    queryset = AppointmentFinal.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

class AppointmentFinalByUer(generics.ListAPIView):
    serializer_class = AppointmentFinalByUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['-created_at']


    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return AppointmentFinal.objects.filter(patient_id=patient_id,status='completed')
#دیدن لیست دکترهایی که کاربر ثبت کرده این عملیات برای پروفایل کاربر ساخته شده است
class AppointmentFinalByPatientProfile(generics.ListAPIView):
    serializer_class = AppointmentFinalByUserProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return AppointmentFinal.objects.filter(patient_id=patient_id,is_finaly=True).distinct('doctor_id')
class AppointmentListByDcViewSet(generics.ListAPIView):
    serializer_class = AppointmentFinalDcSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        # date = self.kwargs['date']  # Expecting date in 'YYYY-MM-DD' format
        return AppointmentFinal.objects.filter(doctor_id=doctor_id)
class AppointmentFinalByTimeSlot(generics.ListAPIView):
    serializer_class = AppointmentFinalSerializer


    def get_queryset(self):
        time_slot_id = self.kwargs['timeslot_id']
        # date = self.kwargs['date']  # Expecting date in 'YYYY-MM-DD' format
        return AppointmentFinal.objects.filter(time_slot_id=time_slot_id)

#دکتر در یک روز چه بیمارانی قرار ملاقات ثبت کردند
class AppointmentFinalByTimeSlotDc(generics.ListAPIView):
    serializer_class = AppointmentFinalDateDcSerializer
    pagination_class = DefaultPagination
    def get_queryset(self):
        # Retrieve URL parameters
        date_str = self.kwargs.get('date')  # expecting 'YYYY-MM-DD' format
        doctor_id = self.kwargs.get('doctor_id')

        # Validate the presence of required parameters
        if not date_str or not doctor_id:
            raise NotFound("Both 'date' and 'doctor_id' are required parameters.")

        # Parse the date string
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise NotFound("Date must be in 'YYYY-MM-DD' format.")

        # Filter appointments by date and doctor_id
        return AppointmentFinal.objects.filter(
            time_slot__date=target_date,  # assuming time_slot is a DateTimeField or DateField
            doctor_id=doctor_id,
            is_finaly=True,
            # status=''
        )
    # def get_queryset(self):
    #     time_slot = self.kwargs['timeslot']
    #     doctor_id = self.kwargs['doctor_id']
    #     return AppointmentFinal.objects.filter(time_slot=time_slot , doctor_id=doctor_id,is_finaly=True)
class ActiveTimeSlotsList(generics.ListAPIView):
    queryset = TimeStamped.objects.filter(is_active=True, is_booked=False)
    serializer_class = TimeStampedSerializer  # Ensure you have a serializer for TimeStamped
    permission_classes = [IsAuthenticated]

class ActiveTimeSlotsByDoctorView(generics.ListAPIView):
    serializer_class = TimeStampedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        date = self.kwargs['date']  # Expecting date in 'YYYY-MM-DD' format
        return TimeStamped.objects.filter(is_active=True, is_booked=False, date=date, doctor_id=doctor_id)

class TimeSlotList(generics.ListAPIView):
    queryset = AvailableTimeSlot.objects.all()
    serializer_class = AvailableTimeSlotSerializer


class TimeSlotByDoctorList(generics.ListAPIView):
    queryset = AvailableTimeSlot.objects.all()
    serializer_class = AvailableTimeSlotSerializer
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        # date = self.kwargs['date']  # Expecting date in 'YYYY-MM-DD' format
        return AvailableTimeSlot.objects.filter( doctor_id=doctor_id)

class TimeSlotCreate(generics.CreateAPIView):
    queryset = AvailableTimeSlot.objects.all()
    serializer_class = AvailableTimeSlotSerializer

class TimeSlotUpdate(generics.UpdateAPIView):
    queryset = AvailableTimeSlot.objects.all()
    serializer_class = AvailableTimeSlotSerializer
class TimeSlotDelete(generics.DestroyAPIView):
    queryset = AvailableTimeSlot.objects.all()
    serializer_class = AvailableTimeSlotSerializer
class TimeSlotDetail(generics.RetrieveAPIView):
    queryset = AvailableTimeSlot.objects.all()
    serializer_class = AvailableTimeSlotSerializer
class StaffMemberList(generics.ListAPIView):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer
    pagination_class = DefaultPagination



class TimeStampedList(generics.ListAPIView):
    queryset = TimeStamped.objects.all()
    serializer_class = TimeStampedSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['date']

class TimeStampedListByDoctor(generics.ListAPIView):
    queryset = TimeStamped.objects.all()
    serializer_class = TimeStampedByDoctorSerializer
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        date = self.kwargs['date']
        return TimeStamped.objects.filter(doctor_id=doctor_id, date=date)

class TimeStampedLisDoctorId(generics.ListAPIView):
    queryset = TimeStamped.objects.all()
    serializer_class = TimeStampedByDoctorSerializer
    pagination_class = DefaultPagination
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        now = datetime.now()
        return TimeStamped.objects.filter(doctor_id=doctor_id,date__gte=now)
class TimeStampedCreate(generics.CreateAPIView):
    queryset = TimeStamped.objects.all()
    serializer_class = TimeStampedSerializer


class TimeStampedUpdate(generics.UpdateAPIView):
    queryset = TimeStamped.objects.all()
    serializer_class = TimeStampedSerializer
class TimeStampedDetail(generics.RetrieveAPIView):
    queryset = TimeStamped.objects.all()
    serializer_class = TimeStampedSerializer

class TimeStampedDelete(generics.DestroyAPIView):
    queryset = TimeStamped.objects.all()
    serializer_class = TimeStampedSerializer


class OrderPackageCreate(generics.CreateAPIView):
    queryset = OrderPackage.objects.all()
    serializer_class = OrderPackageSerializer

class OrderPackageList(generics.ListAPIView):
    queryset = OrderPackage.objects.all()
    serializer_class = OrderPackageSerializer

class OrderPackageUpdate(generics.UpdateAPIView):
    queryset = OrderPackage.objects.all()
    serializer_class = OrderPackageSerializer


class OrderPackageDelete(generics.DestroyAPIView):
    queryset = OrderPackage.objects.all()
    serializer_class = OrderPackageSerializer


class PatientsList(generics.ListAPIView):
    queryset = Patients.objects.all()
    serializer_class = PatientsSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name','phone_number']
#####patient by user
class PatientsByUserList(generics.ListAPIView):
    serializer_class = PatientsSerializer
    permission_classes = [IsAuthenticated]      #نیاز به بررسی دارد چک شود

    def get_queryset(self):
        user_id = self.kwargs['user_id']

        # Check if the doctor exists
        if not Patients.objects.filter(user_id=user_id).exists():
            raise NotFound(detail="PATIENTS NOT FOUND.")
        return Patients.objects.filter(user_id=user_id, is_active=True)

class patientsCreate(generics.CreateAPIView):
    queryset = Patients.objects.all()
    serializer_class = PatientsSerializer
############
class patientsUpdate(generics.UpdateAPIView):
    queryset = Patients.objects.all()
    serializer_class = PatientsSerializer

class patientsDetail(generics.RetrieveAPIView):
    queryset = Patients.objects.all()
    serializer_class = PatientsSerializer

class StaffMembersByDoctor(generics.ListAPIView):
    serializer_class = TimeStampedSerializerByDoctor
    pagination_class = DefaultPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    # ordering = ('created_date',)
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']

        # Check if the doctor exists
        if not Doctor.objects.filter(id=doctor_id).exists():
            raise NotFound(detail="Doctor not found.")

        return StaffMember.objects.filter(doctor_id=doctor_id)
        # Optional: Filter only active staff
#by doctor-first
class StaffMembersByDoctorLast(generics.ListAPIView):
    serializer_class = TimeStampedSerializerByDoctor

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        # date = self.kwargs['date']
        # Check if the doctor exists
        if not Doctor.objects.filter(id=doctor_id).exists():
            raise NotFound(detail="Doctor not found.")

        # Wrap in a list to make it iterable for ListAPIView
        last_staff_member = StaffMember.objects.filter(doctor_id=doctor_id, is_active=True).last()
        # return last_staff_member
        return [last_staff_member] if last_staff_member else []

class StaffMembersByDoctorDate(generics.ListAPIView):
    serializer_class = StaffMemberByDateSerializerByDoctor
    # serializer_class = StaffMemberTimeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['time_stamps__date']
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']

        # چک کنید آیا دکتر با این ID وجود دارد
        if not Doctor.objects.filter(id=doctor_id).exists():
            raise NotFound(detail="Doctor not found.")

        # دریافت پارامتر تاریخ از کوئری (به صورت پیش‌فرض تاریخ امروز)
        date_param = self.request.query_params.get('date', None)
        if date_param:
            # تبدیل پارامتر به فرمت تاریخ
            try:
                target_date = date.fromisoformat(date_param)  # فرمت انتظار: YYYY-MM-DD
            except ValueError:
                raise ValidationError("Invalid date format. Please provide a valid date in YYYY-MM-DD format.")
        else:
            target_date = date.today()

        # فیلتر کارکنان بر اساس دکتر و تاریخ زمان
        staff_members = StaffMember.objects.filter(
            doctor_id=doctor_id,  # شناسه دکتر
            is_active=True,  # فقط کارکنان فعال
        ).distinct()

        # فیلتر time_stamps بر اساس تاریخ دقیق
        staff_members = staff_members.filter(
            time_stamps__date=target_date,  # فقط تاریخ مورد نظر
            time_stamps__is_active=True  # فقط time_stamp های فعال
        )

        return staff_members
    # def get_queryset(self):
    #     doctor_id = self.kwargs['doctor_id']
    #     # Retrieve the doctor to ensure it exists
    #     doctor = Doctor.objects.filter(id=doctor_id).first()
    #     if not doctor:
    #         raise NotFound(detail="Doctor not found.")
    #
    #     # Get date from query parameters (default to today if not provided)
    #     date_param = self.request.query_params.get('date', None)
    #     if date_param:
    #         # Parse date if provided
    #         try:
    #             target_date = date.fromisoformat(date_param)  # Expecting the date in ISO format (YYYY-MM-DD)
    #         except ValueError:
    #             raise NotFound(detail="Invalid date format. Please provide a valid date in YYYY-MM-DD format.")
    #     else:
    #         # Default to today's date if no date is provided
    #         target_date = date.today()
    #
    #     # Query for staff members for the given doctor and active time slots
    #     staff_members = StaffMember.objects.filter(
    #         doctor=doctor,
    #         is_active=True,
    #         time_stamps__date=target_date
    #     ).distinct()  # Use distinct to avoid duplicates
    #
    #     return staff_members
    def get_serializer_context(self):
        # Add the date filter to the context of the serializer
        context = super().get_serializer_context()
        date_param = self.request.query_params.get('date', None)
        context['date'] = date_param
        return context
class StaffMembersByDoctorTimeLast(generics.ListAPIView):
    serializer_class = StaffMemberTimeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['time_stamps__date']

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        # Retrieve the doctor to ensure it exists
        doctor = Doctor.objects.get(id=doctor_id)
        if not doctor:
            raise NotFound(detail="Doctor not found.")

        # Get date from query parameters (default to today if not provided)
        date_param = self.request.query_params.get('date', None)
        if date_param:
            # Parse date if provided
            try:
                target_date = date.fromisoformat(date_param)  # Expecting the date in ISO format (YYYY-MM-DD)
            except ValueError:
                raise NotFound(detail="Invalid date format. Please provide a valid date in YYYY-MM-DD format.")
        else:
            # Default to today's date if no date is provided
            target_date = date.today()

        # Query for staff members for the given doctor and active time slots
        staff_members = StaffMember.objects.filter(
            doctor=doctor,
            is_active=True,
            time_stamps__date=target_date
        ) # Use distinct to avoid duplicates

        return staff_members

    def get_serializer_context(self):
        # Add the date filter to the context of the serializer
        context = super().get_serializer_context()
        date_param = self.request.query_params.get('date', None)
        context['date'] = date_param
        return context
class StaffMembersCreate(generics.CreateAPIView):
    serializer_class = StaffMemberCreateSerializer
    queryset = StaffMember.objects.all()
    permission_classes = [IsDoctorOrAdminDoctor]



class StaffMembersUpdate(generics.UpdateAPIView):
    serializer_class = StaffMemberCreateSerializer
    queryset = StaffMember.objects.all()
    permission_classes = [IsDoctorOrAdminDoctor]

class StaffMembersDetail(generics.RetrieveAPIView):
    serializer_class = StaffMemberCreateSerializer
    queryset = StaffMember.objects.all()
    permission_classes = [IsDoctorOrAdminDoctor]



class StaffMembersDelete(generics.DestroyAPIView):
    serializer_class = StaffMemberCreateSerializer
    queryset = StaffMember.objects.all()
    permission_classes = [IsDoctorOrAdminDoctor]

# class canceledappointmentCreateUserViewSet():

