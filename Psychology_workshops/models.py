from django.db import models
from doctors.models import Doctor
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from tag.models import Tag




class WorkshopCategory(models.Model):
    title = models.CharField(max_length=200,verbose_name="نام")
    image = models.ImageField(verbose_name=_("عکس"), help_text=_("یک عکس بارگذاری کنید"),
                              upload_to="blog-cat/images/", null=True, blank=True, )
    web_image = models.ImageField(verbose_name=_("عکس فشرده وب"),
                              upload_to="blog-cat/web-images/", null=True, blank=True, )

    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    is_validated = models.BooleanField(null=True, verbose_name='تایید/عدم تایید')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

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
        return reverse('WorkshopCategory-detail', kwargs={'slug': self.slug})
    def __str__(self):
        return self.title


class WorkShop(models.Model):
    title = models.CharField(max_length=200,verbose_name="نام کارگاه")
    category = models.ForeignKey(WorkshopCategory, on_delete=models.SET_NULL,verbose_name="دسته بندی", null=True)
    doctor = models.ForeignKey(Doctor,on_delete=models.SET_NULL,verbose_name="مدرس", null=True)
    date = models.DateField(verbose_name="تاریخ برگزاری",null=True,blank=True)
    locations = models.CharField(max_length=500,verbose_name="محل برگزاری",null=True,blank=True)
    price = models.DecimalField(max_digits=20,decimal_places=2,verbose_name="قیمت اولیه")
    discount = models.DecimalField(max_digits=20,decimal_places=2)
    final_price = models.DecimalField(max_digits=20,verbose_name='قیمت نهایی',decimal_places=2)
    content = models.TextField(verbose_name="محتوا")
    page_meta = models.CharField(verbose_name=_("متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    meta_descriptions = models.CharField(verbose_name=_("توضیحات متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    canolically = models.URLField(null=True,blank=True,verbose_name=_("کنولیکال"))
    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)
    tags = models.ManyToManyField(Tag, related_name='WorkShop', verbose_name='تگ بلاگ')
    keywords = models.CharField(max_length=600, null=True, blank=True, verbose_name='کلمات کلیدی')
    video = models.FileField(upload_to='workshops/videos/',verbose_name="یدیوی معرفی",null=True,blank=True)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
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
        return reverse('WorkShop-detail', kwargs={'slug': self.slug})
    def __str__(self):
        return self.title

class RegisterWorkshop(models.Model):
    work_shop = models.ForeignKey(WorkShop,on_delete=models.SET_NULL,verbose_name="ورکشاپ", null=True)
    full_name = models.CharField(max_length=200,verbose_name="نام و نام خانوادگی")
    phone_number = models.CharField(max_length=12,verbose_name="شماره همراه")
    content = models.TextField(verbose_name="محتوا")
    video = models.FileField(upload_to='workshops/register/videos',verbose_name="ویدیو")
    def __str__(self):
        return f"{self.full_name} {self.work_shop}"
