#!/usr/bin/env python
import os
import django
import sys
from datetime import datetime, timedelta
import random

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from mapscraper.models import MapData, InstagramData, FacebookData, TwitterData, LinkedInData, TikTokData

def add_more_sample_data():
    print("Daha fazla örnek veri ekleniyor...")
    
    # Instagram verileri
    instagram_users = [
        {'username': 'travel_istanbul', 'full_name': 'Istanbul Travel Guide', 'followers_count': 125000, 'bio': 'Best places to visit in Istanbul', 'category': 'Travel'},
        {'username': 'food_lover_tr', 'full_name': 'Turkish Food Lover', 'followers_count': 89000, 'bio': 'Traditional Turkish cuisine', 'category': 'Food'},
        {'username': 'tech_guru_tr', 'full_name': 'Tech Guru Turkey', 'followers_count': 156000, 'bio': 'Latest tech news and reviews', 'category': 'Technology'},
        {'username': 'fashion_tr', 'full_name': 'Turkish Fashion', 'followers_count': 203000, 'bio': 'Fashion trends from Turkey', 'category': 'Fashion'},
        {'username': 'fitness_coach_tr', 'full_name': 'Fitness Coach', 'followers_count': 67000, 'bio': 'Personal trainer and nutrition expert', 'category': 'Fitness'},
    ]
    
    for user in instagram_users:
        InstagramData.objects.get_or_create(
            username=user['username'],
            defaults={
                'full_name': user['full_name'],
                'bio': user['bio'],
                'followers_count': user['followers_count'],
                'following_count': random.randint(500, 2000),
                'posts_count': random.randint(100, 1000),
                'is_verified': random.choice([True, False]),
                'is_private': False,
                'category': user['category'],
            }
        )
    
    # Facebook verileri
    facebook_pages = [
        {'page_name': 'Istanbul Tourism', 'page_id': 'istanbul_tourism_official', 'likes_count': 450000, 'category': 'Travel'},
        {'page_name': 'Turkish Airlines', 'page_id': 'turkishairlines_official', 'likes_count': 2100000, 'category': 'Airlines'},
        {'page_name': 'Galatasaray', 'page_id': 'galatasaray_official', 'likes_count': 8500000, 'category': 'Sports'},
        {'page_name': 'Turkish Delight Recipes', 'page_id': 'turkish_delight_recipes', 'likes_count': 125000, 'category': 'Food'},
        {'page_name': 'Cappadocia Tours', 'page_id': 'cappadocia_tours_official', 'likes_count': 67000, 'category': 'Travel'},
    ]
    
    for page in facebook_pages:
        FacebookData.objects.get_or_create(
            page_name=page['page_name'],
            defaults={
                'page_id': page['page_id'],
                'likes_count': page['likes_count'],
                'followers_count': page['likes_count'] + random.randint(1000, 50000),
                'category': page['category'],
                'description': f"Official {page['page_name']} page",
                'is_verified': random.choice([True, False]),
            }
        )
    
    # Twitter verileri
    twitter_accounts = [
        {'username': 'istanbul_daily', 'display_name': 'Istanbul Daily News', 'followers_count': 234000, 'bio': 'Daily news from Istanbul'},
        {'username': 'turkish_tech', 'display_name': 'Turkish Tech Community', 'followers_count': 89000, 'bio': 'Technology community in Turkey'},
        {'username': 'bosphorus_view', 'display_name': 'Bosphorus View', 'followers_count': 156000, 'bio': 'Beautiful views of Bosphorus'},
        {'username': 'turkish_cuisine', 'display_name': 'Turkish Cuisine', 'followers_count': 78000, 'bio': 'Traditional Turkish food recipes'},
        {'username': 'ankara_events', 'display_name': 'Ankara Events', 'followers_count': 45000, 'bio': 'Events happening in Ankara'},
    ]
    
    for account in twitter_accounts:
        TwitterData.objects.get_or_create(
            username=account['username'],
            defaults={
                'display_name': account['display_name'],
                'bio': account['bio'],
                'followers_count': account['followers_count'],
                'following_count': random.randint(100, 1000),
                'tweets_count': random.randint(500, 5000),
                'is_verified': random.choice([True, False]),
                'location': random.choice(['Istanbul', 'Ankara', 'Izmir', 'Antalya']),
            }
        )
    
    # LinkedIn verileri
    linkedin_profiles = [
        {'profile_name': 'Ahmet Yılmaz', 'company': 'Turkish Airlines', 'position': 'Software Engineer', 'connections_count': 1200},
        {'profile_name': 'Elif Demir', 'company': 'Turkcell', 'position': 'Data Scientist', 'connections_count': 890},
        {'profile_name': 'Mehmet Kaya', 'company': 'Garanti BBVA', 'position': 'Product Manager', 'connections_count': 1567},
        {'profile_name': 'Zeynep Özkan', 'company': 'Trendyol', 'position': 'UX Designer', 'connections_count': 734},
        {'profile_name': 'Can Erdoğan', 'company': 'Getir', 'position': 'Marketing Manager', 'connections_count': 2100},
    ]
    
    for profile in linkedin_profiles:
        LinkedInData.objects.get_or_create(
            profile_name=profile['profile_name'],
            defaults={
                'current_company': profile['company'],
                'current_position': profile['position'],
                'connections_count': profile['connections_count'],
                'industry': random.choice(['Technology', 'Finance', 'E-commerce', 'Aviation', 'Telecommunications']),
                'location': random.choice(['Istanbul', 'Ankara', 'Izmir']),
                'experience_years': random.randint(2, 15),
                'headline': f"{profile['position']} at {profile['company']}",
                'summary': f"Experienced {profile['position']} with {random.randint(2, 15)} years in the industry.",
            }
        )
    
    # TikTok verileri
    tiktok_creators = [
        {'username': 'istanbul_vibes', 'display_name': 'Istanbul Vibes', 'followers_count': 567000, 'bio': 'Best spots in Istanbul'},
        {'username': 'turkish_dance', 'display_name': 'Turkish Folk Dance', 'followers_count': 234000, 'bio': 'Traditional Turkish dances'},
        {'username': 'cooking_turkish', 'display_name': 'Turkish Cooking', 'followers_count': 445000, 'bio': 'Easy Turkish recipes'},
        {'username': 'travel_turkey', 'display_name': 'Travel Turkey', 'followers_count': 678000, 'bio': 'Amazing places in Turkey'},
        {'username': 'tech_turkey', 'display_name': 'Tech Turkey', 'followers_count': 123000, 'bio': 'Latest tech trends in Turkey'},
    ]
    
    for creator in tiktok_creators:
        TikTokData.objects.get_or_create(
            username=creator['username'],
            defaults={
                'display_name': creator['display_name'],
                'bio': creator['bio'],
                'followers_count': creator['followers_count'],
                'following_count': random.randint(100, 500),
                'likes_count': creator['followers_count'] * random.randint(10, 50),
                'videos_count': random.randint(50, 500),
                'is_verified': random.choice([True, False]),
            }
        )
    
    # Map verileri
    map_locations = [
        {'name': 'Hagia Sophia', 'address': 'Sultanahmet, Istanbul', 'rating': 4.8, 'category': 'Museum'},
        {'name': 'Galata Tower', 'address': 'Galata, Istanbul', 'rating': 4.5, 'category': 'Landmark'},
        {'name': 'Grand Bazaar', 'address': 'Beyazıt, Istanbul', 'rating': 4.3, 'category': 'Shopping'},
        {'name': 'Bosphorus Bridge', 'address': 'Bosphorus, Istanbul', 'rating': 4.6, 'category': 'Bridge'},
        {'name': 'Cappadocia Hot Air Balloon', 'address': 'Cappadocia, Nevşehir', 'rating': 4.9, 'category': 'Activity'},
        {'name': 'Pamukkale Thermal Pools', 'address': 'Pamukkale, Denizli', 'rating': 4.7, 'category': 'Natural'},
        {'name': 'Ephesus Ancient City', 'address': 'Selçuk, İzmir', 'rating': 4.8, 'category': 'Historical'},
        {'name': 'Antalya Marina', 'address': 'Antalya', 'rating': 4.4, 'category': 'Marina'},
    ]
    
    for location in map_locations:
        MapData.objects.get_or_create(
            name=location['name'],
            defaults={
                'address': location['address'],
                'rating': location['rating'],
                'category': location['category'],
                'latitude': random.uniform(36.0, 42.0),
                'longitude': random.uniform(26.0, 45.0),
                'phone': f"+90 {random.randint(200, 600)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
                'website': f"https://www.{location['name'].lower().replace(' ', '')}.com",
            }
        )
    
    print("Örnek veriler başarıyla eklendi!")
    
    # Toplam verileri göster
    print(f"\nToplam veriler:")
    print(f"Map Data: {MapData.objects.count()}")
    print(f"Instagram Data: {InstagramData.objects.count()}")
    print(f"Facebook Data: {FacebookData.objects.count()}")
    print(f"Twitter Data: {TwitterData.objects.count()}")
    print(f"LinkedIn Data: {LinkedInData.objects.count()}")
    print(f"TikTok Data: {TikTokData.objects.count()}")

if __name__ == '__main__':
    add_more_sample_data()
