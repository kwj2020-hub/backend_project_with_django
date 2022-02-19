from django.contrib import admin
from .models import Post, Category, Tag

admin.site.register(Post)

class CategorytAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategorytAdmin)
admin.site.register(Tag, TagAdmin)