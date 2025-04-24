from blog.models import Blog, BlogCategory, BlogImage, CommentsBlog, AuthorList
from rest_framework import serializers, request
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from accounts.models import User
from doctors.api.v1.serializers import DoctorSerializer
from tag.serializers import TagSerializer
class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = '__all__'
        read_only_fields = ('web_image',)

    def create(self, validated_data):
        # Get the uploaded image from the validated data
        image_file = validated_data.get('image_url')

        # Convert the image to WebP format
        if image_file:
            image = Image.open(image_file)
            webp_image = BytesIO()
            image.save(webp_image, format="webp")
            webp_image.seek(0)

            # Create a new InMemoryUploadedFile object with the WebP image data
            webp_image_file = InMemoryUploadedFile(
                webp_image, None, f"{image_file.name.split('.')[0]}.webp", 'image/webp',
                webp_image.tell(), None
            )

            # Save the webp_image_file to the web_image field
            validated_data['web_image'] = webp_image_file

        # Call the parent create method to save the model instance
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Get the uploaded image from the validated data
        image_file = validated_data.get('image_url')

        # Convert the image to WebP format
        if image_file:
            image = Image.open(image_file)
            webp_image = BytesIO()
            image.save(webp_image, format="webp")
            webp_image.seek(0)

            # Create a new InMemoryUploadedFile object with the WebP image data
            webp_image_file = InMemoryUploadedFile(
                webp_image, None, f"{image_file.name.split('.')[0]}.webp", 'image/webp',
                webp_image.tell(), None
            )

            # Update the validated data with the webp_image_file
            validated_data['web_image'] = webp_image_file

        # Call the parent update method to save the updated model instance
        return super().update(instance, validated_data)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and not request.user.is_staff:
            fields.pop('is_active', None)
            fields.pop('created_at', None)
            fields.pop('updated_at', None)
        return fields


class AuthorBlogSerializers(serializers.ModelSerializer):
    class Meta:
        model = AuthorList
        fields = '__all__'
class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'title', 'parent', 'image', 'web_image', 'slug', 'is_active', 'is_validated']
        read_only_fields = ['slug', 'created_at', 'updated_at']


    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and not request.user.is_staff:
            fields.pop('is_active', None)
            fields.pop('is_validated', None)
            # fields.pop('slug', None)
            # fields.pop('user', None)
            fields.pop('created_at', None)
            fields.pop('updated_at', None)
            # fields.pop('id', None)
        return fields

    def create(self, validated_data):
        # Get the uploaded image from the validated data
        image_file = validated_data.get('image')

        # Convert the image to WebP format
        if image_file:
            image = Image.open(image_file)
            webp_image = BytesIO()
            image.save(webp_image, format="webp")
            webp_image.seek(0)

            # Create a new InMemoryUploadedFile object with the WebP image data
            webp_image_file = InMemoryUploadedFile(
                webp_image, None, f"{image_file.name.split('.')[0]}.webp", 'image/webp',
                webp_image.tell(), None
            )

            # Save the webp_image_file to the web_image field
            validated_data['web_image'] = webp_image_file

        # Call the parent create method to save the model instance
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Get the uploaded image from the validated data
        image_file = validated_data.get('image')

        # Convert the image to WebP format
        if image_file:
            image = Image.open(image_file)
            webp_image = BytesIO()
            image.save(webp_image, format="webp")
            webp_image.seek(0)

            # Create a new InMemoryUploadedFile object with the WebP image data
            webp_image_file = InMemoryUploadedFile(
                webp_image, None, f"{image_file.name.split('.')[0]}.webp", 'image/webp',
                webp_image.tell(), None
            )

            # Update the validated data with the webp_image_file
            validated_data['web_image'] = webp_image_file

        # Call the parent update method to save the updated model instance
        return super().update(instance, validated_data)
#این فقط برای ایجاد بلگ است
class PostBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'
    def validate_title(self, value):
        """
        بررسی عدم وجود عنوان تکراری
        """
        if Blog.objects.filter(title=value).exists():
            raise serializers.ValidationError("مقاله‌ای با این عنوان از قبل وجود دارد. لطفاً عنوان دیگری انتخاب کنید.")
        return value

    def validate_slug(self, value):
        """
        بررسی عدم وجود slug تکراری
        """
        if Blog.objects.filter(slug=value).exists():
            raise serializers.ValidationError("عنوان در URL (slug) تکراری است. لطفاً مقدار دیگری وارد کنید.")
        return value

class BlogSerializer(serializers.ModelSerializer):
    images = BlogImageSerializer(many=True, read_only=True, source='blog_image')
    doctorname_full_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    doctorname = DoctorSerializer(read_only=True)
    category = BlogCategorySerializer(read_only=True)
    tags = TagSerializer(many=True,read_only=True)
    # author_name = serializers.SerializerMethodField()
    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ('view_count','slug')
        # ordering = ('slug',)
    def get_doctorname_full_name(self, obj):
        if obj.doctorname:

            return obj.doctorname.full_name
    def get_category_name(self,obj):
        if obj.category:
            return obj.category.title
        return None
    def get_author_name(self,obj):
        return obj.doctorname.full_name



class BlogCommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = CommentsBlog
        fields = '__all__'


class DoctorBlogSerializer(serializers.ModelSerializer):
    blog_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'blog_count']

class BlogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'