from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

import tag
from tag.models import Tag
from accounts.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.

# مدل تست روانشناسی
class Test(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان تست")
    description = models.TextField(blank=True, verbose_name="توضیحات تست")
    category = models.CharField(
        max_length=100,
        choices=[
            ('stress', 'استرس'),
            ('anxiety', 'اضطراب'),
            ('depression', 'افسردگی')
        ],
        verbose_name="دسته‌بندی تست"
    )
    low_threshold = models.PositiveIntegerField(default=10, verbose_name="آستانه پایین")
    medium_threshold = models.PositiveIntegerField(default=20, verbose_name="آستانه متوسط")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "تست"
        verbose_name_plural = "تست‌ها"


# مدل دسته‌بندی MBTI
class Category(models.Model):
    code = models.CharField(max_length=2, unique=True, verbose_name="کد دسته‌بندی")
    name = models.CharField(max_length=50, verbose_name="نام دسته‌بندی")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "دسته‌بندی MBTI"
        verbose_name_plural = "دسته‌بندی‌های MBTI"


# مدل سوالات
class Question(models.Model):
    text = models.CharField(max_length=255, verbose_name="متن سوال")
    weight = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="وزن سوال"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="دسته‌بندی MBTI"
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات"


# مدل گزینه‌های پاسخ
class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        related_name='choices',
        on_delete=models.CASCADE,
        verbose_name="سوال"
    )
    text = models.CharField(max_length=255, verbose_name="متن گزینه")
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="امتیاز گزینه"
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "گزینه"
        verbose_name_plural = "گزینه‌ها"


# مدل پاسخ‌های کاربر
class UserResponse(models.Model):
    user_id = models.CharField(max_length=255, verbose_name="شناسه کاربر")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="سوال"
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        verbose_name="گزینه انتخابی"
    )

    class Meta:
        verbose_name = "پاسخ کاربر"
        verbose_name_plural = "پاسخ‌های کاربران"
        unique_together = ('user_id', 'question')  # هر کاربر فقط یک پاسخ به هر سوال می‌دهد


# مدل نتیجه MBTI
class MBTIResult(models.Model):
    user_id = models.CharField(max_length=255, unique=True, verbose_name="شناسه کاربر")
    mbti_type = models.CharField(max_length=4, verbose_name="نوع MBTI")
    scores = models.JSONField(verbose_name="امتیازات دسته‌ها")
    description = models.TextField(verbose_name="توضیحات شخصیت")
    analysis = models.TextField(verbose_name="تحلیل نتیجه")
    suggestions = models.TextField(verbose_name="پیشنهادات برای توسعه شخصیتی")

    def __str__(self):
        return f"{self.user_id} - {self.mbti_type}"

    class Meta:
        verbose_name = "نتیجه تست MBTI"
        verbose_name_plural = "نتایج تست MBTI"
#######################
class TestCategory(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="نام")
    photo = models.ImageField(upload_to='test/pictures', verbose_name="عکس")
    web_photo = models.ImageField(upload_to='test/pictures/logo', verbose_name="لوگو")
    short_description = models.TextField(verbose_name="توضیحات کوتاه")
    content = models.TextField(verbose_name="محتوا")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="عنوان در url")
    tags = models.ManyToManyField(Tag, related_name='TestCategory', verbose_name='تگ بلاگ')
    price = models.IntegerField(verbose_name="قیمت")
    keywords = models.CharField(max_length=600, null=True, blank=True, verbose_name='کلمات کلیدی')
    page_meta = models.CharField(verbose_name=_("متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    meta_descriptions = models.CharField(verbose_name=_("توضیحات متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    canolically = models.URLField(null=True,blank=True,verbose_name=_("کنولیکال"))
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ اپدیت")
    is_free = models.BooleanField(default=False, verbose_name="رایگان")
    no_index = models.BooleanField(default=False)
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
        return reverse('psychological_test:test-category-detail', kwargs={'slug': self.slug})
    def __str__(self):
        return self.title

class TestResultUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="کاربر")
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE,verbose_name="دسته بندی")
    final_score = models.CharField(max_length=200, null=True, blank=True)
    detail_test = models.JSONField(verbose_name="پاسخ با جزییات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    chart_content = models.JSONField(verbose_name="نمودار نمایشی")
    def __str__(self):
        return str(self.user)

class TypeTest(models.Model):
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE,verbose_name="دسته بندی")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    short_result = models.CharField(max_length=500, verbose_name="پاسخ کوتاه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    def __str__(self):
        return self.title

class FinalResult(models.Model):
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE,verbose_name="دسته بندی")
    title = models.CharField(max_length=200, verbose_name="عنوان",null=True, blank=True)
    long_result = models.TextField(verbose_name="پاسخ کامل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    short_result = models.ForeignKey(TypeTest,on_delete=models.CASCADE, verbose_name="پاسخ کوتاه")
    photo = models.ImageField(upload_to='psychology/pic/',verbose_name="عکس")
    def __str__(self):
        return self.title