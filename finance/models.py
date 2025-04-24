from django.db import models
from accounts.models import Profile
from config import settings
User = settings.AUTH_USER_MODEL



#فاکتور برای درگاه
class client_cash_in(models.Model):
    title = models.CharField(max_length=150 ,default='',verbose_name='شرح ورودی')
    price = models.BigIntegerField(default=0,verbose_name='مبلغ')
    method = models.CharField(max_length=6,default='انلاین',verbose_name='روش پرداخت')
    online_ret = models.CharField(max_length=200,default='',blank=True,null=True,verbose_name='لینک ارجاع')
    gen_user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='gen_user_to_user',
                                 on_delete=models.CASCADE,null=True,blank=True,default=None,verbose_name='کاربر ایجاد کننده فاکتور')
    gen_date = models.DateTimeField(verbose_name='تاریخ ایجادفاکتور')
    confirmer_is_gate = models.BooleanField(default=False,verbose_name='تایید کننده ی پرداخت درگاه بانکی است؟')
    confirm_user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                     null=True,blank=True,verbose_name='کاربر تایید کننده')
    confirm_date = models.DateTimeField(blank= True,null=True,verbose_name='تاریخ تایید دریافت وجه')
    client = models.ForeignKey(Profile,on_delete=models.CASCADE,blank= True,null=True
                               ,default=None,verbose_name='کاربری که فاکتور برای او صادر شده است')
    is_paid = models.BooleanField(default=False,verbose_name='ایا پرداخت شده است؟')
    self_type = models.CharField(max_length=10, default='main',verbose_name='نوع سند مالی')
    obj_rel = models.CharField(max_length=10,verbose_name='فاکتور برای چه خدمتی است')
    obj_rel_id = models.BigIntegerField(verbose_name='کد خدمت')
    lawer_share = models.BigIntegerField(default=0,verbose_name='سهم پزشک')
    website_shar = models.BigIntegerField(default=0,verbose_name='سهم وبسایت')
    used_tariff = models.BigIntegerField(default=0,verbose_name='تعرفه اعمال شده')
    def __str__(self):
        return self.title

#درگاه
class idpay_main(models.Model):
    order_id = models.TextField()
    payment_id = models.TextField()
    amount = models.IntegerField(default='-')
    card_number = models.TextField(default="****")
    id_pay_track_id = models.IntegerField(default=0000)
    bank_track_id = models.TextField(default=0000)
    status = models.IntegerField(default=0)
    ret_url = models.CharField(max_length=250, default='',verbose_name='مسیر برگشت')
    cash_in = models.ForeignKey(client_cash_in, on_delete=models.CASCADE, verbose_name='فاکتور مربوطه')
    def __str__(self):
        return str(self.order_id) + ' ' + str(self.amount) + ' ' + str(self.status)

# کیف پول کاربر
class UserBalance(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,verbose_name='کاربر')
    balance = models.BigIntegerField(verbose_name='موجودی')
    def __str__(self):
        return "{} - {}".format(self.user, self.balance)
#توضیحات کیف پول کاربر
class UserBalanceDescriptions(models.Model):
    user =models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='کاریر')
    descriptions = models.CharField(max_length=500, default='',verbose_name='شرح')
    price = models.IntegerField(verbose_name='مبلغ')
    type = models.CharField(max_length=1, verbose_name='نوع تراکنش')
    transfer_kind = models.CharField(max_length=5, default='0',verbose_name='نحوه انتقال')
    date = models.DateField(verbose_name='تاریخ')

