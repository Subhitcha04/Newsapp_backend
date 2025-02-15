from rest_framework import serializers
from .models import NewsArticle
from datetime import datetime

class NewsArticleSerializer(serializers.ModelSerializer):
    pubDate = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = '__all__'

    def get_pubDate(self, obj):
        try:
            return datetime.strptime(obj.pubDate, "%Y-%m-%d %H:%M:%S").isoformat()
        except ValueError:
            return obj.pubDate  # Return as-is if conversion fails
