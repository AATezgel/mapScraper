#!/usr/bin/env python
import os
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from mapscraper.supabase_service import supabase_service
from mapscraper.models import MapData
import json

# Mevcut verileri listele
django_count = MapData.objects.count()
print(f"Django'da toplam veri sayısı: {django_count}")

if django_count > 0:
    print("\nDjango'daki son 5 veri:")
    for data in MapData.objects.all()[:5]:
        print(f"- {data.name} ({data.address[:50]}...)")

if supabase_service.is_connected():
    supabase_data = supabase_service.get_map_data(limit=5)
    print(f"\nSupabase'den çekilen veri sayısı: {len(supabase_data) if supabase_data else 0}")
    if supabase_data:
        print("İlk veri:", json.dumps(supabase_data[0], indent=2, ensure_ascii=False))
else:
    print("Supabase bağlantısı yok")
