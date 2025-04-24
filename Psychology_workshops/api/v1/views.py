from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import IntegrityError

from Psychology_workshops.api.v1.paginations import DefaultPagination
from Psychology_workshops.models import WorkShop
from config.permissions import IsDoctorOrAdmin
from Psychology_workshops.api.v1.serializers import WorkShopSerializers, WorkshopCategorySerializers, \
    RegisterWorkshopSerializers
from Psychology_workshops.models import WorkShop ,WorkshopCategory ,RegisterWorkshop
from rest_framework import status

###category
class WorkshopCategoryCreateAPIView(generics.CreateAPIView):
    queryset = WorkshopCategory.objects.all()
    serializer_class = WorkshopCategorySerializers
    permission_classes = [IsAuthenticated]
class WorkshopCategoryListAPIView(generics.ListAPIView):
    queryset = WorkshopCategory.objects.all()
    serializer_class = WorkshopCategorySerializers
    pagination_class = DefaultPagination
class WorkshopCategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = WorkshopCategory.objects.all()
    serializer_class = WorkshopCategorySerializers
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

class WorkshopCategoryUpdateAPIView(generics.UpdateAPIView):
    queryset = WorkshopCategory.objects.all()
    serializer_class = WorkshopCategorySerializers
    permission_classes = [IsAuthenticated]

class WorkshopCategoryDeleteAPIView(generics.DestroyAPIView):
    queryset = WorkshopCategory.objects.all()
    serializer_class = WorkshopCategorySerializers
    permission_classes = [IsAuthenticated]

#################workshop
class WorkShopCreateAPIView(generics.CreateAPIView):
    queryset = WorkShop.objects.all()
    serializer_class = WorkShopSerializers
    permission_classes = [IsAuthenticated]
class WorkShopListAPIView(generics.ListAPIView):
    queryset = WorkShop.objects.all()
    serializer_class = WorkShopSerializers
    pagination_class = DefaultPagination
class WorkShopDetailAPIView(generics.RetrieveAPIView):
    queryset = WorkShop.objects.all()
    serializer_class = WorkShopSerializers
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'



class WorkShopUpdateAPIView(generics.UpdateAPIView):
    queryset = WorkShop.objects.all()
    serializer_class = WorkShopSerializers
    permission_classes = [IsAuthenticated]

class WorkShopDeleteAPIView(generics.DestroyAPIView):
    queryset = WorkShop.objects.all()
    serializer_class = WorkShopSerializers
    permission_classes = [IsAuthenticated]

######################regisster workshop
class RegisterWorkShopCreateAPIView(generics.CreateAPIView):
    queryset = RegisterWorkshop.objects.all()
    serializer_class = RegisterWorkshopSerializers

class RegisterWorkShopListAPIView(generics.ListAPIView):
    queryset = RegisterWorkshop.objects.all()
    serializer_class = RegisterWorkshopSerializers
    pagination_class = DefaultPagination
class RegisterWorkShopDetailAPIView(generics.RetrieveAPIView):
    queryset = RegisterWorkshop.objects.all()
    serializer_class = RegisterWorkshopSerializers

class RegisterWorkShopUpdateAPIView(generics.UpdateAPIView):
    queryset = RegisterWorkshop.objects.all()
    serializer_class = RegisterWorkshopSerializers
    permission_classes = [IsAuthenticated]
class RegisterWorkShopDeleteAPIView(generics.DestroyAPIView):
    queryset = RegisterWorkshop.objects.all()
    serializer_class = RegisterWorkshopSerializers
    permission_classes = [IsDoctorOrAdmin]

###################like and view count
class WorkshopLikeCountView(APIView):
    def get(self, request, workshop_id):
        if not workshop_id:
            return Response({'error': 'workshop ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            workshop = WorkShop.objects.get(id=workshop_id)
        except WorkShop.DoesNotExist:
            return Response({'error': 'Podcast not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Check if the user has already liked the Podcast
            like = WorkShop.objects.get(workshop=workshop, user=request.user)
            return Response({'error': 'You have already liked this podcast'}, status=status.HTTP_400_BAD_REQUEST)
        except WorkShop.DoesNotExist:
            # Create a new like object
            like = WorkShop(workshop=workshop, user=request.user)
            try:
                like.save()
            except IntegrityError:
                # Handle the case where the like was created by another request in the meantime
                return Response({'error': 'You have already liked this podcast'}, status=status.HTTP_400_BAD_REQUEST)

            # Increment the like count
            workshop.like_count += 1
            workshop.save()

            return Response({'success': 'LIKE number incremented successfully'}, status=status.HTTP_200_OK)

class PodcastVisitCountView(APIView):
    permission_classes = [IsAuthenticated]
    # pagination_class = DefaultPagination

    def get(self, request,workshop_id):
        if not workshop_id:
            return Response({'error': 'Podcast ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            workshop = WorkShop.objects.get(id=workshop_id)
        except WorkShop.DoesNotExist:
            return Response({'error': 'Podcast not found'}, status=status.HTTP_404_NOT_FOUND)
        if workshop.view_count is None:
            workshop.view_count = 0
        workshop.view_count += 1
        workshop.save()

        return Response({'success': 'Visit number incremented successfully'}, status=status.HTTP_200_OK)