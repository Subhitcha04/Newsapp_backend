from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
import requests
from .models import (
    NewsArticle, User, Bookmark, Notification, Comment, Reaction,
    TrendingArticle, SearchLog, ArticleRecommendation
)
from .serializers import NewsArticleSerializer

# API URL to fetch news data
API_URL = "https://newsdata.io/api/1/news?apikey=pub_67013e1ec9be58cc17b4584c1ca071d4b9ee9&q=latest%20indian%20news"

# Home Page View
def index(request):
    return HttpResponse("Welcome to NewsApp!")

# Fetch News from API and Store in Database
@api_view(['GET'])
@permission_classes([AllowAny])
def fetch_news(request):
    response = requests.get(API_URL)
    
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch news from API"}, status=500)
    
    data = response.json()
    
    if "results" in data:
        articles = data.get("results", [])

        for article in articles:
            news_data = {
                "article_id": article.get("article_id", ""),
                "title": article.get("title", "No Title"),
                "link": article.get("link", ""),
                "keywords": ", ".join(article.get("keywords", [])) if article.get("keywords") else "",
                "creator": article.get("creator", ["Unknown"])[0] if article.get("creator") else "Unknown",
                "video_url": article.get("video_url", ""),
                "description": article.get("description", "No Description"),
                "pubDate": article.get("pubDate", ""),
                "image_url": article.get("image_url", ""),
                "source_name": article.get("source_name", "Unknown"),
                "category": ", ".join(article.get("category", [])) if article.get("category") else "",
                "country": ", ".join(article.get("country", [])) if article.get("country") else "",
            }
            
            existing_article = NewsArticle.objects.filter(article_id=news_data["article_id"]).first()
            if not existing_article:
                NewsArticle.objects.create(**news_data)
    
    return JsonResponse({"message": "News articles updated successfully!"})


# Get All Stored News Articles
@api_view(['GET'])
@permission_classes([AllowAny])
def get_news(request):
    articles = NewsArticle.objects.all()
    response_data = []

    for article in articles:
        response_data.append({
            "_id": str(article.id),
            "article_id": article.article_id,
            "title": article.title,
            "link": article.link,
            "keywords": article.keywords if isinstance(article.keywords, list) else [],
            "creator": article.creator,
            "video_url": article.video_url,
            "description": article.description,
            "pubDate": article.pubDate,
            "image_url": article.image_url,
            "source_name": article.source_name,
            "category": article.category if isinstance(article.category, list) else []
        })

    return JsonResponse(response_data, safe=False)

# User Registration
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Allows unauthenticated users to register
def register_user(request):
    if request.method == "GET":
        return Response({"message": "Use POST to register a new user."}, status=200)

    data = request.data
    if User.objects.filter(email=data.get('email')).exists():
        return JsonResponse({"error": "User already exists"}, status=400)

    user = User.objects.create(
        email=data.get('email'),
        password=make_password(data.get('password')),
        full_name=data.get('full_name'),
        role='reader'
    )
    return JsonResponse({"message": "User registered successfully", "user_id": str(user.user_id)})


# User Login
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Allows unauthenticated users to log in
def login_user(request):
    if request.method == "GET":
        return Response({"message": "Use POST to log in with email and password."}, status=200)

    data = request.data
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    user = User.objects.filter(email=email).first()

    if user and check_password(password, user.password):
        return JsonResponse({"message": "Login successful", "user_id": str(user.user_id)})

    return JsonResponse({"error": "Invalid credentials"}, status=400)
# Bookmark an Article
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bookmark_article(request):
    user = request.user
    article = get_object_or_404(NewsArticle, article_id=request.data['article_id'])
    Bookmark.objects.create(user=user, article=article)
    return JsonResponse({"message": "Article bookmarked successfully!"})

# Get Bookmarked Articles
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookmarks(request):
    user = request.user
    bookmarks = Bookmark.objects.filter(user=user).select_related('article')
    articles = [{"title": b.article.title, "link": b.article.link} for b in bookmarks]
    return JsonResponse({"bookmarks": articles})

# Post a Comment on an Article
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_comment(request):
    user = request.user
    article = get_object_or_404(NewsArticle, article_id=request.data['article_id'])
    comment = Comment.objects.create(
        user=user,
        article=article,
        content=request.data['content'],
        parent_comment=None if 'parent_comment_id' not in request.data else get_object_or_404(Comment, comment_id=request.data['parent_comment_id'])
    )
    return JsonResponse({"message": "Comment posted!", "comment_id": str(comment.comment_id)})

# React to an Article (Like, Dislike, etc.)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def react_to_article(request):
    user = request.user
    article = get_object_or_404(NewsArticle, article_id=request.data['article_id'])
    reaction_type = request.data['reaction_type']
    Reaction.objects.create(user=user, article=article, reaction_type=reaction_type)
    return JsonResponse({"message": "Reaction added successfully!"})

# Get Trending Articles
@api_view(['GET'])
def get_trending_articles(request):
    trending = TrendingArticle.objects.all().order_by('-trend_score')[:10]
    articles = [{"title": t.article.title, "link": t.article.link, "trend_score": t.trend_score} for t in trending]
    return JsonResponse({"trending_articles": articles})

# Log a Search Query
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_search(request):
    user = request.user if request.user.is_authenticated else None
    query = request.data['query_text']
    SearchLog.objects.create(user=user, query_text=query)
    return JsonResponse({"message": "Search logged successfully!"})

# Get Personalized Article Recommendations
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    user = request.user
    recommendations = ArticleRecommendation.objects.filter(user=user).select_related('article')
    articles = [{"title": r.article.title, "link": r.article.link, "reason": r.reason} for r in recommendations]
    return JsonResponse({"recommendations": articles})
