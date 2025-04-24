from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from blog.models import AuthorList
from doctors.models import Doctor
from django.utils.text import slugify
from django.urls import reverse
from tag.models import Tag


# Create your models here.
class PodcastCategory(models.Model):
    title = models.CharField(max_length=250, verbose_name='عنوان دسته بندی پادکست')
    parent = models.ForeignKey('PodcastCategory', null=True, blank=True, on_delete=models.CASCADE,
                               verbose_name='دسته بندی والد')
    image = models.ImageField(verbose_name=_("عکس"), help_text=_("یک عکس بارگذاری کنید"),
                              upload_to="podcast-cat/images/", null=True, blank=True, )
    web_image = models.ImageField(verbose_name=_("عکس فشرده وب"),
                              upload_to="podcast-cat/web-images/", null=True, blank=True, )

    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)

    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    is_validated = models.BooleanField(null=True, verbose_name='تایید/عدم تایید')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))
    def save(self, *args, **kwargs):
        if not self.slug:
            if self.title.isascii():
                title = slugify(self.title.replace(" ", "-"))
                slug = f"{title}"
            else:
                title = self.title.replace(" ", "-")
                slug = f"{title}"
            self.slug = slug
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('PodcastCategory-detail', kwargs={'slug': self.slug})
    def __str__(self):
        return self.title


class Podcast(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name= 'نام کاربر',null=True,blank=True)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE, blank=True,null=True,related_name='doctors',verbose_name='پزشک')
    author = models.ForeignKey(AuthorList, on_delete=models.CASCADE, verbose_name='نویسنده ی مقاله',null=True, blank=True)
    title = models.CharField(max_length=300, verbose_name='نام پادکست')
    category = models.ForeignKey(PodcastCategory, on_delete=models.SET_NULL,null=True, verbose_name='دسته بندی پادکست')
    time_durations = models.IntegerField(verbose_name='مدت زمان')
    price = models.IntegerField(verbose_name='قیمت نهایی به تومان',default=0)
    first_price = models.IntegerField(verbose_name='قیمت اولیه',default=0)
    discount_price = models.IntegerField(verbose_name='تخفیف بر حسب تومان',default=0)
    is_free = models.BooleanField(verbose_name='رایگان است؟',default=False)
    description = models.TextField(verbose_name='توضیحات')
    file = models.FileField(upload_to='podcasts/%Y/%m/%d',null=True,blank=True,verbose_name='فایل')
    image = models.ImageField(upload_to='podcast_images/', verbose_name='تصویر پادکست')
    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)
    content = models.TextField(verbose_name='محتوای پادکست')
    page_meta = models.CharField(verbose_name=_("متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    meta_descriptions = models.CharField(verbose_name=_("توضیحات متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    canolically = models.URLField(null=True,blank=True,verbose_name=_("کنولیکال"))
    tags = models.ManyToManyField(Tag, related_name='Podcast', verbose_name='تگ پادکست')
    keywords = models.CharField(max_length=600, null=True, blank=True, verbose_name='کلمات کلیدی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ اپدیت')
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیرفعال')
    is_validate = models.BooleanField(default=True, verbose_name='تایید/عدم تایید')

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            if self.title.isascii():
                slug = slugify(self.title.replace(" ", "-"))
            else:
                slug = self.title.replace(" ", "-")
            self.slug = slug

        # Adjust price based on discount
        if self.discount_price > 0:
            self.price = max(0, self.first_price - self.discount_price)
        else:
            self.price = self.first_price

        # Save the instance
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('Podcast-detail', kwargs={'slug': self.slug})
    def get_final_price(self):
        """Calculate the final price after discount."""
        return max(0, self.price - self.discount_price)

    def __str__(self):
        return self.title

class LikePodcastPost(models.Model):
    Podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.IntegerField(default=0)
    def __str__(self):
        # return self.blog + " - " + self.like
        return f'like count {self.like} on {self.Podcast}'
class CommentsPodcast(models.Model):
    auther = models.CharField(max_length=20)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    text = models.TextField()
    is_active = models.BooleanField(default=False, verbose_name=_("تایید/عدم تایید"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name =("کامنت در پادکست")
        verbose_name_plural = _("کامنتهای پادکست")

    def __str__(self):
        return self.auther


