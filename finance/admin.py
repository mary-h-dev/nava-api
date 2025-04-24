from django.contrib import admin
from finance.models import client_cash_in ,idpay_main,UserBalanceDescriptions,UserBalance
# Register your models here.


admin.site.register(client_cash_in)
admin.site.register(idpay_main)
admin.site.register(UserBalance)
admin.site.register(UserBalanceDescriptions)