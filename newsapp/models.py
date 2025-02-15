from django.db import models
import uuid

class NewsArticle(models.Model):
    article_id = models.CharField(max_length=255, unique=True)
    title = models.TextField()
    link = models.URLField()
    keywords = models.TextField(blank=True, null=True)
    creator = models.CharField(max_length=255, default="Unknown")
    video_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pubDate = models.DateTimeField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    source_name = models.CharField(max_length=255, default="Unknown")
    category = models.TextField(blank=True, null=True)  # Storing as comma-separated values
    country = models.TextField(blank=True, null=True)  # Storing as comma-separated values

    def __str__(self):
        return self.title

class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=255)  # Should be hashed
    full_name = models.CharField(max_length=255)
    preferences = models.JSONField(default=dict, blank=True)  # Stores category/keyword preferences
    role = models.CharField(max_length=10, choices=[('reader', 'Reader'), ('editor', 'Editor'), ('admin', 'Admin')])
    created_at = models.DateTimeField(auto_now_add=True)

class Bookmark(models.Model):
    bookmark_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(NewsArticle, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

class Comment(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, db_index=True)
    parent_comment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  # For replies
    content = models.TextField()
    likes_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

class Reaction(models.Model):
    reaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, db_index=True)
    reaction_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike'), ('love', 'Love'), ('angry', 'Angry')])
    timestamp = models.DateTimeField(auto_now_add=True)

class TrendingArticle(models.Model):
    trend_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, db_index=True)
    trend_score = models.FloatField()  # Based on views, likes, comments
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

class SearchLog(models.Model):
    search_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Nullable for anonymous searches
    query_text = models.CharField(max_length=500, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ArticleRecommendation(models.Model):
    recommendation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, db_index=True)
    reason = models.CharField(max_length=255)  # Example: "Based on your reading history"
    timestamp = models.DateTimeField(auto_now_add=True)
