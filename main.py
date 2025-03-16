from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import os

# Initialize FastAPI
app = FastAPI()

# Environment Setup
uri = os.getenv("MONGO_URI")
if not uri:
    raise RuntimeError("MONGO_URI not set")

# Database Connection
try:
    client = MongoClient(uri, server_api=ServerApi("1"))
    db = client['blog_posts']
    posts_collection = db['blog_posts']
    client.admin.command("ping")
except Exception as e:
    raise RuntimeError("DB connection failed") from e

# Centralized Error Messages
ERRORS = {
    "invalid_id": "Invalid article ID format",
    "not_found": "Article not found",
    "no_posts": "No posts found",
    "create_fail": "Failed to create article",
    "update_fail": "Failed to update article"
}

# Models
class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    tags: List[str]

class BlogPostResponse(BlogPostCreate):
    id: str
    createdAt: str
    updatedAt: str

# Helper function to convert MongoDB document to Pydantic model
def serialize_post(post) -> BlogPostResponse:
    return BlogPostResponse(
        id=str(post["_id"]),
        title=post["title"],
        content=post["content"],
        category=post["category"],
        tags=post["tags"],
        createdAt=post["createdAt"],
        updatedAt=post["updatedAt"]
    )

# Routes
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Blog API"}

@app.post("/new_article/", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
def create_article(article: BlogPostCreate):
    now = datetime.now().isoformat()
    new_post = article.model_dump()
    new_post["createdAt"] = now
    new_post["updatedAt"] = now

    result = posts_collection.insert_one(new_post)
    created_post = posts_collection.find_one({"_id": result.inserted_id})

    if created_post:
        return serialize_post(created_post)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERRORS["create_fail"])

@app.get("/articles/", response_model=List[BlogPostResponse], status_code=status.HTTP_200_OK)
def get_articles():
    articles = posts_collection.find({})
    serialized_articles = [serialize_post(article) for article in articles]

    if not serialized_articles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERRORS["no_posts"])
    
    return serialized_articles

@app.get("/articles/{article_id}", response_model=BlogPostResponse, status_code=status.HTTP_200_OK)
def get_article(article_id: str):
    if not ObjectId.is_valid(article_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERRORS["invalid_id"])
    
    article = posts_collection.find_one({"_id": ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERRORS["not_found"])
    
    return serialize_post(article)

@app.put("/update_article/{article_id}", response_model=BlogPostResponse, status_code=status.HTTP_200_OK)
def update_article(article_id: str, article: BlogPostCreate):
    if not ObjectId.is_valid(article_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERRORS["invalid_id"])
    
    existing_article = posts_collection.find_one({"_id": ObjectId(article_id)})
    if not existing_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERRORS["not_found"])

    now = datetime.now().isoformat()
    update_data = article.model_dump()
    update_data["updatedAt"] = now

    result = posts_collection.update_one({"_id": ObjectId(article_id)}, {"$set": update_data})

    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERRORS["update_fail"])
    
    updated_article = posts_collection.find_one({"_id": ObjectId(article_id)})
    return serialize_post(updated_article)

@app.delete("/delete_article/{article_id}", status_code=status.HTTP_200_OK)
def delete_article(article_id: str):
    if not ObjectId.is_valid(article_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERRORS["invalid_id"])
    
    existing_article = posts_collection.find_one({"_id": ObjectId(article_id)})
    if not existing_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERRORS["not_found"])
    
    posts_collection.delete_one({"_id": ObjectId(article_id)})
    return {"message": "Article deleted successfully"}

@app.get("/filter_article/", response_model=List[BlogPostResponse], status_code=status.HTTP_200_OK)
def filter_article(search_term: Optional[str] = None):
    if not search_term:
        return get_articles()
    
    query = {
        "$or": [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"content": {"$regex": search_term, "$options": "i"}},
            {"category": {"$regex": search_term, "$options": "i"}},
            {"tags": {"$in": [search_term]}}
        ]
    }

    articles = posts_collection.find(query)
    serialized_articles = [serialize_post(article) for article in articles]

    if not serialized_articles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERRORS["no_posts"])

    return serialized_articles
