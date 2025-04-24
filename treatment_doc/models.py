from django.db import models
from config import settings
from doctors.models import Doctor
from accounts.models import Profile
User = settings.AUTH_USER_MODEL



class Treatments(models.Model):
    name = models.CharField(max_length=100,verbose_name="نام")
    family = models.CharField(max_length=200,verbose_name="فامیل")
    age = models.IntegerField(verbose_name="سن")
    gender = models.CharField(max_length=15,verbose_name='جنسیت', choices=[('M', 'مرد'), ('F', 'زن')])
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="پزشک معالج")
    nation_code = models.IntegerField(default=0, verbose_name="کد ملی")
    documents_number = models.IntegerField(verbose_name="شماره پرونده")
    create_visit = models.DateTimeField(auto_now_add=True,verbose_name="تاریخ ایجاد ویزیت")
    diagnose=models.CharField(max_length=500,verbose_name="تشخیص پزشک")
    prescription = models.TextField(max_length=1000,verbose_name="نسخه")
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name="کاربر")
    is_active = models.BooleanField(default=True,verbose_name="فعال/غیرفعال")
    upload_doc = models.FileField(upload_to='media/%Y/%m/%d/treatment', null=True, blank=True,verbose_name="اپلود مدارک پزشکی")
    is_finished = models.BooleanField(default=False, verbose_name="توسط پزشک بسته شده است؟")
    def __str__(self):
        return self.name +' '+self.family


