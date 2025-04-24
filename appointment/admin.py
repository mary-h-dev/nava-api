from django.contrib import admin

from appointment.models import (OrderVisit,PackageService,StaffMember,
                             DayOff,WorkingHours,AppointmentFinal,AppointmentReminder,
                              Patients,TimeStamped,AvailableTimeSlot,OrderPackage)


# Register your models here.

admin.site.register(OrderPackage)
admin.site.register(TimeStamped)
admin.site.register(Patients)
# admin.site.register(Wallet)
admin.site.register(OrderVisit)
admin.site.register(PackageService)
admin.site.register(StaffMember)
admin.site.register(DayOff)
admin.site.register(WorkingHours)
admin.site.register(AppointmentFinal)
admin.site.register(AppointmentReminder)
admin.site.register(AvailableTimeSlot)