from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Post, Category, Tag, Comment

admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(Comment)

class CategorytAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategorytAdmin)
admin.site.register(Tag, TagAdmin)