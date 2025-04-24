from django.contrib import admin
from .models import WorkShop ,WorkshopCategory ,RegisterWorkshop
# Register your models here.
@admin.register(WorkshopCategory)
class WorkshopCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    search_fields = ['title', 'slug']
    list_filter = ['is_active', 'is_validated']

@admin.register(WorkShop)
class WorkShopAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'doctor', 'date', 'price', 'final_price']
    search_fields = ['title', 'locations']
    list_filter = ['category', 'doctor', 'date']

admin.site.register(RegisterWorkshop)