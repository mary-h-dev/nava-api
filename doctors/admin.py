from django.contrib import admin
# from . import models
from .models import Rate_Doctor, Doctor, Cooprations, DoctorCategory, Specialization, DoctorPoint, Rate_Doctor, \
    DoctorComment, DoctorAnswer

admin.site.register(Doctor)
admin.site.register(Cooprations)
admin.site.register(DoctorCategory)
admin.site.register(Specialization)
admin.site.register(DoctorPoint)
admin.site.register(Rate_Doctor)
admin.site.register(DoctorComment)
admin.site.register(DoctorAnswer)
