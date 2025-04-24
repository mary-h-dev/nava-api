from rest_framework import serializers
from doctors.models import Doctor, DoctorPoint, Rate_Doctor, DoctorCategory, DoctorComment, Cooprations, Specialization, \
    DoctorAnswer


class cooprationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooprations
        fields = '__all__'


class DoctorAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAnswer
        fields = '__all__'



class CommentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    parent_comment = serializers.SerializerMethodField()  # New field for parent comment
    Answer = DoctorAnswerListSerializer(read_only=True)
    class Meta:
        model = DoctorComment
        fields = '__all__'
        # fields = '__all__'

    def get_doctor_name(self, obj):
        return obj.doctor.full_name
    def get_user_name(self, obj):
        # Retrieve the user's phone number
        return obj.user.Phone_Number if obj.user else None
    def get_parent_comment(self, obj):
        # Check if the parent comment exists
        if obj.parent_comment:
            return {
                'id': obj.parent_comment.id,
                'text': obj.parent_comment.text,
                'doctor_name': obj.parent_comment.doctor.full_name if obj.parent_comment.doctor else None,
                'user_name': obj.parent_comment.user.Phone_Number if obj.parent_comment.user else None,
                'created_at': obj.parent_comment.created_at,
                'like_count': obj.parent_comment.like_count,
                'dislike_count': obj.parent_comment.dislike_count,
            }
        return None  # Return None if there is no parent comment




class DoctorCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = DoctorCategory
        fields = '__all__'
    def get_children(self, obj):
        # Ensure that obj.children.all() is a queryset, which is iterable
        return DoctorCategorySerializer(obj.children.all(),many=True).data

class DoctorSerializerList(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    # categories = DoctorCategorySerializer(many=True, read_only=True)
    categories = serializers.SerializerMethodField()
    cooperation_kind_name = cooprationSerializer(many=True, read_only=True, source='cooperation_kind.all')
    specialization_name = serializers.SerializerMethodField()
    # cooperation_kind = serializers.SerializerMethodField()
    tags_name = serializers.SerializerMethodField()
    class Meta:
        model = Doctor
        fields = '__all__'
    def get_specialization_name(self, obj):
        # Check if specialization is a ManyToManyField
        try:
            return [specialization.title for specialization in obj.specialization.all()]
        except AttributeError:
            # Handle if specialization is a ForeignKey instead of ManyToManyField
            return obj.specialization.title if obj.specialization else None

    def get_tags_name(self, obj):
        # Return a list of dictionaries with id and title for each tag
        return [{'id': tag.id, 'name': tag.name} for tag in obj.tags.all()]
    def get_categories(self, obj):
        return obj.category.title
    def get_cooperation_kind_name(self, obj):
        # Create a list of titles from the related cooperation_kind objects
        return [cooperation.title for cooperation in obj.cooperation_kind.all()]

    def create(self, validated_data):
        doctor = Doctor.objects.create(**validated_data)
        return doctor
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class DoctorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    categories = serializers.SerializerMethodField()
    cooperation_kind = cooprationSerializer(many=True, read_only=True)
    tags_name = serializers.SerializerMethodField()
    special_name = serializers.SerializerMethodField()
    # meet_link = serializers.URLField(read_only=True)
    class Meta:
        model = Doctor
        fields = '__all__'

    def get_special_name(self,obj):
        return obj.specialization.title
    def get_tags_name(self, obj):
        # Assuming `tags` is a ManyToManyField on Doctor pointing to Tag
        return [tag.name for tag in obj.tags.all()]
    def get_categories(self, obj):
        return obj.category.title
   

class DoctorRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate_Doctor
        fields = '__all__'

class ListCoprateserializer(serializers.ModelSerializer):
    class Meta:
        model = Cooprations
        fields = '__all__'
class DoctorAnswerCreateSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField(write_only=True)  # دریافت ID کامنت از فرانت‌اند

    class Meta:
        model = DoctorAnswer
        fields = ['id', 'doctor', 'text', 'comment_id']

    def create(self, validated_data):
        """
        ذخیره پاسخ و اتصال آن به کامنت.
        """
        # گرفتن اطلاعات معتبر
        comment_id = validated_data.pop('comment_id')
        doctor = validated_data['doctor']
        text = validated_data['text']

        # گرفتن کامنت مربوطه
        comment = DoctorComment.objects.get(id=comment_id)

        # ایجاد پاسخ و ذخیره آن
        doctor_answer = DoctorAnswer.objects.create(
            comments=comment,
            doctor=doctor,
            text=text
        )

        # حالا که doctor_answer ذخیره شده، می‌توانیم آن را به کامنت متصل کنیم
        comment.Answer = doctor_answer
        comment.save(update_fields=['Answer'])

        return doctor_answer



class DoctorCommentSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer(many=True, read_only=True, source='user.profile')
    user = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    class Meta:
        model = DoctorComment
        fields = '__all__'

        # read_only_fields = ('user', 'web_image',)
    def get_user(self, obj):
        return obj.user.Phone_Number
    def get_doctor(self, obj):
        return obj.doctor.full_name
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            # Check the request method
            if request.method == 'GET':
                # Replace ProductComment ID with name in GET method
                #     representation['product'] = instance.product.title
                #     representation['user'] = instance.user.phone_number
                if instance.parent_comment:
                    representation['parent_comment'] = instance.parent_comment.text
                    representation['parent_comment'] = {
                        'id': instance.parent_comment.id,
                        'text': instance.parent_comment.text,
                        'user': instance.parent_comment.user.Phone_Number,
                        # 'username': instance.parent_comment.user.profile
                    }
            else:
                # Use ProductComment ID in POST and UPDATE methods
                #     representation['product'] = instance.product.id
                #     representation['user'] = instance.user.id
                if instance.parent_comment:
                    representation['parent_comment'] = instance.parent_comment.id

        return representation

    def create(self, validated_data):
        # Set the "user" field to the currently authenticated user
        validated_data['user'] = self.context['request'].user

        parent_comment = validated_data.get('parent_comment')
        if parent_comment:
            parent_doctor = parent_comment.product
            # Check if the parent comment is associated with a product
            doctorcomment = validated_data['doctorcomment']
            if not parent_comment == doctorcomment:
                raise serializers.ValidationError("Parent comment is not associated with a product.")


        # Call the parent create method to save the model instance
        return super().create(validated_data)


    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and not request.user.is_staff:
            fields.pop('is_active', None)
            fields.pop('is_validated', None)
            fields.pop('created_at', None)
            fields.pop('updated_at', None)
        return fields

class SpecializationSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'

class DoctorPointSerializers(serializers.ModelSerializer):

    class Meta:
        model = DoctorPoint
        fields = '__all__'


class RateDoctorSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Rate_Doctor
        fields = [
            'id','name','doctor', 'rate_1', 'rate_2', 'rate_3', 'rate_4',
            'text', 'created_at', 'average_rating'
        ]
        read_only_fields = ['id', 'created_at', 'average_rating']
class CooprationsKindSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cooprations
        fields = '__all__'