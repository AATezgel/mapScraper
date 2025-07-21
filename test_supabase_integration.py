"""
Supabase entegrasyonunu test etmek için test dosyası
"""

import os
import sys
import django

# Django settings'i yükle
sys.path.append('/Users/aatezgel/Projects/django/mapToplayici')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from mapscraper.supabase_service import supabase_service
from mapscraper.models import MapData

def test_supabase_integration():
    """Supabase entegrasyonunu test eder"""
    print("=== Supabase Entegrasyon Testi ===")
    
    # 1. Bağlantı testi
    print(f"Supabase bağlantısı: {'✓ Bağlı' if supabase_service.is_connected() else '✗ Bağlı değil'}")
    
    if not supabase_service.is_connected():
        print("Supabase bağlantısı için .env dosyasındaki SUPABASE_URL ve SUPABASE_KEY değerlerini güncellemeniz gerekiyor.")
        return
    
    # 2. Test connection
    connection_test = supabase_service.test_connection()
    print(f"Bağlantı testi: {'✓ Başarılı' if connection_test else '✗ Başarısız'}")
    
    # 3. Veri çekme testi
    try:
        data = supabase_service.get_map_data(limit=5)
        print(f"Veri çekme testi: ✓ {len(data)} kayıt bulundu")
    except Exception as e:
        print(f"Veri çekme hatası: ✗ {e}")
    
    # 4. Manuel test verisi oluştur
    print("\n--- Manuel Test Verisi ---")
    test_data = [
        {
            'name': 'Test Kafe 1',
            'address': 'Test Adres 1, Istanbul',
            'phone': '0212 123 4567',
            'rating': 4.5,
            'category': 'Kafe',
            'latitude': 41.0082,
            'longitude': 28.9784,
            'status': 'active',
            'job_id': 'test_job_1'
        },
        {
            'name': 'Test Restaurant 2',
            'address': 'Test Adres 2, Ankara',
            'phone': '0312 987 6543',
            'rating': 4.2,
            'category': 'Restaurant',
            'latitude': 39.9334,
            'longitude': 32.8597,
            'status': 'active',
            'job_id': 'test_job_2'
        }
    ]
    print(f"Test verisi: {len(test_data)} kayıt")
    
    # 5. Supabase'e test verisi ekleme
    if test_data:
        print("\n--- Supabase Test Verisi Ekleme ---")
        try:
            result = supabase_service.upsert_map_data(test_data)
            if result.get('success'):
                print(f"Supabase test: ✓ {result.get('upserted_count')} kayıt eklendi")
            else:
                print(f"Supabase test hatası: ✗ {result.get('error')}")
        except Exception as e:
            print(f"Supabase test hatası: ✗ {e}")
    
    print("\n=== Test Tamamlandı ===")

if __name__ == "__main__":
    test_supabase_integration()
