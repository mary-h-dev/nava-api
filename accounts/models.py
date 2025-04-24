from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser
, PermissionsMixin)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, Phone_Number, password, **extra_fields):
        if not Phone_Number:
            raise ValueError(_("The phone_number must be set"))

        user = self.model(Phone_Number=Phone_Number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, Phone_Number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(Phone_Number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    Phone_Number = models.CharField(max_length=120, unique=True, verbose_name='شماره همراه'
,default="")
    email = models.EmailField(unique=True,null=True,blank=True ,verbose_name='ایمیل')
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_supporter = models.BooleanField(default=False)
    is_doctoradmin = models.BooleanField(default=False)
    is_admin_assistant = models.BooleanField(default=False)
    is_abroad = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=False)
    is_seo = models.BooleanField(default=False)
    confirm_otp = models.IntegerField(validators=[MinValueValidator(10000),
                                                  MaxValueValidator(99999)], blank=True, null=True)
    confirm_otp_expiration = models.DateTimeField(null=True)
    date_joined = models.DateTimeField( auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_date = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'Phone_Number'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def get_full_name(self):
        """
        Retrieve the full name from the related Profile model.
        Returns the Profile's full_name if it exists, else None.
        """
        return self.profile.full_name if hasattr(self, 'profile') and self.profile.full_name else None
    def __str__(self):
        return self.Phone_Number

Exp = (
    ('اضطراب و استرس', 'اضطراب و استرس'),
    ('هیپنوتراپی', 'هیپنوتراپی'),
    ('فوبیا', 'فوبیا'),
    ('ترس', 'ترس'),
    ('روانکاوی', 'روانکاوی'),
    ('خانواده', 'خانواده'),
    ('کودک', 'کودک'),
    ('افسردگی', 'افسردگی'),
    ('تحصیلی', 'تحصیلی'),
    ('سوگواری', 'سوگواری'),
    ('خیانت', 'خیانت'),
    ('ازدواج', 'ازدواج'),
    ('طلاق', 'طلاق'),
    ('پیش از ازدواج', 'پیش از ازدواج'),
    ('جنسی و سکستراپی', 'جنسی و سکستراپی'),
    ('اعتماد به نفس', 'اعتماد به نفس'),
    ('روابط عاطفی', 'روابط عاطفی'),
    ('اعتماد', 'اعتماد'),
    ('خودشناسی', 'خودشناسی'),
    ('مهاجرت', 'مهاجرت'),
    ('زوج درمانی', 'زوج درمانی'),
    ('افکار وسواسی', 'افکار وسواسی'),
    ('درمان اعتیاد', 'درمان اعتیاد'),
    ('کودک و نوجوان', 'کودک و نوجوان'),
    ('شکست عشقی', 'شکست عشقی'),
    ('هوش عاطفی', 'هوش عاطفی'),
    ('سایر اختلالات فردی', 'سایر اختلالات فردی')
)
#

class Profile(models.Model):
    # user => one to one
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile',verbose_name=_("نام کاربری"))
    email = models.EmailField(max_length=250,blank=True, null=True,verbose_name=_("ایمیل"))
    # email = models.ForeignKey(User, on_delete=models.CASCADE, to_field='email')
    full_name = models.CharField(max_length=250,verbose_name=_("نام و نام خانوادگی"))
    national_code = models.BigIntegerField(blank=True, null=True,verbose_name=_("کد ملی"))
    subject = models.CharField(choices=Exp,max_length=50,blank=True, null=True,verbose_name=_("موضوع مشاوره"))
    image = models.ImageField(verbose_name=_("عکس"), help_text=_("یک عکس بارگذاری کنید"),
                              upload_to="users/profile/images/", null=True, blank=True)
    deaf = models.BooleanField(default=False,verbose_name=_("شنوا هستم"))
    hard_hearing = models.BooleanField(default=False,verbose_name=_("کم شنوا هستم"))
    hearing = models.BooleanField(default=False,verbose_name=_("نا شنوا هستم"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    upload_file = models.FileField(upload_to='media/userfile', null=True, blank=True, verbose_name=_("اپلود فایل"))

    def __str__(self):
        return str(self.user)


#django signal
    @receiver(post_save, sender=User)
    def save_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance,email=instance.email)

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    access_token_expiration = models.DateTimeField(null=True)
    refresh_token_expiration = models.DateTimeField(null=True)
    def __str__(self):
        return self.access_token

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.Phone_Number}: {self.message[:30]}"

    class Meta:
        ordering = ['-created_at']