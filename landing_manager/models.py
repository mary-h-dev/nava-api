from django.db import models

STATUS_CHOICES =(
    ("1", "پاسخگو"),
    ("2", "عدم پاسخگویی"),
    ("2", "در حال بررسی"),
)
STATUS_NUMBER = (
    ("hot","داغ"),
    ("consultation","مشاوره ای")
)
ADVERTISING_PLATFORMS = (
    ("eitaa", "ایتا"),
    ("soroush", "سروش"),
    ("telegram", "تلگرام"),
    ("instagram", "اینستاگرام"),
)


class Campaign(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')
    def __str__(self):
        return self.name


class LandingPage(models.Model):
    name = models.CharField(max_length=255)
    campaign = models.ForeignKey(Campaign, related_name='landing_pages', on_delete=models.CASCADE, null=True, blank=True)
    cost = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)  # Cost of the landing page
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True, verbose_name='فعال/غیر فعال')

    def __str__(self):
        return self.name


class SubmissionLandingPage(models.Model):
    landing_page = models.ForeignKey(LandingPage, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    content = models.TextField(blank=True, null=True)
    utm_source = models.CharField(max_length=255, blank=True, null=True)
    utm_medium = models.CharField(max_length=255, blank=True, null=True)
    utm_campaign = models.CharField(max_length=255, blank=True, null=True)
    utm_content = models.CharField(max_length=255, blank=True, null=True)
    utm_term = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    advertising_platform = models.CharField(choices=ADVERTISING_PLATFORMS, max_length=100, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)  # Field for storing the session key
    created_at = models.DateTimeField(auto_now_add=True)
    status_number = models.CharField(choices=STATUS_NUMBER, max_length=200, blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=200,default=STATUS_CHOICES[0][0],blank=True,null=True)

    def __str__(self):
        return f"{self.phone_number} - {self.landing_page} -  - {self.created_at.date()}"




class landing_api_authorization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name




class AllowedIP(models.Model):
    """
    Model to store allowed IP addresses for restricted API access.
    """
    ip_address = models.GenericIPAddressField(unique=True)  # Ensures IPs are unique
    description = models.CharField(max_length=255, blank=True, null=True)  # Optional description field

    def __str__(self):
        return self.ip_address




def zip_upload_path(instance, filename):
    return f"uploads/landing_page_assets/{instance.landing_page.id}/{filename}"



class AssetUpload(models.Model):
    landing_page = models.ForeignKey(LandingPage, on_delete=models.CASCADE, related_name="assets")
    zip_file = models.FileField(upload_to=zip_upload_path, verbose_name="Upload Zip File")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assets for {self.landing_page.name} - Uploaded on {self.uploaded_at}"



class Counseling(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.full_name