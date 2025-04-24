from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from rest_framework import status
from django.core.exceptions import ValidationError
from cart.models import Wallet, MyFactors, PurchaseOrder, FactorCounter
from ...models import TestResultUser, TypeTest, FinalResult
from .paginations import DefaultPagination
from ...models import Question, UserResponse, MBTIResult, Category, Test, Choice, TestCategory
from rest_framework import viewsets
from .serializers import (
    TestSerializer, CategorySerializer, QuestionSerializer,
    ChoiceSerializer, UserResponseSerializer, MBTIResultSerializer, TestCategorySerializers, TestResultUserSerializers,
    TestResultUserCreateSerializers, TypeTestSerializers, FinalResultsSerializers,
    TypeTestMainSerializers
)
import uuid
from django.db.models import Max
from django.db.models import F

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class UserResponseViewSet(viewsets.ModelViewSet):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer


class MBTIResultViewSet(viewsets.ModelViewSet):
    queryset = MBTIResult.objects.all()
    serializer_class = MBTIResultSerializer


class CalculateMBTIResult(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        responses = UserResponse.objects.filter(user_id=user_id)

        if not responses.exists():
            return Response({"error": "No responses found for this user."}, status=status.HTTP_404_NOT_FOUND)

        category_scores = {}
        for response in responses:
            category = response.choice.question.category.code
            score = response.choice.score
            if category in category_scores:
                category_scores[category] += score
            else:
                category_scores[category] = score

        mbti_type = self.determine_mbti_type(category_scores)
        description, analysis, suggestions = self.get_mbti_description(mbti_type)

        result = MBTIResult.objects.create(
            user_id=user_id,
            mbti_type=mbti_type,
            scores=category_scores,
            description=description,
            analysis=analysis,
            suggestions=suggestions
        )

        serializer = MBTIResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def determine_mbti_type(self, category_scores):
        mbti_type = ""
        mbti_type += "E" if category_scores.get('E', 0) > category_scores.get('I', 0) else "I"
        mbti_type += "N" if category_scores.get('N', 0) > category_scores.get('S', 0) else "S"
        mbti_type += "T" if category_scores.get('T', 0) > category_scores.get('F', 0) else "F"
        mbti_type += "J" if category_scores.get('J', 0) > category_scores.get('P', 0) else "P"
        return mbti_type

    def get_mbti_description(self, mbti_type):
        descriptions = {
            "INTJ": "معماری‌ها افرادی هستند که...",
            "INTP": "منطق‌دان‌ها افرادی هستند که...",
            # سایر انواع MBTI
        }
        analysis = {
            "INTJ": "تحلیل برای INTJ...",
            "INTP": "تحلیل برای INTP...",
            # سایر انواع MBTI
        }
        suggestions = {
            "INTJ": "پیشنهادات برای INTJ...",
            "INTP": "پیشنهادات برای INTP...",
            # سایر انواع MBTI
        }
        return descriptions.get(mbti_type, ""), analysis.get(mbti_type, ""), suggestions.get(mbti_type, "")\



class TestCategoryCreateView(generics.CreateAPIView):
    queryset = TestCategory.objects.all()
    serializer_class = TestCategorySerializers
class TestCategoryListView(generics.ListAPIView):
    queryset = TestCategory.objects.all()
    serializer_class = TestCategorySerializers
    pagination_class = DefaultPagination

class TestCategoryUpdateView(generics.UpdateAPIView):
    queryset = TestCategory.objects.all()
    serializer_class = TestCategorySerializers
    lookup_field = 'slug'


class TestCategoryDetailView(generics.RetrieveAPIView):
    queryset = TestCategory.objects.all()
    serializer_class = TestCategorySerializers
    lookup_field = 'slug'
#TestResultUser
class TestResultUserCreateView(generics.CreateAPIView):
    queryset = TestResultUser.objects.all()
    serializer_class = TestResultUserCreateSerializers


class TestResultUserListView(generics.ListAPIView):
    queryset = TestResultUser.objects.all()
    serializer_class = TestResultUserSerializers
class TestResultByUserListView(generics.ListAPIView):
    queryset = TestResultUser.objects.all()
    serializer_class = TestResultUserSerializers
    def get_queryset(self):
        user_id = str(self.kwargs['user_id'])
        return TestResultUser.objects.filter(user_id=user_id)

class TestResultUserDetailView(generics.RetrieveAPIView):
    queryset = TestResultUser.objects.all()
    serializer_class = TestResultUserSerializers
#type test
class TypeTestCreateView(generics.CreateAPIView):
    queryset = TypeTest.objects.all()
    serializer_class = TypeTestMainSerializers
class TypeTestListView(generics.ListAPIView):
    queryset = TypeTest.objects.all()
    serializer_class = TypeTestSerializers
class TypeTestByTitleView(generics.ListAPIView):
    queryset = TypeTest.objects.all()
    serializer_class = TypeTestSerializers
    def get_queryset(self):
        title = self.kwargs['title']
        return TypeTest.objects.filter(title__exact=title)

class TypeTestByCatView(generics.ListAPIView):
    queryset = TypeTest.objects.all()
    serializer_class = TypeTestSerializers
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return TypeTest.objects.filter(category_id=category_id)

class TypeTestDetailView(generics.RetrieveAPIView):
    queryset = TypeTest.objects.all()
    serializer_class = TypeTestSerializers

class TypeTestUpdateView(generics.UpdateAPIView):
    queryset = TypeTest.objects.all()
    serializer_class = TypeTestMainSerializers

class FinalResultsCreateView(generics.CreateAPIView):
    queryset = FinalResult.objects.all()
    serializer_class = FinalResultsSerializers

class FinalResultsListView(generics.ListAPIView):
    queryset = FinalResult.objects.all()
    serializer_class = FinalResultsSerializers

class FinalResultsCatidView(generics.ListAPIView):
    queryset = FinalResult.objects.all()
    serializer_class = FinalResultsSerializers
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return FinalResult.objects.filter(category_id=category_id)



class FinalResultsDetailView(generics.RetrieveAPIView):
    queryset = FinalResult.objects.all()
    serializer_class = FinalResultsSerializers

class FinalResultsUpdateView(generics.UpdateAPIView):
    queryset = FinalResult.objects.all()
    serializer_class = FinalResultsSerializers

class FinalResultsHistoryView(generics.GenericAPIView):
    queryset = FinalResult.objects.all()
    serializer_class = FinalResultsSerializers
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        testresult_instance = serializer.save()

        user = testresult_instance.patient.user
        wallet = get_object_or_404(Wallet.objects.select_related('user'), user=user)

# def generate_unique_factor_number():
#     """Generate a unique factor number starting from 100."""
#     BASE_NUMBER = "T" + 1000 # Starting point
#     latest_number = MyFactors.objects.aggregate(Max('number_factors')).get('number_factors__max') or (BASE_NUMBER - 1)
#     return latest_number + 1

def generate_unique_factor_number(service_type):
    """Generate a unique factor number with a prefix based on service type."""
    prefix_mapping = {
        "test": "T",       # برای تست روانشناسی

    }

    prefix = prefix_mapping.get(service_type, "X")  # پیش‌فرض X اگر نوع ناشناخته بود

    # دریافت یا ایجاد یک رکورد برای شماره فاکتور این نوع
    factor_counter, created = FactorCounter.objects.get_or_create(service_type=service_type)

    # افزایش شماره فاکتور
    factor_counter.last_number = F('last_number') + 1
    factor_counter.save()

    # دریافت مقدار جدید از دیتابیس
    factor_counter.refresh_from_db()

    return f"{prefix}{factor_counter.last_number}"
class FinalTestPurchaseView(APIView):
    def post(self, request, test_category_id):
        user = request.user

        # دریافت قیمت از مدل TestCategory
        try:
            test_category = TestCategory.objects.get(id=test_category_id)
            test_price = test_category.price
        except TestCategory.DoesNotExist:
            return Response({"error": "دسته‌بندی تست یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

        # بررسی و کسر مبلغ از کیف پول
        try:
            wallet = Wallet.objects.get(user=user)
            wallet.deduct_from_wallet(test_price)
        except Wallet.DoesNotExist:
            return Response({"error": "کیف پول یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        unique_number = generate_unique_factor_number("test")

        # ایجاد رکورد در MyFactors
        factor = MyFactors.objects.create(
            user=user,
            title=f"فاکتور تست {test_category.title}",
            number_factors=unique_number,
            total_price=test_price,
            final_pay_price=test_price,
            discounted_price=0,
            payment_status="paid",
            trackId=str(uuid.uuid4()),
            is_paid=True
        )

        # ایجاد رکورد در PurchaseOrder
        purchase_order = PurchaseOrder.objects.create(
            user=user,
            service_type="تست روانشناسی",
            final_price=test_price
        )

        return Response({
            "message": "تست نهایی با موفقیت خریداری شد",
            "test_category": test_category.title,
            "factor_id": factor.id,
            "purchase_order_id": purchase_order.id,
            "wallet_balance": wallet.balance
        }, status=status.HTTP_201_CREATED)