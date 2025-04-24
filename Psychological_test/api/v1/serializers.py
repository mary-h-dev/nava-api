from rest_framework import serializers

from ...models import Question, Choice, UserResponse, MBTIResult, Category, Test, TestCategory, TestResultUser, \
    TypeTest, FinalResult


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        ref_name = 'QuestionSerializerV1'  # این خط را اضافه کنید


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = '__all__'


class MBTIResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MBTIResult
        fields = '__all__'

class TestCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = TestCategory
        fields = '__all__'

class TestResultUserCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = TestResultUser
        fields = '__all__'

class TestResultUserSerializers(serializers.ModelSerializer):
    category = TestCategorySerializers()
    class Meta:
        model = TestResultUser
        fields = '__all__'
class TypeTestSerializers(serializers.ModelSerializer):
    category = TestCategorySerializers()
    class Meta:
        model = TypeTest
        fields = '__all__'
#type test for create views its vithout category detail only id
class TypeTestMainSerializers(serializers.ModelSerializer):
    class Meta:
        model = TypeTest
        fields = '__all__'
class FinalResultsSerializers(serializers.ModelSerializer):
    class Meta:
        model = FinalResult
        fields = '__all__'