#!/usr/bin/env python3
"""
Django ORM'deki tüm map data'yı Supabase'e aktaran script
"""

import os
import sys
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from mapscraper.models import MapData
from mapscraper.supabase_service import supabase_service

def main():
    print('🔄 Django ORM -> Supabase Sync başlıyor...\n')
    
    # Django ORM veri sayısı
    django_count = MapData.objects.count()
    print(f'📊 Django ORM\'de toplam: {django_count} kayıt')
    
    # Supabase veri sayısı
    supabase_data = supabase_service.get_map_data(limit=10000)
    supabase_count = len(supabase_data) if supabase_data else 0
    print(f'📊 Supabase\'de toplam: {supabase_count} kayıt\n')
    
    if django_count == 0:
        print('❌ Django ORM\'de veri yok!')
        return
    
    if not supabase_service.is_connected():
        print('❌ Supabase bağlantısı yok!')
        return
    
    print(f'🔄 {django_count} kayıt Supabase\'e aktarılacak...\n')
    
    # Django ORM'den tüm verileri al
    all_django_data = []
    for i, obj in enumerate(MapData.objects.all(), 1):
        data = {
            'name': obj.name,
            'address': obj.address,
            'phone': obj.phone or '',
            'website': obj.website or '',
            'rating': float(obj.rating) if obj.rating else None,
            'reviews_count': int(obj.reviews_count) if obj.reviews_count else None,
            'latitude': float(obj.latitude) if obj.latitude else None,
            'longitude': float(obj.longitude) if obj.longitude else None,
            'category': obj.category or '',
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'updated_at': obj.updated_at.isoformat() if obj.updated_at else None
        }
        all_django_data.append(data)
        
        if i % 50 == 0:
            print(f'  📦 {i}/{django_count} kayıt hazırlandı...')
    
    print(f'✅ {len(all_django_data)} kayıt hazırlandı\n')
    
    # Supabase'e batch upsert
    batch_size = 50
    total_inserted = 0
    
    for i in range(0, len(all_django_data), batch_size):
        batch = all_django_data[i:i+batch_size]
        batch_num = i//batch_size + 1
        
        try:
            # Upsert yap (name + address unique olacak şekilde)
            response = supabase_service.supabase.table('map_data').upsert(
                batch, 
                on_conflict='name,address'
            ).execute()
            
            if response.data:
                inserted_count = len(response.data)
                total_inserted += inserted_count
                print(f'  📤 Batch {batch_num}: {inserted_count} kayıt eklendi/güncellendi')
            else:
                print(f'  ❌ Batch {batch_num}: Hata - {response}')
                
        except Exception as e:
            print(f'  ❌ Batch {batch_num} hatası: {e}')
            continue
    
    print(f'\n🎉 Transfer tamamlandı!')
    print(f'📊 Toplam {total_inserted} kayıt Supabase\'e aktarıldı\n')
    
    # Final kontrol
    final_check = supabase_service.get_map_data(limit=10000)
    final_count = len(final_check) if final_check else 0
    print(f'✅ Final kontrol: Supabase\'de şimdi {final_count} kayıt var')
    
    if final_count >= django_count:
        print('🎯 Sync başarılı! Tüm veriler aktarıldı.')
    else:
        print(f'⚠️  Eksik veri var: Django({django_count}) -> Supabase({final_count})')

if __name__ == '__main__':
    main()
