
from django_filters.rest_framework import DjangoFilterBackend
from itsdangerous import serializer

from config.permissions import AdminAssistantOrIsAdmin, IsAdminOrIsSupporter
from appointment.api.v1.serializers import AppointmentFinalSerializer, PackageServiceSerializer
from .models import ReportUser, LibraryBookDoctor, TreatmentProcess, SaleExpert
# from Hamaram.permissions import Admin_AssistantOrIs_Admin
from accounts.models import Notification
from cart.models import Wallet, CartToCart, Charge_Wallet
from doctors.models import DoctorComment, DoctorCategory, Doctor
from podcast.models import PodcastCategory, Podcast
from tag.models import Tag
from .models import CommentReporting, Coupon, CouponType, SmsMessage, SmsTemplates
from .serializers import CommentReportingSerializer, CheckFinallyAppointmentSerializer, \
    CheckActiveBlogCategorySerializer, CouponSerializer, CouponTypeSerializer, CouponCodeSerializer, \
    CheckValidCommentsSerializers, CheckValidCommentsBlogSerializers, NotificationlistSerializer, \
    PriceFinalyTransactionSerializer, SmsSenderSerializer, SmsSenderSerializerList, SmsTemplatesSerilizers, \
    ExpertsAppointmentSerializers, PodcastCategoryAdminSerializer, BlogAdminSerializer, PodcastSerializers, \
    DoctorSerializers, TagAdminSerializer, ReportUserSerializers, LibraryBookDoctorSerializers, SaleExpertSerializers, \
    SaleExpertUserSerializers, AppointmentSerializer
from rest_framework import viewsets, status
from appointment.models import AppointmentFinal, PackageService, OrderPackage
from blog.models import BlogCategory, CommentsBlog, Blog
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .serializers import AddToWalletSerializer
from rest_framework.decorators import action
from kavenegar import *
from .paginations import DefaultPagination
from rest_framework import filters
from appointment.models import AppointmentFinal
# Create your views here.


class CheckValidProductViewSet(viewsets.ModelViewSet):
    serializer_class = CheckFinallyAppointmentSerializer
    http_method_names = ['get']
    pagination_class = DefaultPagination

    def get_queryset(self):
        return AppointmentFinal.objects.filter()


class CheckActiveCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CheckActiveBlogCategorySerializer
    http_method_names = ['get']
    pagination_class = DefaultPagination

    def get_queryset(self):
        return BlogCategory.objects.filter()


class CommentReportingViewSet(viewsets.ModelViewSet):
    serializer_class = CommentReportingSerializer
    queryset = CommentReporting.objects.all()
    http_method_names = ['get', 'post']
    pagination_class = DefaultPagination

    # def get_permissions(self):
    #     if self.action == 'create':
    #         return [permissions.IsAuthenticated()]
    #     elif self.action == 'list':
    #         return [permissions.IsAdminUser()]
    #     return super().get_permissions()


class CouponViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAdmin_VendorsOrReadOnly]
    serializer_class = CouponSerializer
    pagination_class = DefaultPagination
    queryset = Coupon.objects.all()

class CouponListByUser(generics.ListAPIView):
    serializer_class = CouponSerializer
    pagination_class = DefaultPagination
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Coupon.objects.filter(user_id = user_id)


class CouponTypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAdmin_VendorsOrReadOnly]
    serializer_class = CouponTypeSerializer
    queryset = CouponType.objects.all()
    pagination_class = DefaultPagination


def apply_coupon_to_service(package_service, coupon):
    if not coupon.is_active:
        raise ValueError("Coupon is not active.")

    # Assuming coupon.value is a discount
    if coupon.max_price > package_service.price:
        raise ValueError("Invalid coupon value.")

    return package_service.price - coupon.max_price


class ApplyCouponView(generics.GenericAPIView):
    serializer_class = CouponCodeSerializer
    queryset = Coupon.objects.all()  # Set queryset to all Coupons

    def post(self, request, package_service_id):
        # Validate the input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            package_service = PackageService.objects.get(id=package_service_id)
            coupon_code = serializer.validated_data['coupon_code']

            # Get the coupon using the validated coupon code
            coupon = self.get_queryset().get(coupon_code=coupon_code)

            discounted_price = apply_coupon_to_service(package_service, coupon)

            return Response({"discounted_price": discounted_price}, status=status.HTTP_200_OK)

        except PackageService.DoesNotExist:
            raise NotFound("PackageService not found.")
        except Coupon.DoesNotExist:
            raise NotFound("Coupon not found.")
        except ValueError as e:
            raise ValidationError(str(e))


##########################
##########################
##########################


def apply_coupon(user, coupon_code, price_approved):
    try:
        coupon = Coupon.objects.get(coupon_code=coupon_code, is_active=True)
    except Coupon.DoesNotExist:
        raise ValidationError("Coupon does not exist or is inactive.")

    # Check if the coupon is valid within the date range
    if not (coupon.valid_from <= timezone.now() <= coupon.valid_until):
        raise ValidationError("Coupon is not valid at this time.")

    # Check if the user is allowed to use this coupon
    if coupon.valid_users.exists() and user not in coupon.valid_users.all():
        raise ValidationError("You are not authorized to use this coupon.")

    # Check if the price_approved meets the minimum price requirement
    if price_approved < coupon.min_price:
        raise ValidationError("Price does not meet the minimum requirement.")

    # Check if the price_approved exceeds the maximum price allowed by the coupon
    if coupon.max_price and price_approved > coupon.max_price:
        raise ValidationError("Price exceeds the maximum allowed by the coupon.")

    # Check the number of uses
    if coupon.num_uses <= 0:
        raise ValidationError("This coupon has reached its usage limit.")

    # Check the user's usage limit
    user_usage_count = OrderPackage.objects.filter(user=user, package__coupon=coupon).count()
    if user_usage_count >= coupon.limit_user:
        raise ValidationError("You have reached the usage limit for this coupon.")

    # Calculate the discount amount
    discount_amount = calculate_discount(coupon, price_approved)

    # Decrease the usage count of the coupon
    coupon.num_uses -= 1
    coupon.save()

    # Adjust the price_approved
    price_approved -= discount_amount

    return price_approved


def calculate_discount(coupon, price_approved):
    # Implement your discount calculation logic
    # Example: 10% discount
    return price_approved * 0.10


class CouponApplyView(generics.GenericAPIView):
    serializer_class = CouponSerializer

    def post(self, request, *args, **kwargs):
        coupon_code = request.data.get('coupon_code')
        price_approved = request.data.get('price_approved')
        user = request.user

        # Call the apply_coupon function here
        calculate_discount(coupon_code, price_approved)
        try:
            new_price = apply_coupon(user, coupon_code, price_approved)
            return Response({"new_price": new_price}, status=200)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)


############charge walle by admin


class WalletView(APIView):
    permission_classes = [AdminAssistantOrIsAdmin]  # Only allow admin or admin assistant

    def get(self, request, user_id):
        """Retrieve the wallet balance for a specific user."""
        try:
            wallet = Wallet.objects.get(user_id=user_id)
            return Response({"balance": str(wallet.balance)}, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet does not exist for the specified user."},
                            status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id):
        """Add the transaction amount to the wallet balance for a specific user."""
        serializer = AddToWalletSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uuid = serializer.validated_data.get('uuid')

        try:
            with transaction.atomic():  # Ensure atomicity
                wallet = Wallet.objects.get(user_id=user_id)
                carttocart = CartToCart.objects.select_for_update().get(id=uuid)

                # Check if the transaction has already been processed
                if carttocart.is_paid:
                    return Response({"error": "This transaction has already been processed."},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Fetch amount from CartToCart and update wallet balance
                amount = carttocart.total_amount
                carttocart.is_paid = True
                carttocart.status  = "2"
                wallet.balance += amount
                wallet.save()
                carttocart.save()
                # Add notification for the user
                # چاپ کردن مقدار amount برای بررسی
                # print(f"Amount to be added: {amount}")  # خط دیباگ برای چک کردن مقدار amount

                # Create the notification message with the amount
                message = f"تراکنش شما با موفقیت تایید شد و مبلغ {amount} به ولت شما اضافه شد."

                # چاپ پیام نوتیفیکیشن برای بررسی
                # print(f"Notification message: {message}")  # چاپ پیام نوتیفیکیشن برای بررسی
                Notification.objects.create(
                    user=wallet.user,
                    message=message
                )
                return Response({"message": "Wallet balance updated successfully.",
                                 "new_balance": str(wallet.balance)},
                                status=status.HTTP_200_OK)

        except Wallet.DoesNotExist:
            return Response({"error": "Wallet does not exist for the specified user."},
                            status=status.HTTP_404_NOT_FOUND)
        except CartToCart.DoesNotExist:
            return Response({"error": "Transaction not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An error occurred while updating the wallet.",
                             "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#############

class DoctorCommentCheckListViews(generics.ListAPIView):
    queryset = DoctorComment.objects.all()
    serializer_class = CheckValidCommentsSerializers
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['text' ]


    def get_queryset(self):
        # CHECK VALID COMMENT BY DOCTOR ID
        doctor_id = self.kwargs['doctor_id']
        return DoctorComment.objects.filter(doctor_id=doctor_id)

class BlogCommentCheckListViews(generics.ListAPIView):
    queryset = CommentsBlog.objects.all()
    serializer_class = CheckValidCommentsBlogSerializers
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['text' ]
    def get_queryset(self):
        # CHECK VALID COMMENT BY BLOG ID
        blog_id = self.kwargs['blog_id']
        return CommentsBlog.objects.filter(blog_id=blog_id)



#########notifications unreadmark
class NotificationUnread(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationlistSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        # Only return notifications for the authenticated user
        user_id = self.kwargs['user_id']

        return Notification.objects.filter(user_id=user_id,is_read=False)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a single notification as read."""
        notification = self.get_object()
        if notification.user != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        notification.is_read = True
        notification.save()
        return Response(NotificationlistSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def send_notification(self, request):
        """Send a new notification to a user."""
        user = request.user
        message = request.data.get('message', None)

        if not message:
            return Response({"detail": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

        notification = Notification.objects.create(user=user, message=message)
        return Response(NotificationlistSerializer(notification).data, status=status.HTTP_201_CREATED)


class PriceFinalyTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = PriceFinalyTransactionSerializer
    queryset = Charge_Wallet.objects.filter(is_paid=True)



class SmsSenderPostView(generics.CreateAPIView):
    serializer_class = SmsSenderSerializer
    queryset = SmsMessage.objects.all()

    def create(self, request, *args, **kwargs):
        # Initialize the serializer with request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Perform the creation of the SmsMessage
        self.perform_create(serializer)

        # Extract validated data from the serializer
        title = serializer.validated_data['title']
        user_sender = serializer.validated_data['user_sender']
        user_receivers = serializer.validated_data['user_receiver']  # This will be a list of users
        message = serializer.validated_data['message']

        # Initialize the Kavenegar API
        api = KavenegarAPI(
            '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D')  # Use your actual Kavenegar API key

        # Clean the message to remove any unsupported characters and ensure UTF-8 encoding
        cleaned_message = str(message)

        for user_receiver in user_receivers:
            # Get the phone number from the user_receiver
            phone_number = user_receiver.Phone_Number  # Ensure that the User model has a Phone_Number field

            # Prepare the parameters for the SMS
            params = {
                'sender': '90009809',  # Sender's number (this might be your virtual number)
                'receptor': phone_number,  # Receiver's phone number
                'message': cleaned_message,  # Ensure the message is UTF-8 encoded and cleaned
            }

            # Send the SMS
            try:
                api.sms_send(params)
            except Exception as e:
                # Log the error or handle it as needed
                print(f"Error sending SMS to {phone_number}: {e}")

        return Response({"message": "پیام‌ها ارسال شدند."})

class SmsSenderListView(generics.ListAPIView):
    serializer_class = SmsSenderSerializerList
    queryset = SmsMessage.objects.all()
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'receiver']
    permission_classes = [IsAdminOrIsSupporter]

class SmsBySenderListView(generics.ListAPIView):
    serializer_class = SmsSenderSerializerList
    queryset = SmsMessage.objects.all()
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'receiver']
    permission_classes = [IsAdminOrIsSupporter]
    def get_queryset(self):
        sender_id = self.kwargs['sender_id']
        return SmsMessage.objects.filter(user_sender=sender_id)
class SmsTemplatesCreateView(generics.CreateAPIView):
    serializer_class = SmsTemplatesSerilizers
    queryset = SmsTemplates.objects.all()
    permission_classes = [IsAdminOrIsSupporter]

class SmsTemplatesListView(generics.ListAPIView):
    serializer_class = SmsTemplatesSerilizers
    queryset = SmsTemplates.objects.all()
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['template_name']
    permission_classes = [IsAdminOrIsSupporter]

class SmsTemplatesDetailView(generics.RetrieveAPIView):
    serializer_class = SmsTemplatesSerilizers
    queryset = SmsTemplates.objects.all()
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrIsSupporter]


class ExpertsByIdAppointment(generics.ListAPIView):
    serializer_class = ExpertsAppointmentSerializers
    queryset = AppointmentFinal.objects.all()
    def get_queryset(self):
        expert_id = self.kwargs['expert_id']

        return AppointmentFinal.objects.filter(coupon_submit__user__is_expert=expert_id)

class CheckActivePodcastCategoryViewSet(generics.ListAPIView):
    queryset = PodcastCategory.objects.all()
    serializer_class = PodcastCategoryAdminSerializer
    pagination_class = DefaultPagination

class CheckActivePodcastList(generics.ListAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializers
    pagination_class = DefaultPagination
class CheckActiveDoctorList(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializers
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = ['full_name']

class CheckActiveDoctorCategoryViewSet(generics.ListAPIView):
    queryset = DoctorCategory.objects.all()
    serializer_class = PodcastCategoryAdminSerializer
    pagination_class = DefaultPagination

class CheckActiveBlogList(generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class =BlogAdminSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    # ordering_fields = ['like_count',]
    search_fields = ['title', ]
    filterset_fields = [
        'like_count','view_count','created_date',

    ]
class CheckActiveTagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagAdminSerializer
    pagination_class = DefaultPagination

class ReportUserCreateViewset(generics.CreateAPIView):
    queryset = ReportUser.objects.all()
    serializer_class = ReportUserSerializers

class ReportUserListViewset(generics.ListAPIView):
    queryset = ReportUser.objects.all()
    serializer_class = ReportUserSerializers
    pagination_class = DefaultPagination
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        queryset = ReportUser.objects.filter(user_id=user_id)
        return queryset

class ReportUserDetailViewset(generics.RetrieveAPIView):
    queryset = ReportUser.objects.all()
    serializer_class = ReportUserSerializers

class ReportUserDeleteViewset(generics.DestroyAPIView):
    queryset = ReportUser.objects.all()
    serializer_class = ReportUserSerializers

class ReportUserUpdateViewset(generics.UpdateAPIView):
    queryset = ReportUser.objects.all()
    serializer_class = ReportUserSerializers
##########
class TreatmentProcessCreateViewset(generics.CreateAPIView):
    queryset = TreatmentProcess.objects.all()
    serializer_class = ReportUserSerializers

class TreatmentProcessListViewset(generics.ListAPIView):
    queryset = TreatmentProcess.objects.all()
    serializer_class = ReportUserSerializers
    pagination_class = DefaultPagination
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        queryset = TreatmentProcess.objects.filter(user_id=user_id)
        return queryset

class TreatmentProcessDetailViewset(generics.RetrieveAPIView):
    queryset = TreatmentProcess.objects.all()
    serializer_class = ReportUserSerializers

class TreatmentProcessDeleteViewset(generics.DestroyAPIView):
    queryset = TreatmentProcess.objects.all()
    serializer_class = ReportUserSerializers

class TreatmentProcessUpdateViewset(generics.UpdateAPIView):
    queryset = TreatmentProcess.objects.all()
    serializer_class = ReportUserSerializers
class LibraryBooksListView(generics.ListAPIView):
    queryset = LibraryBookDoctor.objects.all()
    serializer_class = LibraryBookDoctorSerializers

class LibraryBooksCreateView(generics.CreateAPIView):
    queryset = LibraryBookDoctor.objects.all()
    serializer_class = LibraryBookDoctorSerializers

class LibraryBooksDetailView(generics.RetrieveAPIView):
    queryset = LibraryBookDoctor.objects.all()
    serializer_class = LibraryBookDoctorSerializers

class LibraryBooksUpdateView(generics.UpdateAPIView):
    queryset = LibraryBookDoctor.objects.all()
    serializer_class = LibraryBookDoctorSerializers
class LibraryBooksDeleteView(generics.DestroyAPIView):
    queryset = LibraryBookDoctor.objects.all()
    serializer_class = LibraryBookDoctorSerializers


#sale expert
class SaleExpertCreateView(generics.CreateAPIView):
    queryset = SaleExpert.objects.all()
    serializer_class = SaleExpertSerializers

class SaleExpertListView(generics.ListAPIView):
    queryset = SaleExpert.objects.all()
    serializer_class = SaleExpertUserSerializers
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name']
class SaleExpertDetailView(generics.RetrieveAPIView):
    queryset = SaleExpert.objects.all()
    serializer_class = SaleExpertUserSerializers

class SaleExpertUpdateView(generics.UpdateAPIView):
    queryset = SaleExpert.objects.all()
    serializer_class = SaleExpertSerializers

class SaleExpertDeleteView(generics.DestroyAPIView):
    queryset = SaleExpert.objects.all()
    serializer_class = SaleExpertSerializers
class ExpertAppointmentByUserView(generics.ListAPIView):
    serializer_class = AppointmentFinalSerializer
    pagination_class = DefaultPagination
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return AppointmentFinal.objects.filter(expert_sale_id=user_id)

class ExpertAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    pagination_class = DefaultPagination
    def get_queryset(self):
        queryset = AppointmentFinal.objects.filter(booke_by_expert=True)
        return queryset
class PackageServiceExpertList(generics.ListAPIView):
    # queryset = PackageService.objects.all()
    serializer_class = PackageServiceSerializer
    pagination_class = DefaultPagination
    def get_queryset(self):
        queryset = PackageService.objects.filter(expert=True)
        return queryset

class PackageServiceAllList(generics.ListAPIView):
    queryset = PackageService.objects.all()
    serializer_class = PackageServiceSerializer
    pagination_class = DefaultPagination
