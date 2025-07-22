from django.db import models
from django.contrib.auth.models import User
import json

class MapData(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    reviews_count = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        # Supabase ile senkronizasyon için unique constraint
        unique_together = ['name', 'address']
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        """Model'i dictionary'ye çevirir (Supabase için)"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'website': self.website,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class ScrapingJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    n8n_webhook_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.query} - {self.status}"


class Settings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Ayar değerini alır"""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """Ayar değerini kaydeder"""
        setting, created = cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        return setting


# Instagram Scraper Models
class InstagramData(models.Model):
    username = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    followers_count = models.BigIntegerField(blank=True, null=True)
    following_count = models.BigIntegerField(blank=True, null=True)
    posts_count = models.BigIntegerField(blank=True, null=True)
    profile_pic_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    external_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['username']
    
    def __str__(self):
        return self.username

# Facebook Scraper Models
class FacebookData(models.Model):
    page_name = models.CharField(max_length=255)
    page_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    likes_count = models.BigIntegerField(blank=True, null=True)
    followers_count = models.BigIntegerField(blank=True, null=True)
    page_url = models.URLField(blank=True, null=True)
    profile_pic_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    category = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['page_name']
    
    def __str__(self):
        return self.page_name

# Twitter Scraper Models
class TwitterData(models.Model):
    username = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    followers_count = models.BigIntegerField(blank=True, null=True)
    following_count = models.BigIntegerField(blank=True, null=True)
    tweets_count = models.BigIntegerField(blank=True, null=True)
    profile_pic_url = models.URLField(blank=True, null=True)
    banner_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    join_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['username']
    
    def __str__(self):
        return self.username

# LinkedIn Scraper Models
class LinkedInData(models.Model):
    profile_name = models.CharField(max_length=255)
    headline = models.CharField(max_length=500, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    connections_count = models.IntegerField(blank=True, null=True)
    profile_url = models.URLField(blank=True, null=True)
    profile_pic_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    current_company = models.CharField(max_length=255, blank=True, null=True)
    current_position = models.CharField(max_length=255, blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['profile_name', 'current_company']
    
    def __str__(self):
        return self.profile_name

# TikTok Scraper Models
class TikTokData(models.Model):
    username = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    followers_count = models.BigIntegerField(blank=True, null=True)
    following_count = models.BigIntegerField(blank=True, null=True)
    likes_count = models.BigIntegerField(blank=True, null=True)
    videos_count = models.BigIntegerField(blank=True, null=True)
    profile_pic_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    external_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['username']
    
    def __str__(self):
        return self.username
