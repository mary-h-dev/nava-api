from django.contrib import admin
from accounts.models import User, Profile, Notification, Token
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class CustomUserAdmin(UserAdmin):
    model=User
    list_display = ('Phone_Number','is_superuser','is_active','is_verified','is_doctoradmin','is_admin_assistant','confirm_otp','is_doctor','is_abroad','is_expert','is_seo','email')
    list_filter = ('Phone_Number','is_superuser','is_active','is_doctor','is_doctoradmin','is_admin_assistant','is_abroad','is_expert','is_seo','email')
    searching_fields = ('Phone_Number',)
    ordering = ('Phone_Number',)

    fieldsets =(
        ('Authentication',{
        'fields':(
    'Phone_Number','password'
    )}),
        ('permissions',{
        'fields':(
    'is_staff','is_active','is_superuser','is_verified','is_doctor','is_supporter','is_doctoradmin','is_admin_assistant','is_abroad','is_expert','is_seo'
    )}),
        ('group permissions',{
        'fields':(
    'groups','user_permissions'
    )}),
        ('importnt date',{
        'fields':(
    'last_login','confirm_otp'
    )}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "Phone_Number", "password1", "password2", "is_staff",
                "is_active", "is_superuser","is_doctor","is_supporter",'is_doctoradmin','is_admin_assistant','is_abroad','is_expert','email','is_seo'
            )}
         ),
    )



admin.site.register(User,CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(Notification)
admin.site.register(Token)