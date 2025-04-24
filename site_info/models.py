from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from accounts.models import User
from blog.models import Blog

# Create your models here.

class AboutUs(models.Model):
    address = models.CharField(max_length=200, verbose_name='آدرس')
    phone = models.BigIntegerField(null=True, blank=True, verbose_name='تلفن')
    fax = models.IntegerField(null=True, blank=True, verbose_name='فکس')
    email = models.EmailField(max_length=200, null=True, blank=True, verbose_name='ایمیل')
    copy_right = models.TextField(verbose_name='متن کپی رایت سایت')
    about_us_text = models.TextField(verbose_name='متن درباره ما سایت')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

    def __str__(self):
        return self.about_us_text


class Slider(models.Model):
    name = models.CharField(verbose_name="نام اسلایدر", help_text=("Required"), max_length=255)
    is_published = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))
    def __str__(self):
        return self.name




class Slide(models.Model):
    slider = models.ForeignKey(Slider, on_delete=models.CASCADE, related_name='slides')
    title = models.CharField(max_length=255, null=True, blank=True)
    caption = models.TextField(null=True, blank=True)
    image_url = models.ImageField(verbose_name=("اسلاید"), help_text=("یک اسلاید بارگذاری کنید"),
                                  upload_to="slides/images/")
    web_image = models.ImageField(verbose_name=("عکس فشرده وب"),
                                  upload_to="slides/web-images/", null=True, blank=True)
    link_url = models.CharField(max_length=500,verbose_name=("ادرس مقصد"), null=True, blank=True)
    alt_text = models.CharField(verbose_name=("متن جایگزین عکس"), help_text="برای اسلاید توضیحی بنویسید",
                                max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    is_main = models.BooleanField(default=False, verbose_name=("عکس اصلی"))
    position = models.IntegerField(verbose_name='جایگاه', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

    def __str__(self):
        return self.title




class Tabs(models.Model):
    title = models.CharField(max_length=255, verbose_name='نام')
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

    def __str__(self):
        return self.title


class SectionType(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام')
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

    def __str__(self):
        return self.name


class Sections(models.Model):
    tab = models.ForeignKey(Tabs, on_delete=models.CASCADE, related_name='tabs')
    name = models.CharField(max_length=255, verbose_name='نام')
    data = models.JSONField(null=True, blank=True)
    SectionType = models.ForeignKey(SectionType, on_delete=models.CASCADE, related_name='sectiontype')
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    position = models.IntegerField(verbose_name='جایگاه', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))
    data_ids = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'section  ({self.name} for  {self.tab})'



class Tags(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام')
    Tag_type = models.CharField(max_length=255, verbose_name='مدل تگ', null=True, blank=True)
    Content_Id = models.IntegerField(verbose_name='شناسه_محتوا', null=True, blank=True)
    tag_url = models.URLField(verbose_name=("آدرس تگ"), null=True, blank=True,
                              help_text=("یک آدرس برای تگ بارگذاری کنید"))
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

    def __str__(self):
        return self.name

#all//home page//
class Banner(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    caption = models.TextField(null=True, blank=True)
    image_url = models.ImageField(verbose_name=("بنر"), help_text=("یک بنر بارگذاری کنید"),
                                  upload_to="banner/images/")
    web_image = models.ImageField(verbose_name=("عکس فشرده وب"),
                                  upload_to="banner/web-images/", null=True, blank=True)
    alt_text = models.CharField(verbose_name=("متن جایگزین بنر"), help_text=("برای اسلاید توضیحی بنویسید"),
                                max_length=255, null=True, blank=True)
    url = models.URLField(verbose_name=("آدرس URL"), help_text="آدرس مورد نظر برای وقتی که روی بنر کلیک می‌شود",
                          null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    is_main = models.BooleanField(default=False, verbose_name=("عکس اصلی"))
    position = models.IntegerField(verbose_name='جایگاه', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

    def __str__(self):
        return self.name


class Social_Media (models.Model):
    instagram = models.URLField(verbose_name=("صفحه اینشتاگرام"),null=True, blank=True)
    facebook = models.URLField(verbose_name=("صفحه ی فیسبوک"),null=True, blank=True)
    whatsapp = models.IntegerField(verbose_name=("واتساپ"),null=True, blank=True)
    twitter = models.URLField(verbose_name=("توییتر"),null=True, blank=True)
    telegram = models.IntegerField(verbose_name=(""),null=True, blank=True)
    youtube = models.URLField(verbose_name=("یوتیوب"),null=True, blank=True)
    aparat = models.URLField(verbose_name=("اپارات"),null=True, blank=True)

    def __str__(self):
        return str(self.instagram)

class SurveySite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE , verbose_name=("کاربر"))
    description = models.TextField()
    rate =models.IntegerField(default=0,validators=[MinValueValidator(0),
                                                  MaxValueValidator(4)] ,verbose_name='میزان رضایت شما از سایت هم ارام')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.Phone_Number