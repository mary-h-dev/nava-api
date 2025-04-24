from rest_framework import serializers
from django.contrib.auth import get_user_model
from appointment.models import OrderPackage
from ...models import Charge_Wallet, CartToCart, OrderProduct, OrderProduct, MyFactors, \
    CartToCartForeigner, PurchaseOrder
from cart.models import Wallet



class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance']

class Charge_WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Charge_Wallet
        fields =['id', 'user',"amount"]
        # fields = "__all__"

class CartToCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartToCart
        fields = "__all__"
        read_only_fields = ['is_paid','created_at']

# class CartToCartUpdateSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = CartToCart
#         fields = "__all__"
#         read_only_fields = ['created_at']

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = '__all__'
        Readonly_fields = ['is_paid','created_at']
class OrderVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPackage
        fields = ['id', 'user']

class ChargeWalletSerializer(serializers.ModelSerializer):
    url_redirect = serializers.CharField()
    class Meta:
        model = Charge_Wallet
        fields = "__all__"
        Readonly_fields = ['is_paid','wallet']

class MyFactorsSerializers(serializers.ModelSerializer):
    class Meta:
        model = MyFactors
        fields = '__all__'

class CartToCartForeignerSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartToCartForeigner
        fields = '__all__'
####################
class TransactionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Charge_Wallet
        fields = '__all__'

class PurchaseOrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'