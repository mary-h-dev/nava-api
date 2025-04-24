from django.db import models
from config import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from doctors.models import Doctor
from tag.models import Tag
from django.urls import reverse
# Create your models here.

User = settings.AUTH_USER_MODEL


class BlogCategory(models.Model):
    """
    this is a class to define categories for blog table
    """
    title = models.CharField(max_length=250, verbose_name='عنوان دسته بندی مقاله')
    parent = models.ForeignKey('BlogCategory', null=True, blank=True, on_delete=models.CASCADE,
                               verbose_name='دسته بندی والد')
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
        return reverse('BlogCategory-detail', kwargs={'slug': self.slug})
    def __str__(self):
        return f"{self.title} (Parent: {self.parent.title if self.parent else 'None'})"

class AuthorList(models.Model):
    author = models.CharField(max_length=300 ,verbose_name='نام نویسنده')

    def __str__(self):
        return self.author

class Blog(models.Model):
    """
    this is a class to define posts for blog app
    """
    author = models.ForeignKey(AuthorList, on_delete=models.CASCADE, verbose_name='نویسنده ی مقاله',null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر',null=True, blank=True)
    doctorname = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='اسم دکتر',null=True, blank=True)
    image_url = models.ImageField(verbose_name=_("عکس"), help_text=_("یک عکس بارگذاری کنید"),
                                  upload_to="blog/images/", null=True, blank=True)
    web_image = models.ImageField(verbose_name=_("عکس فشرده وب"),
                                  upload_to="blog/web-images/", null=True, blank=True)
    title = models.CharField(max_length=250, verbose_name='عنوان مقاله')
    description = models.TextField(verbose_name='عنوان کوتاه', null=True, blank=True)
    content = models.TextField(verbose_name='محتوای مقاله')
    page_meta = models.CharField(verbose_name=_("متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    meta_descriptions = models.CharField(verbose_name=_("توضیحات متای صفحه"), help_text=_("برای صفحه  متایی بنویسید"),
                                max_length=200, null=True, blank=True)
    canolically = models.URLField(null=True,blank=True,verbose_name=_("کنولیکال"))
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    is_validated = models.BooleanField(default=True, verbose_name='تایید/عدم تایید')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL,
                                 null=True,blank=True, verbose_name='دسته بندی مقاله')
    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)
    tags = models.ManyToManyField(Tag, related_name='blog', verbose_name='تگ بلاگ')
    keywords = models.CharField(max_length=600, null=True, blank=True, verbose_name='کلمات کلیدی')
    read_time = models.IntegerField(default=5,null=True, blank=True, verbose_name='زمان خواندن مقاله')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
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
        return reverse('blog-detail', kwargs={'slug': self.slug})
    # comments
    def __str__(self):
        return self.title



class LikeBlogPost(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.IntegerField(default=0)
    def __str__(self):
        # return self.blog + " - " + self.like
        return f'like count {self.like} on {self.blog}'


class BlogImage(models.Model):
    """
    The Blog Image table.
    """

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="blog_image")
    image_url = models.ImageField(verbose_name=_("عکس"), help_text=_("یک عکس بارگذاری کنید"),
                                  upload_to="blog/images/")
    web_image = models.ImageField(verbose_name=_("عکس فشرده وب"),
                                  upload_to="blog/web-images/", null=True, blank=True, )
    is_active = models.BooleanField(default=False, verbose_name='فعال/غیر فعال')
    alt_text = models.CharField(verbose_name=_("متن جایگزین عکس"),help_text=_("برای عکس توضیحی بنویسید"),
                                max_length=255,null=True,blank=True)
    description = models.CharField(max_length=360, null=True, blank=True, verbose_name='توضیحات کوتاه')
    is_feature = models.BooleanField(default=False, verbose_name=_("عکس اصلی"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=("تاریخ ایجاد "))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))

    class Meta:
        verbose_name = _("عکس مقاله")
        verbose_name_plural = _("عکس های مقالات")

    def __str__(self):
        return f'image of ({self.alt_text})'


class CommentsBlog(models.Model):
    auther = models.CharField(max_length=20)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    text = models.TextField()
    is_active = models.BooleanField(default=False, verbose_name=_("تایید/عدم تایید"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name =("کامنت در مقاله")
        verbose_name_plural = _("کامنتهای مقالات")

    def __str__(self):
        return self.auther
