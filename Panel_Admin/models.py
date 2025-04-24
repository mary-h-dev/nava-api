from django.db import models
from accounts.models import User
from appointment.models import PackageService, AppointmentFinal, TimeStamped
from doctors.models import DoctorComment, Doctor



class CommentReporting(models.Model):
    reason = models.CharField(max_length=250)
    comment = models.ForeignKey(DoctorComment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

    def __str__(self):
        return f'comment ({self.comment}) is reported because ({self.reason})'

    class Meta:
        verbose_name = 'کامنت گزارش شده'
        verbose_name_plural = 'کامنت های گزارش شده'
class PaymentStatus(models.Model):
    is_valid = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

class CouponType(models.Model):
    codetype = models.CharField(max_length=100, unique=True, verbose_name='نوع کد')
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    description = models.TextField(verbose_name='توضیحات اصلی', null=True, blank=True)

    def __str__(self):
        return self.codetype

    class Meta:
        verbose_name = 'نوع کد تخفیف'
        verbose_name_plural = 'انواع کد های تخفیف'
class Coupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_creator')
    coupon_code = models.CharField(max_length=100, unique=True, verbose_name='کد تخفیف',null=True,blank=True)  # Ensure this field exists
    name = models.CharField(max_length=100, unique=True, verbose_name='نام کد')
    type = models.ForeignKey(CouponType, on_delete=models.CASCADE,null=True,blank=True,verbose_name='نوع کد تخفیف')
    num_uses = models.PositiveIntegerField(verbose_name='سقف تعداد ', default=1)
    limit_user = models.PositiveIntegerField(verbose_name='سقف استفاده کاربر ', default=1)
    description = models.TextField(verbose_name='توضیحات اصلی', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    valid_from = models.DateTimeField(verbose_name='زمان شروع')
    valid_until = models.DateTimeField(verbose_name='زمان پایان', blank=True, null=True)
    max_price = models.PositiveIntegerField(verbose_name=' حداکثر قیمت قابل استفاده', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))
    valid_products = models.ManyToManyField(PackageService, verbose_name='محصولات مجاز')
    invalid_users = models.ManyToManyField(User, verbose_name='کاربران غیر مجاز', blank=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کد های تخفیف'


class SmsMessage(models.Model):
    user_sender = models.ForeignKey(User, verbose_name='پیام فرستنده', on_delete=models.CASCADE,related_name='sent_messages')
    user_receiver = models.ManyToManyField(User, verbose_name='پیام گیرنده',related_name='received_messages')
    title = models.CharField(max_length=500, verbose_name='عنوان', null=True, blank=True)
    message = models.TextField(verbose_name='متن پیام')
    def __str__(self):
        return f"Message from {self.user_sender} to {self.user_receiver}"

class SmsTemplates(models.Model):
    user_template = models.ForeignKey(User, verbose_name='ایجاد کننده', on_delete=models.CASCADE)
    template_name = models.CharField(max_length=500, verbose_name='اسم پوسته', null=True, blank=True)
    content = models.TextField(verbose_name='محتوای فایل', null=True, blank=True)
    def __str__(self):
        return f"Template. Name: {self.user_template}, Content: {self}"
STATUS_CANCELLED = (
    ('1','کارت به کارت'),
    ('2','به ولت اضافه شود'),
    ('3','رد شده توسط امور مالی')
)
class CancellApointment(models.Model):
   # user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)
   patient = models.ForeignKey(User, verbose_name='لغو شده توسط مریض', on_delete=models.SET_NULL, null=True, blank=True)
   doctor = models.ForeignKey(Doctor, verbose_name='لغو شده توسط دکتر', on_delete=models.SET_NULL, null=True, blank=True)
   appointment_final = models.ForeignKey(AppointmentFinal , verbose_name='نوبت ثبت شده', on_delete=models.CASCADE, null=True, blank=True)
   timeslot = models.ForeignKey(TimeStamped, verbose_name='زمان رزو شده', on_delete=models.CASCADE, null=True, blank=True)
   price = models.IntegerField(verbose_name='قیمت')
   status = models.CharField(max_length=500,choices=STATUS_CANCELLED, verbose_name='وضعیت', null=True, blank=True)
   is_finaly = models.BooleanField(default=False, verbose_name='انجام شده است؟')

   def __str__(self):
       return self.appointment_final.doctor

class ReportUser(models.Model):
    doctor = models.ForeignKey(Doctor, verbose_name='دکتر', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='کاریر', on_delete=models.CASCADE)
    age = models.IntegerField(verbose_name="سن")
    gender = models.CharField(max_length=15,verbose_name='جنسیت', choices=[('M', 'مرد'), ('F', 'زن')])
    title = models.CharField(max_length=300,verbose_name='عنوان')
    content = models.TextField(verbose_name='محتوای یاداشت', null=True)
    reason_visit = models.CharField(max_length=500,verbose_name='علت مراجعه', null=True, blank=True)
    diagnose=models.CharField(max_length=500,verbose_name="تشخیص پزشک")
    treatment_steps = models.TextField(verbose_name="مراحل درمان")
    exercises = models.TextField(verbose_name="تمرین ها")
    upload_doc = models.ImageField(upload_to='media/%Y/%m/%d/treatment', null=True, blank=True,verbose_name="اپلود مدارک پزشکی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ اپدیت')
    def __str__(self):
        return f'{self.doctor} --->>{self.user}'

class TreatmentProcess(models.Model):
    doctor = models.ForeignKey(Doctor, verbose_name='دکتر', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='کاریر', on_delete=models.CASCADE)
    treatment_goals = models.TextField(verbose_name="اهداف درمانی بلند مدت و کوتاه مدت")
    technique_used = models.TextField(verbose_name="تکنیک و رویکرد مورد استفاده")
    therapy_note = models.TextField(verbose_name="خلاصه هر جلسه و تکالیف ارائه شده")
    planning_meeting = models.TextField(verbose_name="برنامه ریزی جلسات آینده")
    therapeutic_homework = models.TextField(verbose_name="تکالیف بین جلسات")
    progress_note = models.TextField(verbose_name="بررسی پیشرفت و تغییرات در علائم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ اپدیت")
    class Meta:
        verbose_name = 'فرآیندهای درمان'
        verbose_name_plural = 'فرآیند درمان'
    def __str__(self):
        return f'{self.doctor} --->>{self.user}'


class LibraryBookDoctor(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,verbose_name="دکتر")
    book = models.FileField(upload_to='panel/books/', verbose_name="کتاب")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(verbose_name="تاریخ اپدیت")
    class Meta:
        verbose_name =("کتابهای پزشکی")
        verbose_name_plural =("کتاب پزشکی")

class SaleExpert(models.Model):
    full_name = models.CharField(max_length=250,verbose_name="نام و نام خانوادگی")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="نام کارشناس")
    image_profile = models.ImageField(blank=True, null=True, upload_to="panel/expert/pictures/%Y/%m/%d", verbose_name="عکس")
    GENDER_CHOICES = [
        ("", ""),
        ('women', 'خانم'),
        ('men', 'آقا'),
    ]
    personnel_number = models.CharField(max_length=20, verbose_name="شماره پرسنلی",null=True, blank=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, verbose_name="جنسیت")
    biography = models.TextField(verbose_name="بیوگرافی",null=True, blank=True)
    active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def __str__(self):
        return f'{self.full_name}>>>{self.user}'
