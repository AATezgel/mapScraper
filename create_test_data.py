#!/usr/bin/env python
import os
import sys
import django
import json

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from mapscraper.models import MapData, ScrapingJob
from django.contrib.auth.models import User

# Test verisi oluştur
test_data = [
    {
        "name": "Starbucks Taksim",
        "address": "Taksim, İstanbul",
        "phone": "+90 212 123 45 67",
        "website": "https://www.starbucks.com.tr",
        "rating": 4.2,
        "reviews_count": 1500,
        "latitude": 41.0370,
        "longitude": 28.9851,
        "category": "Kafe"
    },
    {
        "name": "Kahve Dünyası",
        "address": "Beyoğlu, İstanbul",
        "phone": "+90 212 987 65 43",
        "website": "https://www.kahvedunyasi.com",
        "rating": 4.0,
        "reviews_count": 890,
        "latitude": 41.0362,
        "longitude": 28.9777,
        "category": "Kafe"
    },
    {
        "name": "Gloria Jean's",
        "address": "Şişli, İstanbul",
        "phone": "+90 212 456 78 90",
        "website": "https://www.gloriajeans.com.tr",
        "rating": 4.3,
        "reviews_count": 650,
        "latitude": 41.0458,
        "longitude": 28.9881,
        "category": "Kafe"
    }
]

# Veriyi kaydet
for item in test_data:
    MapData.objects.create(
        name=item['name'],
        address=item['address'],
        phone=item['phone'],
        website=item['website'],
        rating=item['rating'],
        reviews_count=item['reviews_count'],
        latitude=item['latitude'],
        longitude=item['longitude'],
        category=item['category']
    )

print("Test verisi oluşturuldu!")
print(f"Toplam {MapData.objects.count()} veri kaydı var.")
