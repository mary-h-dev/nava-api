from django.db import models
from django.utils.text import slugify

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=500,unique=True,verbose_name="نام تگ")
    eng_title = models.CharField(max_length=500,unique=True,verbose_name="نام تگ به انگلیسی",blank=True)
    slug = models.SlugField(blank=True, db_index=True, max_length=360,
                            unique=True, verbose_name='عنوان در url', allow_unicode=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            if self.name.isascii():
                # random_num = random.randint(1000, 9999)
                name = slugify(self.name.replace(" ", "-"))
                slug = f"{name}"
            else:
                # random_num = random.randint(1000, 9999)
                name = self.name.replace(" ", "-")
                slug = f"{name}"

            self.slug = slug

        super().save(*args, **kwargs)
    def __str__(self):
        return self.name