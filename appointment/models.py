from config import settings
from doctors.models import Doctor ,DoctorCategory
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.core.exceptions import ValidationError
from django.core.validators import  MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField



User = settings.AUTH_USER_MODEL



class PaymentGatewayVisit(models.Model):
    GATEWAY_CHOICES = (
        ('Stripe', 'Stripe'),
        ('PayPal', 'PayPal'),
        ('Braintree', 'Braintree'),
    )
    name = models.CharField(max_length=255)
    gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES)
    merchant_id = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.gateway}"


class PaymentVisit(models.Model):
    appointment = models.ForeignKey('AppointmentFinal', on_delete=models.CASCADE, related_name='payments')
    gateway = models.ForeignKey(PaymentGatewayVisit, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    payment_date = models.DateTimeField(default=datetime.datetime.now)
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.appointment.patient.full_name} - {self.amount}"


#########################
######################
#


TYPES = (
    ('online', 'انلاین'),
    ('person', 'حضوری'),
    ('call', 'تلفنی'),
)

PAYMENT_TYPES = (
    ('full', _('Full payment')),
    ('down', _('Down payment')),
)

DAYS_OF_WEEK = (
    (0, 'Sunday'),
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
)


class PackageService(models.Model):
    name = models.CharField(max_length=100, blank=False,verbose_name='نام سرویس')
    title_category = models.ForeignKey(DoctorCategory, on_delete=models.CASCADE,null=True, blank=True,verbose_name='موضوع مشاوره')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    duration = models.DurationField(validators=[MinValueValidator(datetime.timedelta(minutes=30))])
    first_price = models.IntegerField(default=0, verbose_name="قیمت محصول",null=True, blank=True)
    price = models.IntegerField( validators=[MinValueValidator(0)], verbose_name='قیمت نهایی به تومان',null=True, blank=True)
    discount_price = models.IntegerField(default=0, verbose_name="تخفیف بر حسب تومان", blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    currency = models.CharField(max_length=10, default='TOMAN', verbose_name='واحد پول',null=True, blank=True)
    count_metting = models.IntegerField(null=True, blank=True)
    free_metting = models.IntegerField(null=True, blank=True,verbose_name='تعداد جلسات رایگان')
    visite_type = models.CharField(max_length=200,choices=TYPES,verbose_name= 'نوع ویزیت',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    seo = models.BooleanField(default=False, verbose_name="سئو")
    client = models.BooleanField(default=False, verbose_name="کلاینت")
    expert = models.BooleanField(default=False, verbose_name="کارشناس فروش")
    def __str__(self):
        return f"{self.name} - Duration: {self.duration}"

    def get_final_price(self):
        """Calculate the final price after discount."""
        return max(0, self.price - self.discount_price)

    def save(self, *args, **kwargs):
        """Override save method to adjust price based on discount."""
        if self.discount_price > 0:
            self.price = self.first_price - self.discount_price
        else:
            self.price = self.first_price  # Ensures price is set correctly if there's no discount.
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "No Description",
            "price": str(self.get_price()),
            "image_url": self.get_image_url(),
            "is_active": self.is_active,
        }

    def get_duration_parts(self):
        total_seconds = int(self.duration.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return days, hours, minutes, seconds

    def get_price(self):
        return int(self.price) if self.price % 1 == 0 else self.price

    def get_image_url(self):
        return self.image.url if self.image else ""

    def is_a_paid_service(self):
        return self.price > 0

    def accepts_down_payment(self):
        return self.down_payment > 0 if hasattr(self, 'down_payment') else False

class OrderPackage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_packages")
    package = models.ForeignKey(PackageService, on_delete=models.CASCADE, related_name="order_packages")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="order_packages")
    price = models.IntegerField(null=True, blank=True)
    count_remaining = models.IntegerField(null=True, blank=True, default=0)
    is_paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderPackage(user={self.user}, package={self.package.name}, doctor={self.doctor.full_name}, price={self.price})"

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.package.price  # Set price only if not provided
        if self.count_remaining < 0:
            raise ValidationError("Count remaining cannot be negative.")
        super().save(*args, **kwargs)

class AvailableTimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('doctor', 'start_time', 'end_time')

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('End time must be greater than start time.')

    def __str__(self):
        return f"{self.start_time} to {self.end_time} for Dr. {self.doctor.full_name}"


class TimeStamped(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,related_name='time_stamps')
    available_time_slot = models.ForeignKey(AvailableTimeSlot, on_delete=models.CASCADE, related_name='self')
    date = models.DateField()  # Field to specify the date of the time slot
    is_active = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)  # New field to track if the time slot is booked
    session_type =MultiSelectField(
        choices=[('online', 'انلاین'),
    ('person', 'حضوری'),
    ('call', 'تلفنی'),]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('doctor', 'available_time_slot', 'date')
    def clean(self):
        # Custom error message for unique constraint
        if TimeStamped.objects.filter(
            doctor=self.doctor,
            available_time_slot=self.available_time_slot,
            date=self.date
        ).exclude(id=self.id).exists():
            raise ValidationError({
                'non_field_errors': ["این زمان در این تاریخ قبلا انتخاب شده است"]
            })

    def __str__(self):
        # return f"{self.date}  (Active: {self.is_active}, Booked: {self.is_booked})"
        return f"{self.date} {self.available_time_slot}--{self.session_type}"
#doctor available
class StaffMember(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,related_name='staff_members')
    services_offered = models.ManyToManyField(PackageService)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_stamps = models.ManyToManyField(TimeStamped)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        services = ', '.join(service.name for service in self.services_offered.all())
        return f"{self.doctor.full_name} / {self.is_active} / package: {services} / date: {self.created_at}"




class DayOff(models.Model):
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.start_date} to {self.end_date} - {self.description if self.description else 'Day off'}"

    def clean(self):
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValidationError(_("Start date must be before end date"))

    def is_owner(self, user_id):
        return self.staff_member.user.id == user_id


class WorkingHours(models.Model):
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    day_of_week = models.PositiveIntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # meta data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):

        return f"{self.get_day_of_week_display()} - {self.start_time} to {self.end_time} "
######################
######################

class Patients(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=300,verbose_name="نام و نام خانوادگی")
    age = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=20,verbose_name='شماره همراه')
    gender = models.CharField(choices=(('M', 'مرد'), ('W', 'زن')), max_length=100)
    address = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.full_name}  + {self.user}"




class AppointmentFinal(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE,related_name='appointments')
    time_slot = models.ForeignKey(TimeStamped, on_delete=models.CASCADE)#new
    package = models.ForeignKey(PackageService, on_delete=models.CASCADE ,null=True, blank=True,db_index=True)
    coupon_code = models.CharField(max_length=100, blank=True, null=True,verbose_name="کپن تخفیف ثبت شده",db_index=True)
    coupon_submit = models.ForeignKey('Panel_Admin.Coupon', on_delete=models.CASCADE, null=True, blank=True)
    doctor_available= models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    status = models.CharField(max_length=10,default='scheduled',choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('canceled', 'Canceled')])
    is_finaly = models.BooleanField(default=False,verbose_name='قرار ملاقات نهایی شده؟',db_index=True)#new is_paid-->is_fianly
    is_reserved = models.BooleanField(default=False,verbose_name='رزو شده توسط پزشک')
    is_coupon = models.BooleanField(default=False, verbose_name='شامل تخفیف شده است؟')
    booke_by_expert = models.BooleanField(default=False, verbose_name='رزرو شده توسط کارشناس فروش')
    price_approved = models.IntegerField(null=True,blank=True,verbose_name='قیمت به تومان')
    created_at = models.DateTimeField(auto_now_add=True)
    effective_date = models.DateField(null=True, blank=True, verbose_name="تاریخ موثر")
    factors = models.ForeignKey("cart.MyFactors", on_delete=models.SET_NULL, null=True, blank=True)
    expert_sale = models.ForeignKey('Panel_Admin.SaleExpert', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ثبت شده توسط کارشناس فروش")
    def save(self, *args, **kwargs):
        # Automatically set status to 'Completed' if the appointment is finalized, otherwise 'Canceled'
        if self.is_finaly:
            self.status = 'completed'
        else:
            self.status = 'canceled'

        # Call the original save() method
        super(AppointmentFinal, self).save(*args, **kwargs)

    def get_package_price(self):
        if self.package:
            return self.package.price
        return self.package.price  # or return 0 or some default value
    def __str__(self):
        return f"{self.patient}+{self.doctor}"



#if fix time send sms or email for user
class AppointmentReminder(models.Model):
    appointment = models.ForeignKey(AppointmentFinal, on_delete=models.CASCADE, related_name='reminders')
#######################

class OrderVisit(models.Model):
    """
    Model for an order.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appointmentfinal = models.ForeignKey(AppointmentFinal, on_delete=models.CASCADE, verbose_name=('ملاقات با پزشک'))
    address = models.CharField(verbose_name='ادرس درخواست کننده',null=True, blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.IntegerField(null=True,blank=True,verbose_name='قیمت به تومان')
    expired_amount = models.IntegerField(null=True,blank=True,verbose_name='تاریخ انقضا سفارش')
    payment_date = models.DateTimeField(default=datetime.datetime.now)
    is_paid = models.BooleanField(default=False)
    def __str__(self):
        # return int(self.total_amount)
        # return f'Order #{self.id}'
        # return f'{self.user}visit >Dr.{self.appointmentfinal.doctor} package> {self.appointmentfinal.package}'
        return f'{self.user}visit >Dr.{self.appointmentfinal.doctor} '
    def save(self, *args, **kwargs):
        # Set total_amount based on the associated service price
        if self.appointmentfinal and hasattr(self.appointmentfinal, 'package'):
            self.total_amount = self.appointmentfinal.package.price
        else:
            self.total_amount = 0  # Default value if service is not available
        super().save(*args, **kwargs)  # Call the original save method

    @receiver(post_save, sender=appointmentfinal)
    def save_OrderVisit(sender, instance, created, **kwargs):
        if created:
            OrderVisit.objects.create(appointmentfinal_id=instance)



