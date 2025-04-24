from django.contrib import admin

from .models import Blog ,BlogCategory , CommentsBlog ,LikeBlogPost ,AuthorList

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ("title",'parent',"slug",'is_active')
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(BlogCategory, PostAdmin)

class BlogCatAdmin(admin.ModelAdmin):
    list_display = ("title", "slug",'is_active','category')
    prepopulated_fields = {"slug": ("title",)}
admin.site.register(Blog, BlogCatAdmin)
# admin.site.register(BlogCategory)
admin.site.register(CommentsBlog)
admin.site.register(LikeBlogPost)
admin.site.register(AuthorList)