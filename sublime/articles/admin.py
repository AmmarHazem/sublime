from django.contrib import admin
from sublime.articles.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status')
    list_filter = ('user', 'status', 'timestamp')
