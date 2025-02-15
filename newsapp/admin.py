from django.contrib import admin
from .models import (
    NewsArticle, User, Bookmark, Notification, Comment, 
    Reaction, TrendingArticle, SearchLog, ArticleRecommendation
)

# Register all models
admin.site.register(NewsArticle)
admin.site.register(User)
admin.site.register(Bookmark)
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(TrendingArticle)
admin.site.register(SearchLog)
admin.site.register(ArticleRecommendation)
