from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated

from config import permissions
from site_info.models import AboutUs, Slider, Slide, Tabs, Tags, SectionType, Sections, Banner, Social_Media, SurveySite
from site_info.serializers import AboutUsSerializer, SlideSerializer, SliderSerializer, SocialSerializer, \
    SurveySiteSerializers


# Create your views here.

class AboutUsModelPostView(generics.CreateAPIView):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = AboutUsSerializer
    queryset = AboutUs.objects.all()
    # pagination_class = DefaultPagination

class AboutUsModelListView(generics.ListAPIView):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = AboutUsSerializer
    queryset = AboutUs.objects.all()
    # pagination_class = DefaultPagination

class AboutUsModelDeleteView(generics.DestroyAPIView):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = AboutUsSerializer
    queryset = AboutUs.objects.all()
    # pagination_class = DefaultPagination



class AboutUsModelUpdateView(generics.UpdateAPIView):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = AboutUsSerializer
    queryset = AboutUs.objects.all()
    # pagination_class = DefaultPagination

#slider crud

class SliderModelPostView(generics.CreateAPIView):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = SliderSerializer
    queryset = Slider.objects.all()
    # pagination_class = DefaultPagination


class SliderModelListView(generics.ListAPIView):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = SliderSerializer
    queryset = Slider.objects.all()
    # pagination_class = DefaultPagination

class SliderModelDeleteView(generics.DestroyAPIView):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = SliderSerializer
    queryset = Slider.objects.all()
    # pagination_class = DefaultPagination



class SliderModelUpdateView(generics.UpdateAPIView):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = SliderSerializer
    queryset = Slider.objects.all()
    # pagination_class = DefaultPagination


class SlideModelViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAdminOrReadOnly]  # get method for all
    serializer_class = SlideSerializer
    queryset = Slide.objects.all()
    # pagination_class = DefaultPagination

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if 'image_url' not in request.data:
    #         request.data['image_url'] = instance.image_url
    #     try:
    #         return super().update(request, *args, **kwargs)
    #     except FileNotFoundError as e:
    #         raise serializers.ValidationError("You must provide a valid image file.")
class SlideListView(generics.ListAPIView):
    serializer_class =  SlideSerializer
    queryset = Slide.objects.all()

class SlideCreateView(generics.CreateAPIView):
    serializer_class = SlideSerializer
    queryset = Slide.objects.all()


class SlideDetailView(generics.RetrieveAPIView):
    serializer_class = SlideSerializer
    queryset = Slide.objects.all()

class SlideUpdateView(generics.UpdateAPIView):
    serializer_class = SlideSerializer
    queryset = Slide.objects.all()

class SlideDeleteView(generics.DestroyAPIView):
    serializer_class = SlideSerializer
    queryset = Slide.objects.all()


#social crud
class SocialListView(generics.ListAPIView):
    serializer_class =  SocialSerializer
    queryset = Social_Media.objects.all()

class SocialCreateView(generics.CreateAPIView):
    serializer_class = SocialSerializer
    queryset = Social_Media.objects.all()


class SocialDetailView(generics.RetrieveAPIView):
    serializer_class = SocialSerializer
    queryset = Social_Media.objects.all()

class SocialUpdateView(generics.UpdateAPIView):
    serializer_class = SocialSerializer
    queryset = Social_Media.objects.all()

class SocialDeleteView(generics.DestroyAPIView):
    serializer_class = SocialSerializer
    queryset = Social_Media.objects.all()
#فرم نظر سنجی
class SurveySiteListView(generics.ListAPIView):
    serializer_class = SurveySiteSerializers
    queryset = SurveySite.objects.all()
    permission_classes = [IsAuthenticated]

class SurveySiteCreateView(generics.ListCreateAPIView):
    serializer_class = SurveySiteSerializers
    queryset = SurveySite.objects.all()
    permission_classes = [IsAuthenticated]

class SurveySiteDetailView(generics.RetrieveAPIView):
    serializer_class = SurveySiteSerializers
    queryset = SurveySite.objects.all()
    permission_classes = [IsAuthenticated]


class SurveySiteUpdateView(generics.UpdateAPIView):
    serializer_class = SurveySiteSerializers
    queryset = SurveySite.objects.all()
    permission_classes = [IsAuthenticated]


class SurveySiteDeleteView(generics.DestroyAPIView):
    serializer_class = SurveySiteSerializers
    queryset = SurveySite.objects.all()
    permission_classes = [IsAuthenticated]
