import traceback
from django.db import transaction
from kavenegar import *
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated

from config.permissions import AdminAssistantOrIsAdminOrIsSupporter
from .paginations import DefaultPagination, MainPagination
from ...models import CartToCart, OrderProduct, MyFactors, CartToCartForeigner, PurchaseOrder
from appointment.models import PackageService, OrderPackage
from cart.api.v1.serializers import WalletSerializer, \
    Charge_WalletSerializer, CartToCartSerializer, OrderProductSerializer, ChargeWalletSerializer, OrderVisitSerializer, \
    MyFactorsSerializers, CartToCartForeignerSerializers, TransactionSerializers, PurchaseOrderSerializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cart.models import  Wallet
from cart.models import Charge_Wallet
import logging
import requests
from zeep import Client
from rest_framework import filters
from rest_framework.exceptions import NotFound
from django.http import HttpResponseRedirect

############################# zarin pal visit
MERCHANT  =  "6144f600-49e2-4391-9990-b39a6b0c8ccc"
ZP_API_REQUEST = f"https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://www.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://www.zarinpal.com/pg/StartPay/"
sandbox = False
amount = 1000  # Rial / Required
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
phone = 'YOUR_PHONE_NUMBER'  # Optional
# Important: need to edit for realy server.
CallbackURL = 'http://localhost:8000/order/payment/'
client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
logger = logging.getLogger(__name__)




class WalletChargeView(generics.CreateAPIView):
    queryset = Charge_Wallet.objects.all()
    serializer_class = ChargeWalletSerializer
    permission_classes = [IsAuthenticated]


#شارز ولت به مبلغ دلخواه


class WalletListByUserView(generics.ListAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.kwargs['user_id']
        # user = self.kwargs['user']
        return Wallet.objects.filter(user_id=user)

class CartToCartCreateView(generics.CreateAPIView):
    serializer_class = CartToCartSerializer
    queryset = CartToCart.objects.all()
    permission_classes = [IsAuthenticated]

class CartToCartListView(generics.ListAPIView):
    serializer_class = CartToCartSerializer
    queryset = CartToCart.objects.all()
    pagination_class = MainPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number_of_transactions',  ]
    ordering_fields = '__all__'
    lookup_field = 'slug'
    ordering = ('created_at',)
class CartToCartListByUserView(generics.ListAPIView):
    serializer_class = CartToCartSerializer
    queryset = CartToCart.objects.all()
    pagination_class = MainPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number_of_transactions',  ]
    ordering_fields = '__all__'
    lookup_field = 'slug'
    ordering = ('created_at',)
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        # user = self.kwargs['user']
        return CartToCart.objects.filter(user_id=user_id)

class CartToCartDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartToCartSerializer
    queryset = CartToCart.objects.all()
    lookup_field = 'id'  # Use UUID field for lookup
    permission_classes = [IsAuthenticated]



################################
#############################OrderProductViews
#این برای وقتی که میخواهیم فقط از طریق ولت شارژ شود و بعد سفارشات از مبلغ ولت کسر شود
class OrderProductViews(generics.CreateAPIView):
    serializer_class = OrderProductSerializer
    queryset = OrderProduct.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Create the order product instance
        order_product = serializer.save(user=self.request.user)
        print(f'Order Product Created: {order_product}')

        # Charge the user's wallet and handle potential errors
        return self.charge_wallet(order_product)

    def charge_wallet(self, order_product):
        try:
            # Use transaction.atomic to ensure atomicity
            with transaction.atomic():
                # Retrieve the wallet for the current user
                wallet = Wallet.objects.get(user=self.request.user)

                if wallet.balance < order_product.price:
                    return Response({'error': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST )

                # Deduct the price from the wallet balance
                wallet.balance -= order_product.price
                wallet.save()

                # Mark the order as paid
                order_product.is_finaly = True
                order_product.save()

                return Response({'message': 'Payment successful.', 'balance': str(wallet.balance)},
                                status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#MAIN REQUEST WALLET CHARGE
class ChargeWalletRequestView(APIView):
    serializer_class = ChargeWalletSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        origin = request.META.get('HTTP_ORIGIN')

        # Validate incoming data
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        amount = serializer.validated_data['amount']
        url_redirect = serializer.validated_data['url_redirect']
        # wallet = serializer.validated_data['wallet']
        user = request.user  # Assuming the user is authenticated
        callback_url = 'https://hamaramcore.liara.run/cart/api/v1/charge_wallet/payment/verify/'
        response = self.process_payment(amount, request.data.get('phone', ''), callback_url)
        # Check if payment was successful
        if response.status_code == 200 and response.data.get('status') is True:
            # Create a new Charge_Wallet instance for each transaction
            try:
                charge_wallet = Charge_Wallet(
                    user=user,
                    wallet=user.wallet,
                    # wallet=wallet,
                    amount=amount,
                    authority=response.data.get('authority'),
                    callback_url=callback_url,
                    redirect_front_url = url_redirect


                )
                charge_wallet.save()
            except Exception as e:
                logger.error(f"Error creating ChargeWallet: {str(e)}")
                return Response(
                    {'status': False, 'code': 'internal server error'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                'status': True,
                'url': response.data.get('url'),
                'authority': response.data.get('authority')
            })

        # Payment processing failed
        return response

    def process_payment(self, amount, phone, callback_url):
        data = {
            "MerchantID": MERCHANT,
            "Amount": amount,
            "Description": "Charge Wallet",
            "Phone": phone,
            "CallbackURL": callback_url,
        }

        headers = {
            'Content-Type': 'application/json',
        }

        try:
            # Send request to payment API
            response = requests.post(ZP_API_REQUEST, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('Status') == 100:
                    return Response({
                        'status': True,
                        'url': ZP_API_STARTPAY + str(response_data['Authority']),
                        'authority': response_data['Authority']
                    })
                return Response(
                    {'status': False, 'code': str(response_data.get('Status'))},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Invalid response from payment API
            return Response({'status': False, 'code': 'invalid response'}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.Timeout:
            return Response({'status': False, 'code': 'timeout'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.ConnectionError:
            return Response({'status': False, 'code': 'connection error'}, status=status.HTTP_502_BAD_GATEWAY)

logger = logging.getLogger(__name__)

class ChargeWalletVerifyView(APIView):
    serializer_class = ChargeWalletSerializer

    def get(self, request):
        status_param = request.GET.get('Status')
        authority_param = request.GET.get('Authority')
        try:
            payment = Charge_Wallet.objects.get(authority=authority_param)
            amount = payment.amount
        except Charge_Wallet.DoesNotExist:
            logger.error(f"Payment record not found for Authority: {authority_param}")
            return self.create_response(
                status=False,
                http_status=status.HTTP_404_NOT_FOUND,
                error={"code": "102", "message": "Payment record not found"}
            )
        if status_param != 'OK':
            logger.warning("Transaction failed or canceled by user")
            # return self.create_response(
            #     status=False,
            #     http_status=status.HTTP_400_BAD_REQUEST,
            #     error={"code": "100", "message": "Transaction failed or canceled by user"}
            # )
            # redirect_url = payment.redirect_front_url or "/default-failure-url/"
            # logger.warning(f"Payment verification failed, redirecting to {redirect_url}")
            # return HttpResponseRedirect(redirect_url)
            redirect_url = payment.redirect_front_url
            redirect = f"{redirect_url}/?id={payment.id}&status={status_param}"
                # logger.info(f"Payment successful, redirecting to {redirect_url}")
            return HttpResponseRedirect(redirect)
        if not authority_param:
            logger.warning("Authority parameter is missing")
            return self.create_response(
                status=False,
                http_status=status.HTTP_400_BAD_REQUEST,
                error={"code": "101", "message": "Authority parameter is missing"}
            )

        # try:
        #     payment = Charge_Wallet.objects.get(authority=authority_param)
        #     amount = payment.amount
        # except Charge_Wallet.DoesNotExist:
        #     logger.error(f"Payment record not found for Authority: {authority_param}")
        #     return self.create_response(
        #         status=False,
        #         http_status=status.HTTP_404_NOT_FOUND,
        #         error={"code": "102", "message": "Payment record not found"}
        #     )

        data = {
            "MerchantID": MERCHANT,
            "Amount": amount,
            "Authority": authority_param,
        }

        try:
            response = requests.post(ZP_API_VERIFY, json=data, headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            response_data = response.json()

            if not isinstance(response_data, dict) or 'Status' not in response_data:
                raise ValueError("Unexpected response format")
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error communicating with Zarinpal: {str(e)}")
            return self.create_response(
                status=False,
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
                error={"code": "103", "message": f"Error communicating with Zarinpal: {str(e)}"}
            )

        if response_data.get('Status') == 100:
            try:
                with transaction.atomic():
                    ref_id = response_data.get('RefID')
                    payment.status = "Successful"
                    payment.RefID = ref_id
                    payment.is_paid = True
                    payment.save()

                    if payment.wallet:
                        payment.wallet.balance += amount
                        payment.wallet.save()

                # redirect_url = payment.redirect_front_url or "/default-success-url/"

                redirect_url = payment.redirect_front_url
                redirect = f"{redirect_url}/?id={payment.id}&status={status_param}"
                # logger.info(f"Payment successful, redirecting to {redirect_url}")
                return HttpResponseRedirect(redirect)
            # except :
            #     redirect_url = payment.redirect_front_url or "/default-failure-url/"
            #     logger.warning(f"Payment verification failed, redirecting to {redirect_url}")
            #     return HttpResponseRedirect(redirect_url)

            except Exception as e:
                logger.error(f"Error processing payment for Authority: {authority_param} - {str(e)}")
                return self.create_response(
                    status=False,
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    error={"code": "104", "message": "Error updating payment records"}
                )
        redirect_url = payment.redirect_front_url
        redirect = f"{redirect_url}/?id={payment.id}&status={status_param}"
                # logger.info(f"Payment successful, redirecting to {redirect_url}")
        return HttpResponseRedirect(redirect)
        # redirect_url = payment.redirect_front_url or "/default-failure-url/"
        # logger.warning(f"Payment verification failed, redirecting to {redirect_url}")
        # return HttpResponseRedirect(redirect_url)

    def create_response(self, status: bool, http_status: int, error: dict):
        return Response(
            {
                "status": status,
                "http_status": http_status,
                "error": error,
            },
            status=http_status
        )

class ChargeWalletVerifyView0(APIView):
    serializer_class = ChargeWalletSerializer

    def get(self, request):
        status_param = request.GET.get('Status')
        authority_param = request.GET.get('Authority')

        if status_param != 'OK':
            return self.create_response(
                status=False,
                http_status=status.HTTP_400_BAD_REQUEST,
                error={"code": "100", "message": "Transaction failed or canceled by user"}
            )

        if not authority_param:
            return self.create_response(
                status=False,
                http_status=status.HTTP_400_BAD_REQUEST,
                error={"code": "101", "message": "Authority parameter is missing"}
            )

        try:
            payment = Charge_Wallet.objects.get(authority=authority_param)
            amount = payment.amount
        except Charge_Wallet.DoesNotExist:
            return self.create_response(
                status=False,
                http_status=status.HTTP_404_NOT_FOUND,
                error={"code": "102", "message": "Payment record not found"}
            )

        data = {
            "MerchantID": MERCHANT,
            "Amount": amount,
            "Authority": authority_param,
        }

        try:
            response = requests.post(ZP_API_VERIFY, json=data, headers={'Content-Type': 'application/json'})
            response.raise_for_status()  # Raise exception for HTTP errors
            response_data = response.json()
        except requests.RequestException as e:
            return self.create_response(
                status=False,
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
                error={"code": "103", "message": f"Error communicating with Zarinpal: {str(e)}"}
            )

        if response_data.get('Status') == 100:
            ref_id = response_data.get('RefID')
            payment.status = "Successful"
            payment.RefID = ref_id
            payment.is_paid = True
            payment.save()

            payment.wallet.balance += amount
            payment.wallet.save()

            redirect_url = payment.redirect_front_url or "/default-success-url/"
            return HttpResponseRedirect(redirect_url)
        elif response_data.get('Status') != 100:
                redirect_url = payment.redirect_front_url
                return HttpResponseRedirect(redirect_url)
        return self.create_response(
            status=False,
            http_status=status.HTTP_400_BAD_REQUEST,
            error={"code": str(response_data.get('Status')), "message": "Payment verification failed"}
        )

    def create_response(self, status: bool, http_status: int, error: dict):
        return Response(
            {
                "status": status,
                "http_status": http_status,
                "error": error,
            },
            status=http_status
        )

class PaymentCallbackView0(APIView):
    def post(self, request):
        authority = request.data.get('Authority')
        status = request.data.get('Status')

        if status != 'OK':
            logger.error(f"Payment failed for Authority: {authority}")
            return Response({'status': False, 'code': 'payment failed'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            current_order = Charge_Wallet.objects.get(authority=authority)
            current_order.is_paid = True
            current_order.save()

            # Update user's wallet balance
            user_wallet = current_order.wallet
            user_wallet.balance += current_order.amount
            user_wallet.save()

            return Response({'status': True, 'message': 'Payment successful'}, status=status.HTTP_200_OK)

        except Charge_Wallet.DoesNotExist:
            logger.error(f"Charge wallet not found for Authority: {authority}")
            return Response({'status': False, 'code': 'order not found'}, status=status.HTTP_404_NOT_FOUND)


#################################################################
class OrderPackageRequestPaymentView1(generics.CreateAPIView):
    serializer_class = OrderVisitSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        user = request.user  # Assuming the user is authenticated
        try:
            # Create or get a ChargeWallet instance
            current_order, created = OrderPackage.objects.get_or_create(is_paid=False, user_id=request.user.id)

        except OrderPackage.DoesNotExist:
            return Response({'status': False, 'code': 'order not found'}, status=status.HTTP_404_NOT_FOUND)

        # Prepare payment request
        total_price = current_order.price  # Now this should work without errors
        data = {
            "MerchantID": MERCHANT,
            "Amount": total_price,
            "Description": description,
            "Phone": phone,
            "CallbackURL": CallbackURL,
        }
        data = json.dumps(data)
        # set content length by data
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        try:
            response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)

            if response.status_code == 200:
                response = response.json()
                if response['Status'] == 100:
                    return Response({'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
                            'authority': response['Authority']})
                else:
                    return {'status': False, 'code': str(response['Status'])}
            return response

        except requests.exceptions.Timeout:
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'code': 'connection error'}


class OrderPackageRequestPaymentView(APIView):
    serializer_class = OrderVisitSerializer
    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)

        user = request.user  # Assuming the user is authenticated
        try:
            # Create or get a ChargeWallet instance
            current_order, created = OrderPackage.objects.get_or_create(is_paid=False, user_id=request.user.id)

        except OrderPackage.DoesNotExist:
            return Response({'status': False, 'code': 'order not found'}, status=status.HTTP_404_NOT_FOUND)

        # Prepare payment request
        total_price = current_order.price  # Now this should work without errors
        data = {
            "MerchantID": MERCHANT,
            "Amount": total_price,
            "Description": description,
            "Phone": phone,
            "CallbackURL": CallbackURL,
        }
        data = json.dumps(data)
        # set content length by data
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        try:
            response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)

            if response.status_code == 200:
                response = response.json()
                if response['Status'] == 100:
                    return Response({'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
                            'authority': response['Authority']})
                else:
                    return {'status': False, 'code': str(response['Status'])}
            return response

        except requests.exceptions.Timeout:
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'code': 'connection error'}
###############
#FACTORS
class MyFactorsCreateView(generics.CreateAPIView):
    queryset = MyFactors.objects.all()
    serializer_class = MyFactorsSerializers
    permission_classes = [IsAuthenticated]

class MyFactorsListView(generics.ListAPIView):
    queryset = MyFactors.objects.all()
    serializer_class = MyFactorsSerializers
    permission_classes = [IsAuthenticated]


class MyFactorsUpdateView(generics.UpdateAPIView):
    queryset = MyFactors.objects.all()
    serializer_class = MyFactorsSerializers
    permission_classes = [IsAuthenticated]



class MyFactorsDeleteView(generics.DestroyAPIView):
    queryset = MyFactors.objects.all()
    serializer_class = MyFactorsSerializers
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]



class MyFactorsDetailView(generics.RetrieveAPIView):
    queryset = MyFactors.objects.all()
    serializer_class = MyFactorsSerializers
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'



#carttocartforeigner
class CartToCartForeignerlistView(generics.ListAPIView):
    queryset = CartToCartForeigner.objects.all()
    serializer_class = CartToCartForeignerSerializers

class CartToCartForeignerCreateView(generics.CreateAPIView):
    queryset = CartToCartForeigner.objects.all()
    serializer_class = CartToCartForeignerSerializers

class CartToCartForeignerDetailView(generics.RetrieveAPIView):
    queryset = CartToCartForeigner.objects.all()
    serializer_class = CartToCartForeignerSerializers
    lookup_field = 'id'

class CartToCartForeignerUpdateView(generics.UpdateAPIView):
    queryset = CartToCartForeigner.objects.all()
    serializer_class = CartToCartForeignerSerializers
class TransactionsListViewSet(generics.ListAPIView):
    queryset = Charge_Wallet.objects.all()
    serializer_class = TransactionSerializers
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ('-created_at',)

class TransactionsDetailViewSet(generics.RetrieveAPIView):
    queryset = Charge_Wallet.objects.all()
    serializer_class = TransactionSerializers
    permission_classes = [IsAuthenticated]

class TransactionsListByUserViewSet(generics.ListAPIView):
    serializer_class = TransactionSerializers
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        # Retrieve Charge_Wallet_id from the URL kwargs
        user_id = self.kwargs.get('user_id')
        if not user_id:
            raise NotFound("Charge Wallet ID not provided.")

        # Filter Charge_Wallet objects
        queryset = Charge_Wallet.objects.filter(user_id=user_id)

        # Ensure the queryset is not empty
        if not queryset.exists():
            raise NotFound("Charge Wallet with the specified ID does not exist.")

        return queryset
class TransactionsByRefidViewSet(generics.ListAPIView):
    serializer_class = TransactionSerializers
    def get_object(self):
        refid_id = self.kwargs.get('refid_id')  # Extract `refid_id` from the URL
        try:
            # Fetch the single transaction matching the RefID
            return Charge_Wallet.objects.get(RefID=refid_id)
        except Charge_Wallet.DoesNotExist:
            raise NotFound({"status": 404, "error": "Transaction not found"})

    def get(self, request, *args, **kwargs):
        # Serialize the single object and return the response
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response({"status": 200, "data": serializer.data, "error": []})
class PurchaseOrderListUserViewSet(generics.ListAPIView):
    serializer_class = PurchaseOrderSerializers
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    ordering_fields = ['created_at']
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return PurchaseOrder.objects.filter(user_id=user_id)

