from config.permissions import  IsAdminOrIsSupporter, IsAdminOrIsDoctorsOrIsSupporter, \
    IsDoctorOrAdminDoctor,  AdminAssistantOrIsAdminOrIsSupporter
from .serializers import (DoctorSerializer, CommentSerializer, DoctorRateSerializer,
                          ListCoprateserializer, DoctorCategorySerializer, DoctorCommentSerializer,
                          SpecializationSerilizer, DoctorSerializerList, DoctorPointSerializers, RateDoctorSerializer,
                          DoctorAnswerCreateSerializer, DoctorUpdateSerializer, CooprationsKindSerializers)
from doctors.models import Doctor, DoctorPoint, Rate_Doctor, DoctorCategory, DoctorComment, Specialization, Cooprations, \
    DoctorAnswer
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .paginations import DefaultPagination, CustomPagination, MainPagination
from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated ,IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.db.models import Avg

class DoctorList(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializerList
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['view_count','-rate_count']
    ordering = ['-rate_count']
    filterset_fields = [
        'gender','cooperation_kind','category','specialization',

    ]
    search_fields = [
        'full_name',

    ]
    pagination_class = DefaultPagination


class DoctorListByTagViews(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class =DoctorSerializerList
    def get_queryset(self):
        tags_id = self.kwargs['tags_id']
        return Doctor.objects.filter(tags=tags_id)
class DoctorCreate(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]
class DoctorDetail(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializerList
    lookup_field = 'slug'

    # permission_classes = [IsAdminOrIsSupporter]

class DoctorDelete(generics.DestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [AdminAssistantOrIsAdminOrIsSupporter]

class DoctorUpdate(generics.UpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrIsSupporter]
    lookup_field = 'slug'
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
class Doctorpatch(generics.UpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorUpdateSerializer
    permission_classes = [IsAdminOrIsSupporter]

class DoctorDetailId(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    # permission_classes = [IsAdminOrIsSupporter]
#doctor cooprate fields

class CommentList(generics.ListAPIView):
    queryset = DoctorComment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CustomPagination

    # queryset = DoctorComment.objects.filter()


class GenerateGoogleMeetLinkAPIView(APIView):
    def post(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            meet_link = doctor.generate_unique_google_meet_link()
            return Response({
                "doctor_id": doctor.id,
                "doctor_name": doctor.full_name,
                "unique_meet_link": meet_link
            }, status=status.HTTP_200_OK)

        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentCreate(generics.CreateAPIView):
    queryset = DoctorComment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentDetail(generics.RetrieveAPIView):
    queryset = DoctorComment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]

class CommentDelete(generics.DestroyAPIView):
    queryset = DoctorComment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]


class CommentUpdate(generics.UpdateAPIView):
    queryset = DoctorComment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]


    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
#######api-like comment
class LikeCommentView(APIView):
    def post(self, request, comment_id):
        try:
            comment = DoctorComment.objects.get(id=comment_id)
            comment.add_like()
            return Response({"message": "Like added", "like_count": comment.like_count}, status=status.HTTP_200_OK)
        except DoctorComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
# see comments based on the doctors
######api - dislike comment
class DislikeCommentView(APIView):
    def post(self, request, comment_id):
        try:
            comment = DoctorComment.objects.get(id=comment_id)
            comment.add_dislike()
            return Response({"message": "Dislike added", "dislike_count": comment.dislike_count}, status=status.HTTP_200_OK)
        except DoctorComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
class DoctorCommentsList(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = DefaultPagination


    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return DoctorComment.objects.filter(doctor_id=doctor_id,is_validated=True,is_active=True)
class DoctorCommentsUpdate(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return DoctorComment.objects.filter(doctor_id=doctor_id)
#########doctor Answer
class AnswerList(generics.ListAPIView):
    queryset = DoctorAnswer.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CustomPagination
    permission_classes = [IsDoctorOrAdminDoctor]
    # queryset = DoctorComment.objects.filter()

class AnswerCreate(generics.CreateAPIView):
    queryset = DoctorAnswer.objects.all()
    # serializer_class = CommentSerializer
    serializer_class = DoctorAnswerCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)

class AnswerDetail(generics.RetrieveAPIView):
    queryset = DoctorAnswer.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]

class AnswerDelete(generics.DestroyAPIView):
    queryset = DoctorAnswer.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]


class AnswerUpdate(generics.UpdateAPIView):
    queryset = DoctorAnswer.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrIsDoctorsOrIsSupporter]


    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
#######api-like comment
class LikeAnswerView(APIView):
    def post(self, request, comment_id):
        try:
            answer = DoctorAnswer.objects.get(id=comment_id)
            answer.add_like()
            return Response({"message": "Like added", "like_count": answer.like_count}, status=status.HTTP_200_OK)
        except DoctorAnswer.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
# see comments based on the doctors
######api - dislike comment
class DislikeAnswerView(APIView):
    def post(self, request, comment_id):
        try:
            answer = DoctorAnswer.objects.get(id=comment_id)
            answer.add_dislike()
            return Response({"message": "Dislike added", "dislike_count": answer.dislike_count}, status=status.HTTP_200_OK)
        except DoctorAnswer.DoesNotExist:
            return Response({"error": "answer not found"}, status=status.HTTP_404_NOT_FOUND)
class DoctorAllRateList(generics.ListAPIView):
    serializer_class =  DoctorRateSerializer
    queryset = Rate_Doctor.objects.all()


class DoctorRateCreate(generics.CreateAPIView):
    serializer_class =  DoctorRateSerializer
    queryset = Rate_Doctor.objects.all()

class DoctorRateDetail(generics.RetrieveAPIView):
    serializer_class =  DoctorRateSerializer
    queryset = Rate_Doctor.objects.all()


class DoctorRateList(generics.ListAPIView):
    serializer_class = DoctorRateSerializer
    pagination_class = MainPagination

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Rate_Doctor.objects.filter(doctor_id=doctor_id)


class ListCoprate(generics.ListAPIView):
    serializer_class = ListCoprateserializer
    queryset = Cooprations.objects.all()


class DoctorCategoryListViews(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    # queryset = DoctorCategory.objects.all()
    serializer_class =DoctorCategorySerializer
    search_fields = ['title']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    def get_queryset(self):
        queryset = DoctorCategory.objects.filter(is_active=True)
        return queryset

class DoctorCategorycreateViews(generics.CreateAPIView):
    permission_classes = [IsAdminOrIsSupporter]
    queryset = DoctorCategory.objects.all()
    serializer_class =DoctorCategorySerializer


class DoctorCategoryDetailViews(generics.RetrieveAPIView):
    permission_classes = [ IsAdminOrIsSupporter]
    queryset = DoctorCategory.objects.all()
    serializer_class =DoctorCategorySerializer
    lookup_field = 'slug'



class DoctorCategoryUpdateViews(generics.UpdateAPIView):
    permission_classes = [IsAdminOrIsSupporter]
    queryset = DoctorCategory.objects.all()
    serializer_class =DoctorCategorySerializer
    lookup_field = 'slug'
 


class DoctorCategoryDeleteViews(generics.DestroyAPIView):
    permission_classes = [IsAdminOrIsSupporter]
    queryset = DoctorCategory.objects.all()
    serializer_class =DoctorCategorySerializer
    lookup_field = 'slug'




class DoctorCommentModelViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = DoctorCommentSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['like_count']

    # queryset = ProductComment.objects.all()
    def get_queryset(self):
        user = self.request.user

        queryset = DoctorComment.objects.filter(is_active=True)

        if user.is_staff:  # Admin can see all comments
            queryset = DoctorComment.objects.all()
        elif user.is_authenticated:  # Registered user can see their own active comments
            queryset = queryset | DoctorComment.objects.filter(user=user, is_active=True)

        return queryset
##########################################################
#doctor spa
class Specializationlist(generics.ListAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerilizer



class SpecializationCreate(generics.CreateAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerilizer
    permission_classes = [IsAdminOrIsSupporter]
class SpecializationDelete(generics.DestroyAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerilizer
    permission_classes = [IsAdminOrIsSupporter]
class SpecializationDetail(generics.RetrieveAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerilizer
    permission_classes = [IsAdminOrIsSupporter]
class SpecializationUpdate(generics.UpdateAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerilizer
    permission_classes = [IsAdminOrIsSupporter]

#############################
############################
#doctor views class
class DoctorVisitCountView(APIView):
    permission_classes = [IsAuthenticated]
    # pagination_class = DefaultPagination

    def get(self, request,doctor_id):
        if not doctor_id:
            return Response({'error': 'doctor ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({'error': 'doctor not found'}, status=status.HTTP_404_NOT_FOUND)
        if doctor.view_count is None:
            doctor.view_count = 0
        doctor.view_count += 1
        doctor.save()

        return Response({'success': 'Visit number incremented successfully'}, status=status.HTTP_200_OK)


class DoctorPointList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = DoctorPoint.objects.all()
    serializer_class = DoctorPointSerializers

class DoctorPointCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = DoctorPoint.objects.all()
    serializer_class = DoctorPointSerializers

class DoctorPointUpdate(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = DoctorPoint.objects.all()
    serializer_class = DoctorPointSerializers


class DoctorPointDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = DoctorPoint.objects.all()
    serializer_class = DoctorPointSerializers

class DoctorPointDelete(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = DoctorPoint.objects.all()
    serializer_class = DoctorPointSerializers
##########
##############
################
#################doctor point new

# List all ratings or create a new rating

class RateDoctorListCreateView(generics.ListCreateAPIView):
    """
    List all ratings or create a new rating.
    """
    queryset = Rate_Doctor.objects.all()
    serializer_class = RateDoctorSerializer

class RateDoctorRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific rating.
    """
    queryset = Rate_Doctor.objects.all()
    serializer_class = RateDoctorSerializer
    permission_classes = [IsAdminOrIsSupporter]


class RateDoctorAveragesByDoctorView(APIView):
    """
    View to calculate the average of each rate field for a specific doctor
    and include the doctor's ID and name in the response.
    """
    def get(self, request, doctor_id, *args, **kwargs):
        # Try to get the doctor instance
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=404)

        # Filter ratings by the given doctor ID
        ratings = Rate_Doctor.objects.filter(doctor_id=doctor_id)

        if not ratings.exists():
            return Response({"doctor_id": doctor.id,
            "doctor_name": doctor.full_name,
            "averages": 4}, status=201)

        # Calculate averages
        averages = ratings.aggregate(
            avg_rate_1=Avg('rate_1'),
            avg_rate_2=Avg('rate_2'),
            avg_rate_3=Avg('rate_3'),
            avg_rate_4=Avg('rate_4')
        )

        # Add doctor details to the response
        response_data = {
            "doctor_id": doctor.id,
            "doctor_name": doctor.full_name,
            "averages": averages
        }

        return Response(response_data)
#############################
# class Cooprations
class CooprationsKindCreateView(generics.CreateAPIView):
    queryset = Cooprations.objects.all()
    serializer_class = CooprationsKindSerializers

# class CooprationsKindListView(generics.ListAPIView):
#     queryset = Cooprations.objects.all()
#     serializer_class = CooprationsKindSerializers

class CooprationsKindUpdateView(generics.UpdateAPIView):
    queryset = Cooprations.objects.all()
    serializer_class = CooprationsKindSerializers

class CooprationsKindDeleteView(generics.DestroyAPIView):
    queryset = Cooprations.objects.all()
    serializer_class = CooprationsKindSerializers