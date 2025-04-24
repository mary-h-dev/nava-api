from rest_framework.permissions import AllowAny
from config import settings
from finance.api.v1.serializers import ClientCashSerializer,UserBalanceSerializer
from finance.models import client_cash_in ,UserBalance
from rest_framework import generics, authentication, request



class FainanceCreateViews(generics.CreateAPIView):
    serializer_class = ClientCashSerializer
    queryset = client_cash_in.objects.all()
    permission_classes = [AllowAny]

class FainanceListViews(generics.ListAPIView):
    serializer_class = ClientCashSerializer
    queryset =  client_cash_in.objects.all()
    permission_classes = [AllowAny]

class FainanceUpdateViews(generics.RetrieveUpdateAPIView):
    serializer_class = ClientCashSerializer
    queryset =  client_cash_in.objects.all()
    permission_classes = [AllowAny]

class FainancedeleteViews(generics.DestroyAPIView):
    serializer_class = ClientCashSerializer
    queryset = client_cash_in.objects.all()
    permission_classes = [AllowAny]

#user balance
class UserBalanceListViews(generics.ListAPIView):
    serializer_class = UserBalanceSerializer
    queryset = UserBalance.objects.all()
    permission_classes = [AllowAny]






