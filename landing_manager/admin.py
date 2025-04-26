from django.contrib import admin
from landing_manager.models import LandingPage, SubmissionLandingPage ,Campaign
from django.contrib import admin

from .models import AllowedIP
# Register your models here.
admin.site.register(Campaign)
admin.site.register(LandingPage)
admin.site.register(SubmissionLandingPage)


# myapp/admin.py



@admin.register(AllowedIP)
class AllowedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'description')
