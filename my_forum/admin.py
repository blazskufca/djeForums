from django.contrib import admin
from . import models
from django.contrib.admin.models import LogEntry
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',), }
    list_display = ('title', 'user', 'inital_post_date')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'votes', 'inital_post_date')
    list_filter = ("user", 'votes')

admin.site.register(models.Posts, PostAdmin)
admin.site.register(models.Comments, CommentAdmin)
admin.site.register(LogEntry)