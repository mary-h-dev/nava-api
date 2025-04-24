from django.contrib import admin
from .models import CommentReporting, PaymentStatus, Coupon, CouponType, SmsMessage, SmsTemplates, CancellApointment, \
    ReportUser, TreatmentProcess ,SaleExpert ,LibraryBookDoctor
from .views import SmsBySenderListView



admin.site.register(Coupon)
admin.site.register(CouponType)
admin.site.register(CommentReporting)
admin.site.register(PaymentStatus)
admin.site.register(SmsMessage)
admin.site.register(SmsTemplates)
admin.site.register(CancellApointment)
admin.site.register(ReportUser)
admin.site.register(TreatmentProcess)
admin.site.register(SaleExpert)
admin.site.register(LibraryBookDoctor)
