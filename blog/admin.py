from django.contrib import admin
from .models import Post, Category

admin.site.register(Post)

class CategorytAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategorytAdmin)