#!/usr/bin/env python
import os
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from mapscraper.supabase_service import supabase_service
from mapscraper.models import MapData
import json

# Test verisi ekle
test_data = {
    'name': 'Test Restaurant',
    'address': 'Test Address, Istanbul',
    'phone': '+90 555 123 45 67',
    'rating': 4.5,
    'reviews_count': 250,
    'category': 'Restaurant',
    'latitude': 41.0082,
    'longitude': 28.9784,
    'website': 'http://example.com'
}

# Django'ya ekle
map_data = MapData.objects.create(**test_data)
print(f"Django'ya eklendi: {map_data.id}")

# Supabase'e de ekle
if supabase_service.is_connected():
    result = supabase_service.insert_map_data([test_data])
    print(f"Supabase'e eklendi: {result}")
else:
    print("Supabase bağlantısı yok")

# Kaç tane veri var kontrol et
django_count = MapData.objects.count()
print(f"Django'da toplam veri sayısı: {django_count}")

if supabase_service.is_connected():
    supabase_data = supabase_service.get_map_data(limit=10)
    print(f"Supabase'den çekilen veri sayısı: {len(supabase_data) if supabase_data else 0}")
    if supabase_data:
        print("İlk veri:", json.dumps(supabase_data[0], indent=2, ensure_ascii=False))
