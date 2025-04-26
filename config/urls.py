
from django.contrib import admin
from django.urls import path,include
from rest_framework import permissions
from config.permissions import ReadOnlySwaggerPermission
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static




schema_view = get_schema_view(
   openapi.Info(
      title="NAVA API",
      default_version='v1',
      description="nava_api description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="Eineheikh_12@yahoo.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[ReadOnlySwaggerPermission],
)


urlpatterns = ([
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('swagger/output.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    #app
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('vlog/', include('vlog.urls')),
    path('doctor/', include('doctors.urls')),
    path('q&a/', include('questions.urls')),
    path('documents_traetments/', include('treatment_doc.urls')),
    path('panel-admin/', include('Panel_Admin.urls')),
    path('finance/', include('finance.urls')),
    path('site_info/', include('site_info.urls')),
    path('filemanager/', include('filemanager.urls')),
    path('appointment/', include('appointment.urls')),
    path('tags/', include('tag.urls')),
    path('cart/', include('cart.urls')),
    path('podcast/', include('podcast.urls')),
    path('psychotest/', include('Psychological_test.urls')),
    path('landing_page/', include('landing_manager.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
               )
