from django.urls import path, include
from django.urls import path
from rest_framework.routers import DefaultRouter

from appointment.api.v1.serializers import AppointmentFinalDateDcSerializer
from appointment.api.v1.views import (StaffMembersByDoctor, AppointmentList,
                                      AppointmentCreateView, patientsUpdate,
                                      AppointmentReminderViewSet, PackageServiceCreate, PackageServiceList,
                                      PatientsList,
                                      PackageServiceDelete, PackageServiceUpdate,
                                      PatientsByUserList,
                                      StaffMemberList, TimeStampedList, patientsCreate, ActiveTimeSlotsList,
                                      ActiveTimeSlotsByDoctorView, OrderPackageCreate, OrderPackageList,
                                      OrderPackageDelete, OrderPackageUpdate, AppointmentFinalByUer,
                                      PackageServiceByIdList, TimeSlotList, TimeSlotCreate, TimeSlotUpdate,
                                      TimeSlotDelete, TimeSlotByDoctorList, PackageServiceDetail, TimeSlotDetail,
                                      TimeStampedCreate, TimeStampedUpdate, TimeStampedDelete, TimeStampedDetail,
                                      AppointmentFinalCreateOptimize,
                                      TimeStampedListByDoctor, AppointmentFinalByTimeSlot,
                                      AppointmentListViewSet, patientsDetail, AppointmentFinalByDoctorCreateOptimize,
                                      AppointmentListByDcViewSet, StaffMembersByDoctorLast,
                                      AppointmentFinalByTimeSlotDc, AppointmentFinalByPatientProfile,
                                      StaffMembersCreate, StaffMembersByDoctorTimeLast, StaffMembersUpdate,
                                      StaffMembersDetail, TimeStampedLisDoctorId, StaffMembersByDoctorDate,
                                      StaffMembersDelete, AppointmentSalesExpertViewSet, AppointmentListByCupoun,
                                      PackageServiceSeoList)

router = DefaultRouter()
router.register(r'appointment-reminders', AppointmentReminderViewSet, basename='appointment-reminder')

urlpatterns = [
    path('', include(router.urls)),
#############################
    #package
    path('package/create/', PackageServiceCreate.as_view(), name='package-create'),
    path('package/list/', PackageServiceList.as_view(), name='package-list'),
    path('package/list-seo/', PackageServiceSeoList.as_view(), name='package-list-seo'),
    path('package/update/<int:pk>', PackageServiceUpdate.as_view(), name='package-update'),
    path('package/detail/<int:pk>', PackageServiceDetail.as_view(), name='package-update'),
    path('package/delete/<int:pk>', PackageServiceDelete.as_view(), name='package-delete'),
    path('package/listbyid/<int:id>', PackageServiceByIdList.as_view(), name='package-list-id'),
    #appointment final(doctor visit)
    path('final/createnewoptimize/', AppointmentFinalCreateOptimize.as_view(), name='appointmentfinal-create'),#main
    path('final/createappointmentbydc/', AppointmentFinalByDoctorCreateOptimize.as_view(), name='appointmentfinal-create-bydc'),#main
    path('final/createappointmentbyexpert/', AppointmentSalesExpertViewSet.as_view(), name='appointmentfinal-create-byexpert'),#main
    path('final/list/appointmentbycuopoun/<int:usr_copoun>/<str:date>/', AppointmentListByCupoun.as_view(), name='appointmentfinal-create-byexpert'),#main
    path('final/listdc/<int:doctor_id>/', AppointmentListByDcViewSet.as_view(), name='appointmentfinal-listdc'),#main
    path('final/list/', AppointmentListViewSet.as_view(), name='appointmentfinal-list'),#main
    path('final/byuser/<int:patient_id>/', AppointmentFinalByUer.as_view(), name='appointmentfinal-list'),#main
    path('final/byuserprofile/<int:patient_id>/', AppointmentFinalByPatientProfile.as_view(), name='appointmentfinal-listprofile'),#main
    path('final/byslot/<int:timeslot_id>/', AppointmentFinalByTimeSlot.as_view(), name='appointmentfinal-timeslot'),#main
    path('final/byslotdoctor/<int:doctor_id>/<str:date>/', AppointmentFinalByTimeSlotDc.as_view(), name='appointmentfinal-timeslotdc'),#main
    #package-order
    path('packageorder/create/', OrderPackageCreate.as_view(), name='packageorder-create'),
    path('packageorder/list/', OrderPackageList.as_view(), name='packageorder-list'),
    path('packageorder/delete/<int:pk>', OrderPackageDelete.as_view(), name='packageorder-delete'),
    path('packageorder/update/<int:pk>', OrderPackageUpdate.as_view(), name='packageorder-update'),
    #list taffmember
    path('staffmember/list/', StaffMemberList.as_view(), name='staffmember'),
    path('staffmember/list/<int:doctor_id>/', StaffMembersByDoctor.as_view(), name='staffmember_by_doctor'),
    path('staffmember/lastdoctor/<int:doctor_id>/', StaffMembersByDoctorLast.as_view(), name='staffmember_by_lastdoctor'),
    path('staffmember/lastdoctor/<int:doctor_id>/date/', StaffMembersByDoctorDate.as_view(), name='staffmember_by_datedoctor'),#check kon
    path('staff_members/<int:doctor_id>/time_slots/', StaffMembersByDoctorTimeLast.as_view(), name='staff-members-by-date'),#query params by ? date
    path('staffmember/create/',StaffMembersCreate.as_view(), name='staffmember-create'),
    path('staffmember/update/<int:pk>/',StaffMembersUpdate.as_view(), name='staffmember-update'),
    path('staffmember/detail/<int:pk>/',StaffMembersDetail.as_view(), name='staffmember-detail'),
    path('staffmember/delete/<int:pk>/',StaffMembersDelete.as_view(), name='staffmember-delete'),
    path('time-slots/active/', ActiveTimeSlotsList.as_view(), name='active-time-slots'),
    path('time-slots/active/<int:doctor_id>/<str:date>/', ActiveTimeSlotsByDoctorView.as_view(),name='active-time-slots-by-doctor'),
    path('TimeStamped/list', TimeStampedList.as_view(), name='time-stamped-list'),
    path('TimeStamped/list/<int:doctor_id>/<str:date>/', TimeStampedListByDoctor.as_view(), name='time-stamped-list'),
    path('TimeStamped/alllistbydc/<int:doctor_id>/', TimeStampedLisDoctorId.as_view(), name='time-stamped-list'),
    path('TimeStamped/create', TimeStampedCreate.as_view(), name='time-stamped-create'),
    path('TimeStamped/update/<int:pk>', TimeStampedUpdate.as_view(), name='time-stamped-update'),
    path('TimeStamped/delete/<int:pk>', TimeStampedDelete.as_view(), name='time-stamped-delete'),
    path('TimeStamped/detail/<int:pk>', TimeStampedDetail.as_view(), name='time-stamped-detail'),
    #patient
    path('patients/create/',patientsCreate.as_view(), name='patients-create'),
    path('patients/list/',PatientsList.as_view(), name='patients-list'),
    path('patients/list/<int:user_id>/',PatientsByUserList.as_view(), name='patients-list'),
    path('patients/update/<int:pk>', patientsUpdate.as_view(), name='patients-update'),
    path('patients/detail/<int:pk>', patientsDetail.as_view(), name='patients-detail'),
    #availble time slot
    path('timeslot/create/', TimeSlotCreate.as_view(), name='TimeSlot-create'),
    path('timeslot/list/', TimeSlotList.as_view(), name='TimeSlot-list'),
    path('timeslot/list/<int:doctor_id>/', TimeSlotByDoctorList.as_view(), name='TimeSlot-list-bydoctor'),
    path('timeslot/update/<int:pk>/', TimeSlotUpdate.as_view(), name='TimeSlot-update'),
    path('timeslot/delete/<int:pk>/', TimeSlotDelete.as_view(), name='TimeSlot-delete'),
    path('timeslot/detail/<int:pk>/', TimeSlotDetail.as_view(), name='TimeSlot-detail'),



]

