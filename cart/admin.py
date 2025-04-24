from django.contrib import admin
from cart.models import Wallet, Charge_Wallet, OrderProduct, CartToCart, CartToCartForeigner, PurchaseOrder, MyFactors

# Register your models here.

admin.site.register(OrderProduct)
admin.site.register(Wallet)
admin.site.register(Charge_Wallet)
admin.site.register(CartToCart)
admin.site.register(CartToCartForeigner)
admin.site.register(PurchaseOrder)
admin.site.register(MyFactors)