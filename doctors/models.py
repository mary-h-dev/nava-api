
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from tag.models import Tag
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg
from django.db.models import F


User = get_user_model()


class DoctorCategory(models.Model):
    title = models.CharField(max_length=150,verbose_name='دسته بندی')
    eng_title = models.CharField(max_length=150,verbose_name='دسته بندی به انگلیسی')
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)
    def save(self, *args, **kwargs):

        if not self.slug:
            if self.title.isascii():
                # random_num = random.randint(1000, 9999)
                title = slugify(self.title.replace(" ", "-"))
                slug = f"{title}"
            else:
                # random_num = random.randint(1000, 9999)
                title = self.title.replace(" ", "-")
                slug = f"{title}"

            self.slug = slug

        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('doctorcategory-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title+' / '+self.eng_title

class Cooprations(models.Model):
    # user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=20, unique=True)
    eng_title = models.CharField(max_length=50, unique=True)
    internal_link = models.CharField(max_length=500,null=True, blank=True, verbose_name='لینک داخلی')
    photo_logo = models.ImageField(upload_to='doctor/logo', null=True, blank=True,verbose_name='لوگو')
    def __str__(self):
        return self.title+' / '+self.eng_title

class Specialization(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name='فیلد تحصیلی')
    eng_title = models.CharField(max_length=100, unique=True, verbose_name='فیلد تحصیلی به زبان انگلیسی')
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیرفعال')
    def __str__(self):
        return self.title+' / '+self.eng_title
class Doctor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="نام دکتر")
    image_profile = models.ImageField(blank=True, null=True, upload_to="doctor/pictures/%Y/%m/%d", verbose_name="عکس")
    full_name = models.CharField(max_length=100, verbose_name="اسم و فامیل")
    category = models.ForeignKey(DoctorCategory, verbose_name="دسته بندی", on_delete=models.CASCADE)
    GENDER_CHOICES = [
        ("", ""),
        ('women', 'خانم'),
        ('men', 'آقا'),

    ]
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, verbose_name="جنسیت")
    start_expiration = models.DateField(blank=True, null=True, verbose_name="شروع فعالیت پزشکی از سال")
    specialization = models.ForeignKey(Specialization,on_delete=models.CASCADE,verbose_name="فیلد تحصیلی")
    medical_license_number = models.CharField(max_length=50, unique=True, verbose_name="شماره نظام پزشکی")
    locations = models.CharField(max_length=600,null=True,blank=True , verbose_name="ادرس مطب")
    bio = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    video_url_meets = models.URLField(blank=True, null=True, verbose_name='لینک گوگل میت')
    cooperation_kind = models.ManyToManyField(Cooprations,max_length=50,verbose_name='نوع همکاری')
    tags = models.ManyToManyField(Tag,max_length=100,verbose_name='تگ')
    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)
    datetime_created = models.DateTimeField(default=timezone.now, verbose_name="تاریخ ایجاد")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="تاریخ تغییرات")
    active = models.BooleanField(default=True, verbose_name="فعال/ غیر فعال")
    view_count = models.IntegerField(default=0)
    rate_count = models.FloatField(default=4, verbose_name="میانگین امتیازات", null=True, blank=True)
    page_meta = models.CharField(verbose_name=_("متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    meta_descriptions = models.CharField(verbose_name=_("توضیحات متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    canolically = models.URLField(null=True,blank=True,verbose_name=_("کنولیکال"))
    keywords = models.CharField(max_length=600, null=True, blank=True, verbose_name='کلمات کلیدی')


        # return meet_link
    def save(self, *args, **kwargs):

        if not self.slug:
            if self.full_name.isascii():
                # random_num = random.randint(1000, 9999)
                full_name = slugify(self.full_name.replace(" ", "-"))
                slug = f"{full_name}"
            else:
                # random_num = random.randint(1000, 9999)
                full_name = self.full_name.replace(" ", "-")
                slug = f"{full_name}"

            self.slug = slug

        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('doctor-detail', kwargs={'slug': self.slug})
    def __str__(self):
        return f"{self.full_name}"


class DoctorPoint(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='comments', on_delete=models.CASCADE, verbose_name="نام پزشک")
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, verbose_name="نام یادداشت گذارنده")
    text = models.TextField(verbose_name='متن نظر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    email = models.EmailField(null=True,verbose_name='ایمیل')
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    rating = models.PositiveSmallIntegerField(null=True,blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='امتیاز'
    )
    def __str__(self):
        return f'Comment by {self.user} on {self.doctor.full_name}'


class DoctorComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, verbose_name='نام و نام خانوادگی')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    text = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    Answer = models.ForeignKey('DoctorAnswer', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    is_validated = models.BooleanField(null=True, verbose_name='تایید/عدم تایید')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)

    def __str__(self):
        return f'comment of ({self.user} for {self.doctor} is {self.text} )'
    def add_like(self):
        """Increases like count by 1."""
        self.like_count += 1
        self.save(update_fields=['like_count'])

    def remove_like(self):
        """Decreases like count by 1, ensuring it doesn't go below zero."""
        if self.like_count > 0:
            self.like_count -= 1
            self.save(update_fields=['like_count'])

    def add_dislike(self):
        """Increases dislike count by 1."""
        self.dislike_count += 1
        self.save(update_fields=['dislike_count'])

    def remove_dislike(self):
        """Decreases dislike count by 1, ensuring it doesn't go below zero."""
        if self.dislike_count > 0:
            self.dislike_count -= 1
            self.save(update_fields=['dislike_count'])

    def net_likes(self):
        """Returns the net likes (like count - dislike count)."""
        return self.like_count - self.dislike_count

class DoctorAnswer(models.Model):
    comments = models.ForeignKey(DoctorComment, on_delete=models.CASCADE, related_name='comment_answers')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_answers')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')

    def __str__(self):
        return str(self.doctor)


class Rate_Doctor(models.Model):
    name = models.CharField(max_length=150, verbose_name='نام کاربر')
    doctor = models.ForeignKey(Doctor, related_name='پزشک', on_delete=models.CASCADE, verbose_name="پزشک")
    rate_1 =models.IntegerField(default=4,validators=[MinValueValidator(0),
                                                  MaxValueValidator(4)] ,verbose_name='رضایت از نحوه مشاوره')
    rate_2 =models.IntegerField(default=4,validators=[MinValueValidator(0),
                                                  MaxValueValidator(4)] ,verbose_name='کیفیت راهنمایی')
    rate_3 =models.IntegerField(default=4,validators=[MinValueValidator(0),
                                                  MaxValueValidator(4)] ,verbose_name='نحوه برگزاری جلسه')
    rate_4 =models.IntegerField(default=4,validators=[MinValueValidator(0),
                                                  MaxValueValidator(4)] ,verbose_name='نظم جلسه مشاوره')
    text = models.TextField(verbose_name='متن نظر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    is_active = models.BooleanField(default=True, verbose_name="فعال /غیر فعال")

    def __str__(self):
        return str(self.doctor)
    @property
    def average_rating(self):
        return (self.rate_1 + self.rate_2 + self.rate_3 + self.rate_4) / 4
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # به‌روزرسانی میانگین امتیاز
        doctor = self.doctor
        doctor.rate_count = Rate_Doctor.objects.filter(doctor=doctor).aggregate(
            avg_rating=Avg((F('rate_1') + F('rate_2') + F('rate_3') + F('rate_4')) / 4)
        )['avg_rating'] or 0
        doctor.save()




