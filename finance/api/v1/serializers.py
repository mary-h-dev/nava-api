from rest_framework import serializers
from finance.models import client_cash_in, UserBalance

class ClientCashSerializer(serializers.ModelSerializer):
    class Meta:
        model = client_cash_in
        fields = '__all__'

class UserBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalance
        fields = '__all__'