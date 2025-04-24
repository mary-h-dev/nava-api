from django.db import models
from accounts.models import User
from doctors.models import Doctor
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

# from products.models import Product


# Create your models here.
class Vlog_Category(models.Model):
    """
    this is a class to define categories for vlog table
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='نویسنده ورلاگ')
    title = models.CharField(max_length=250, verbose_name='عنوان دسته بندی ولاگ')
    parent = models.ForeignKey('Vlog_Category', null=True, blank=True, on_delete=models.CASCADE,
                               verbose_name='دسته بندی والد')
    image = models.ImageField(verbose_name=_("عکس"), help_text=_("یک عکس بارگذاری کنید"),
                              upload_to="upload/vlog/images", null=True, blank=True, )
    logo = models.ImageField(verbose_name=_("عکس"), help_text=_("یک عکس بارگذاری کنید"),
                             upload_to="brand/images/", null=True, blank=True)
    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    is_validated = models.BooleanField(null=True, verbose_name='تایید/عدم تایید')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))
    def __str__(self):
        if not self.slug:
            if self.title.isascii():
                name = slugify(self.title.replace(" ", "-"))
                slug = f"{name}"
            else:
                name = self.title.replace(" ", "-")
                slug = f"{name}"

            self.slug = slug
            # self.serial = random_num
        return self.title+ ' : ' +str(self.user)

    def save(self, *args, **kwargs):
        super(Vlog_Category, self).save(*args, **kwargs)




StatusVlog=[
        ('تایید', 'تایید'),
        ('عدم تایید', 'عدم تایید'),
    ]
class Vlog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='vlog')
    title = models.CharField(max_length=250, verbose_name='عنوان ویدیو')
    author = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='مدرس')
    video_banner = models.FileField(upload_to='upload/vlog/video_banner', verbose_name='ویدیو')
    video_photo = models.ImageField(upload_to='upload/vlog/video_photo', verbose_name='بنر ویدیو')
    voice = models.FileField(upload_to='upload/vlog/voice', verbose_name='voice',null=True, blank=True)
    price = models.IntegerField( default=0, verbose_name='قیمت',validators = [MinValueValidator(0)])
    discount_price = models.IntegerField(verbose_name='قیمت تخفیف خورده', null=True, blank=True)
    final_price = models.IntegerField(verbose_name='قیمت نهایی', null=True, blank=True)
    free_status = models.BooleanField(default=False, verbose_name='محصول رایگان')
    category = models.ForeignKey(Vlog_Category, on_delete=models.SET_NULL,
                                 null=True, verbose_name='دسته بندی مقاله')
    content = models.TextField(verbose_name='محتوای مقاله')
    description_author = models.FileField(upload_to='upload/vlog/mp3/description_author', null=True, blank=True,verbose_name='توضیحات مشاور')
    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)
    data_file = models.IntegerField(default=0, verbose_name='حجم فایل')
    Discount = models.IntegerField(default=0, verbose_name='تخفیف')
    # download_url = models.FileField(upload_to='upload/vlog')
    # about_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    # expertise_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد"))
    update_date = models.DateTimeField(auto_now=True,editable=False, verbose_name=("تاریخ بروزرسانی"))
    # status = models.CharField(max_length=100,choices=StatusVlog)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    is_validated = models.BooleanField(null=True, verbose_name='تایید/عدم تایید')
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.author)+' : '+self.title+ ' : '+ str(self.final_price)
    def author_doctor_name(self):
        return str(self.author.full_name)
    def save(self, *args, **kwargs):
        # Calculate the final price
        if self.discount_price is not None:
            self.final_price = self.discount_price
        else:
            self.final_price = self.price

        # Set the serial type
        # if self.Vlog:
        #     self.serial_type = self.Vlog.serial_type

        # Save the model instance
        super().save(*args, **kwargs)


class CommentsVlog(models.Model):
    auther = models.CharField(max_length=20)
    # title = models.CharField(max_length=250)
    vlog = models.ForeignKey(Vlog, on_delete=models.CASCADE)
    image = models.ImageField(
                              upload_to="vlog-comments/images/", null=True, blank=True, )
    text = models.TextField()
    image_2 = models.ImageField(
                              upload_to="vlog-comments/images/", null=True, blank=True, )
    text_2 = models.TextField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name =("کامنت در ولاگ")
        verbose_name_plural = _("کامنتهای ولاگها")

    def __str__(self):
        return self.auther
