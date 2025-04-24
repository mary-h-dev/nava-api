from django.urls import path ,include
from cart.api.v1.views import WalletChargeView, \
    ChargeWalletRequestView, ChargeWalletVerifyView, WalletListByUserView, CartToCartCreateView, OrderProductViews, \
    OrderPackageRequestPaymentView, MyFactorsCreateView, MyFactorsListView, MyFactorsUpdateView, MyFactorsDeleteView, \
    MyFactorsDetailView, CartToCartListView, CartToCartDetailView, CartToCartForeignerCreateView, \
    CartToCartForeignerlistView, CartToCartForeignerUpdateView, CartToCartForeignerDetailView, TransactionsListViewSet, \
    TransactionsListByUserViewSet, CartToCartListByUserView, PurchaseOrderListUserViewSet, TransactionsByRefidViewSet, \
    TransactionsDetailViewSet
from rest_framework.routers import DefaultRouter

urlpatterns = [

    path('charge_wallet/payment/request', ChargeWalletRequestView.as_view(), name='request-charge-wallet'),  # main
    path('charge_wallet/payment/verify/', ChargeWalletVerifyView.as_view(), name='verify-charge-wallet'),  # main

###############
    ####payment package
    path('orders/paymentpackegeorder/request/',OrderPackageRequestPaymentView.as_view(), name="payment-request-orderpackage"),
    #wallet
    path('charge_wallet/create/',WalletChargeView.as_view(), name='wallet_charge_amount_create'),
    path('wallet/charge/<int:pk>/', WalletChargeView.as_view(), name='wallet-charge-detail'),
    path('wallet/list/<int:user_id>', WalletListByUserView.as_view(), name='wallet-detail-by-user'),
    path('cart-to-cart/create/', CartToCartCreateView.as_view(), name='cart-to-cart-create'),
    path('cart-to-cart/list/', CartToCartListView.as_view(), name='cart-to-cart-list'),
    path('cart-to-cart/listbyuser/<int:user_id>', CartToCartListByUserView.as_view(), name='cart-to-cart-list_byuser'),
    path('cart-to-cart/update/<uuid:id>/', CartToCartDetailView.as_view(), name='cart-to-cart-detail'),
    path('order-product/create/',OrderProductViews.as_view(), name='order-product-request'),
    ####cart to cart foriegn
    path('cart-to-cartforeigner/create/', CartToCartForeignerCreateView.as_view(), name='cart-to-cartforeigner-create'),
    path('cart-to-cartforeigner/list/', CartToCartForeignerlistView.as_view(), name='cart-to-cartforeigner-list'),
    path('cart-to-cartforeigner/update/<int:pk>/', CartToCartForeignerUpdateView.as_view(), name='cart-to-cartforeigner-update'),
    path('cart-to-cartforeigner/detail/<int:pk>/', CartToCartForeignerDetailView.as_view(), name='cart-to-cartforeigner-detail'),
    #factors
    path('myfactors/create/',MyFactorsCreateView.as_view(), name='myfactors-create'),
    path('myfactors/list/',MyFactorsListView.as_view(), name='myfactors-list'),
    path('myfactors/update/<uuid:id>/',MyFactorsUpdateView.as_view(), name='myfactors-update'),
    path('myfactors/delete/<int:pk>/',MyFactorsDeleteView.as_view(), name='myfactors-update'),
    path('myfactors/detail/<uuid:id>/',MyFactorsDetailView.as_view(), name='myfactors-update'),
    #transactions
    path('transactions/listbyuser/<int:user_id>/',TransactionsListByUserViewSet.as_view(), name='transactions-userlist'),
    path('transactions/list',TransactionsListViewSet.as_view(), name='transactions-list'),
    path('transactions/refid/<int:refid_id>/',TransactionsByRefidViewSet.as_view(), name='transactions-refid'),
    path('transactions/detail/<int:pk>/',TransactionsDetailViewSet.as_view(), name='transactions-detail'),
    #PurchasOrder
    path('purchasorder/listbyuser/<int:user_id>/',PurchaseOrderListUserViewSet.as_view(), name='purchas')
    ]