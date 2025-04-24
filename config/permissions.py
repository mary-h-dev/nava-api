from rest_framework.permissions import BasePermission, SAFE_METHODS


# ------------------------------
# پایه نقش‌ها (Base Role Permission)
# ------------------------------
class BaseRolePermission(BasePermission):
    allowed_roles = []  # نقش‌های مجاز در هر کلاس مشخص می‌شه

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return any(getattr(request.user, role, False) for role in self.allowed_roles)


# ------------------------------
# دسترسی فقط خواندنی (برای Swagger یا Viewهای عمومی)
# ------------------------------
class ReadOnlySwaggerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_superuser




class IsAdminOrReadOnly(BaseRolePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# ------------------------------
# نقش‌محور ساده
# ------------------------------
class IsDoctorOrAdmin(BaseRolePermission):
    allowed_roles = ["is_doctor", "is_staff", "is_superuser"]

class IsDoctorOrAdminDoctor(BaseRolePermission):
    allowed_roles = ["is_doctor", "is_doctoradmin"]

class IsAdminOrIsDoctorsOrIsSupporter(BaseRolePermission):
    allowed_roles = ["is_superuser", "is_staff", "is_doctor", "is_supporter"]

class IsAdminOrIsSupporter(BaseRolePermission):
    allowed_roles = ["is_superuser", "is_staff", "is_supporter"]

class AdminAssistantOrIsAdminOrIsSupporter(BaseRolePermission):
    allowed_roles = ["is_superuser", "is_staff", "is_admin_assistant", "is_supporter"]

class IsAdminOrIsDoctorsOrIsSupporterOrDcAdmin(BaseRolePermission):
    allowed_roles = ["is_superuser", "is_staff", "is_admin_assistant", "is_supporter", "is_doctoradmin"]

class AdminAssistantOrIsAdmin(BaseRolePermission):
    allowed_roles = ["is_superuser", "is_staff", "is_admin_assistant"]

class IsSaleExpertOrAdmin0(BaseRolePermission):
    allowed_roles = ["is_superuser", "is_staff", "is_expert"]


# ------------------------------
# ترکیبی و خاص
# ------------------------------
class IsSaleExpertOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_expert)



class IsAdminOrNp(BasePermission):
    """
    فقط ادمین‌ها اجازه ایجاد، ویرایش یا حذف دارند.
    همه می‌تونن لیست آیتم‌ها رو ببینن.
    """
    def has_permission(self, request, view):
        if view.action == 'list':
            return True
        return request.user and request.user.is_staff and request.user.is_superuser
