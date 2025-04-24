from django.contrib import admin
from .models import Vlog,Vlog_Category,CommentsVlog
# Register your models here.



admin.site.register(Vlog)
admin.site.register(Vlog_Category)
admin.site.register(CommentsVlog)