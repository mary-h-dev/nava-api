from django.db import models
from rest_framework.fields import DateField
import accounts.models
from config import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from appointment.models import PackageService, AppointmentFinal
from vlog.models import Vlog
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import uuid
# Create your models here.
User = settings.AUTH_USER_MODEL

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0.00, verbose_name='Wallet Balance')


    def deduct_from_wallet(self, amount):
        if amount <= 0:
            raise ValidationError("Deduction amount must be positive.")
        if amount > self.balance:
            raise ValidationError("Insufficient balance.")
        self.balance -= amount
        self.save()

    def __str__(self):
        return f"{self.user}'s Wallet - Balance: {self.balance}"
    @receiver(post_save, sender=User)
    def save_Wallet(sender, instance, created, **kwargs):
        if created:
            Wallet.objects.create(user=instance)

class Charge_Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField(default=0.00, verbose_name='Charge wallet amount')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    authority = models.CharField(max_length=255, null=True, blank=True)  # For tracking payment authority
    RefID = models.CharField(max_length=50 , null=True , blank=True)
    Status = models.CharField(max_length=50, null=True, blank=True)
    callback_url = models.CharField(max_length=255, null=True, blank=True)
    redirect_front_url = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"{self.user}'s Charge wallet{self.wallet}"


class MyFactors(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(accounts.models.User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, null=True, blank=True)
    number_factors = models.CharField(max_length=100,null=True, blank=True)
    total_price = models.IntegerField(null=True, blank=True)
    final_pay_price = models.IntegerField(null=True, blank=True)
    discounted_price = models.IntegerField(null=True, blank=True)
    payment_status = models.CharField(max_length=128, null=True, blank=True)
    trackId = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=("تاریخ اخرین اپدیت"))
    order_item_data = JSONField(null=True, blank=True)

    def __str__(self):
        return f'history of orders with id {self.id}  is {self.user} and pay-status is {self.payment_status}'

class CartToCart(models.Model):
    STATUS_CHOICES = (
        ('1', 'در حال بررسی'),
        ('2', 'با موفقیت انجام شده'),
        ('3', 'رد شده'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID field
    user = models.ForeignKey(accounts.models.User, on_delete=models.CASCADE)
    photo_transactions = models.ImageField(upload_to='cart_cart/',verbose_name= 'رسید کارت به کارت', null=True, blank=True)
    total_amount = models.IntegerField(null=True, blank=True,verbose_name="مبلغ واریز شده")
    created_transactions = models.DateField(verbose_name="تاریخ تراکنیش")
    time_of_transactions = models.DateTimeField(verbose_name="ساعت تراکنش")
    number_of_transactions = models.CharField(max_length=100,null=True, blank=True,verbose_name="شماره پیگیری")
    cart_number = models.CharField(max_length=128,verbose_name="4 رقم اخر شماره کارت")
    status = models.CharField(max_length=150,choices=STATUS_CHOICES,default=1,null=True,blank=True,verbose_name="وضعیت")#
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده است؟")
    comment_status = models.TextField(null=True,blank=True,verbose_name="پاسخ وضعیت تراکنش")
    def __str__(self):
        return f'history of{self.user}  is {self.total_amount} and pay{self.is_paid}'
        # return f'history of is {self.total_amount} and pay{self.is_paid}'

class CartToCartForeigner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(accounts.models.User, on_delete=models.CASCADE)
    photo_transactions = models.ImageField(upload_to='carttocartForeigner/',verbose_name= 'رسید کارت به کارت خارجی', null=True, blank=True)
    total_amount = models.IntegerField(null=True, blank=True,verbose_name="مبلغ واریز شده")
    link_of_transactions = models.CharField(max_length=100,null=True, blank=True,verbose_name="لینک تراکنش")
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده است؟")
    def __str__(self):
        return f'history of{self.user} - pay{self.total_amount}'





class OrderProduct(models.Model):
    user = models.ForeignKey(accounts.models.User, on_delete=models.CASCADE)
    vlog = models.ForeignKey(Vlog, on_delete=models.CASCADE, null=True, blank=True)
    package_service = models.ForeignKey(PackageService, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField(verbose_name="قیمت محصول", null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    is_finaly = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Override save method to set price based on related Vlog or PackageService."""
        if self.vlog:
            self.price = self.vlog.final_price
        elif self.package_service:
            self.price = self.package_service.price
        else:
            self.price = 0  # Default to 0 if neither is present
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}'


class PurchaseOrder(models.Model):
    TYPE_SERVICE = (
        ('قرار ملاقات با پزشک', 'قرار ملاقات با پزشک'),
        ('تست روانشناسی', 'تست روانشناسی'),
        ('کارگاه های من', 'کارگاه های من'),
        ('پادکست', 'پادکست'),
        ('ولاگ', 'ولاگ'),
    )
    user = models.ForeignKey(accounts.models.User, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=150,choices=TYPE_SERVICE,default=1,null=True,blank=True)
    final_price = models.IntegerField(default=0,verbose_name="قیمت نهایی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد", null=True, blank=True)
    appointment = models.OneToOneField(AppointmentFinal, on_delete=models.CASCADE, null=True, blank=True)  # Add this field
    def __str__(self):
        return f'{self.user} + {self.service_type}+ {self.final_price}'

class FactorCounter(models.Model):
    service_type = models.CharField(max_length=50, unique=True)  # مثل "test" یا "appointment"
    last_number = models.IntegerField(default=1000)  # شماره شروع فاکتور

    def __str__(self):
        return f"{self.service_type} - Last Number: {self.last_number}"