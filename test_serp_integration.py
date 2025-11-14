#!/usr/bin/env python
"""
SERP API entegrasyonunu test eden script
"""
import os
import django
import requests

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from mapscraper.models import MapData, ScrapingJob, Settings
from django.contrib.auth.models import User

def test_serp_api():
    """SERP API'yi direkt test et"""
    print("🔍 SERP API Test Başlıyor...")
    print("=" * 60)
    
    # API Key'i al
    serp_api_key = Settings.get_setting('serp_api_key', '19b8cfa3a27fb5b568411275ca980abbba9cdc077b6a1ee93bf5c18ca556b397')
    print(f"✓ API Key: {serp_api_key[:20]}...")
    
    # Test query
    test_query = "restaurant istanbul"
    print(f"✓ Test Query: {test_query}")
    
    # SERP API parametreleri
    params = {
        'engine': 'google_maps',
        'q': test_query,
        'type': 'search',
        'api_key': serp_api_key
    }
    
    print("\n📡 SERP API'ye istek gönderiliyor...")
    
    try:
        response = requests.get('https://serpapi.com/search.json', params=params, timeout=30)
        
        print(f"✓ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            local_results = data.get('local_results', [])
            
            print(f"✓ Toplam Sonuç: {len(local_results)}")
            
            if local_results:
                print("\n📋 İlk 3 Sonuç:")
                print("-" * 60)
                
                for i, result in enumerate(local_results[:3], 1):
                    gps = result.get('gps_coordinates', {})
                    print(f"\n{i}. {result.get('title', 'N/A')}")
                    print(f"   Adres: {result.get('address', 'N/A')}")
                    print(f"   Kategori: {result.get('type', 'N/A')}")
                    print(f"   Rating: {result.get('rating', 'N/A')}")
                    print(f"   Telefon: {result.get('phone', 'N/A')}")
                    print(f"   Konum: {gps.get('latitude', 'N/A')}, {gps.get('longitude', 'N/A')}")
                
                # Veritabanına kaydet
                print(f"\n💾 Veritabanına kaydediliyor...")
                saved_count = 0
                updated_count = 0
                
                for item in local_results:
                    gps = item.get('gps_coordinates', {})
                    
                    map_data = {
                        'name': item.get('title', ''),
                        'address': item.get('address', ''),
                        'phone': item.get('phone', ''),
                        'rating': float(item.get('rating', 0)) if item.get('rating') else None,
                        'category': item.get('type', ''),
                        'website': item.get('website', ''),
                        'latitude': gps.get('latitude') if gps.get('latitude') else None,
                        'longitude': gps.get('longitude') if gps.get('longitude') else None,
                    }
                    
                    obj, created = MapData.objects.update_or_create(
                        name=map_data['name'],
                        defaults=map_data
                    )
                    
                    if created:
                        saved_count += 1
                    else:
                        updated_count += 1
                
                print(f"✓ {saved_count} yeni kayıt eklendi")
                print(f"✓ {updated_count} kayıt güncellendi")
                
                # Toplam kayıt sayısı
                total_records = MapData.objects.count()
                print(f"✓ Toplam MapData Kayıtları: {total_records}")
                
                print("\n" + "=" * 60)
                print("✅ SERP API Entegrasyonu Başarılı!")
                return True
            else:
                print("⚠️  Sonuç bulunamadı")
                return False
        else:
            print(f"❌ SERP API Hatası: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ SERP API zaman aşımına uğradı")
        return False
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def show_database_stats():
    """Veritabanı istatistiklerini göster"""
    print("\n📊 Veritabanı İstatistikleri")
    print("=" * 60)
    
    total_map_data = MapData.objects.count()
    total_jobs = ScrapingJob.objects.count()
    
    print(f"Map Data Kayıtları: {total_map_data}")
    print(f"Scraping Jobs: {total_jobs}")
    
    # Kategori bazlı istatistikler
    from django.db.models import Count
    category_stats = MapData.objects.values('category').annotate(count=Count('category')).order_by('-count')[:5]
    
    if category_stats:
        print("\nEn Çok Kategoriler:")
        for stat in category_stats:
            if stat['category']:
                print(f"  - {stat['category']}: {stat['count']}")

if __name__ == '__main__':
    print("\n🚀 SERP API Entegrasyon Testi\n")
    
    # Önce veritabanı durumunu göster
    show_database_stats()
    
    # SERP API testini çalıştır
    success = test_serp_api()
    
    # Sonuçları tekrar göster
    if success:
        show_database_stats()
    
    print("\n✨ Test tamamlandı!\n")
