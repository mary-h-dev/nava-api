from django.contrib import admin
from podcast.models import Podcast, PodcastCategory
# Register your models here.
admin.site.register(Podcast)
admin.site.register(PodcastCategory)
