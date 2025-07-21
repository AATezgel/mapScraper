"""
Django yönetim komutu: Supabase veritabanını senkronize eder
Kullanım: python manage.py sync_supabase_data
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from mapscraper.supabase_service import supabase_service
from mapscraper.models import MapData
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Supabase veritabanını Django ORM ile senkronize eder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['django_orm', 'supabase', 'both'],
            default='both',
            help='Senkronizasyon kaynağı (django_orm, supabase, both)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Sadece kontrol et, veri değiştirme'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Supabase senkronizasyon başlatılıyor...'))
        
        # Supabase bağlantısını kontrol et
        if not supabase_service.is_connected():
            self.stdout.write(self.style.ERROR('Supabase bağlantısı kurulamadı!'))
            return
        
        source = options['source']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - Hiçbir veri değiştirilmeyecek'))
        
        # Django ORM'den Supabase'e senkronizasyon
        if source in ['django_orm', 'both']:
            self.sync_from_django_orm(dry_run)
        
        # Supabase'den Django'ya senkronizasyon  
        if source in ['supabase', 'both']:
            self.sync_from_supabase(dry_run)
        
        # İstatistikleri göster
        self.display_sync_stats()
        
        self.stdout.write(self.style.SUCCESS('Senkronizasyon tamamlandı!'))

    def sync_from_supabase(self, dry_run):
        """Supabase'den Django ORM'e senkronizasyon"""
        self.stdout.write('Supabase\'den Django\'ya senkronize ediliyor...')
        
        try:
            # Supabase'den tüm verileri al
            supabase_data = supabase_service.get_all_map_data()
            self.stdout.write(f'Supabase\'den {len(supabase_data)} kayıt alındı')
            
            if not dry_run and supabase_data:
                created_count = 0
                updated_count = 0
                failed_count = 0
                
                for item in supabase_data:
                    try:
                        obj, created = MapData.objects.update_or_create(
                            name=item.get('name'),
                            address=item.get('address'),
                            defaults={
                                'phone': item.get('phone', ''),
                                'website': item.get('website', ''),
                                'rating': item.get('rating'),
                                'reviews_count': item.get('reviews_count'),
                                'latitude': item.get('latitude'),
                                'longitude': item.get('longitude'),
                                'category': item.get('category', ''),
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                            
                    except Exception as e:
                        failed_count += 1
                        self.stdout.write(self.style.ERROR(f'Hata: {e}'))
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Supabase→Django senkronizasyonu: '
                        f'{created_count} yeni, '
                        f'{updated_count} güncellendi, '
                        f'{failed_count} hata'
                    )
                )
            else:
                self.stdout.write(f'DRY RUN: {len(supabase_data)} kayıt senkronize edilecekti')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Supabase senkronizasyon hatası: {e}'))

    def sync_from_django_orm(self, dry_run):
        """Django ORM'den Supabase'e senkronizasyon"""
        self.stdout.write('Django ORM\'den Supabase\'e senkronize ediliyor...')
        
        try:
            # Django'dan tüm verileri al
            django_data = MapData.objects.all()
            self.stdout.write(f'Django ORM\'den {django_data.count()} kayıt alındı')
            
            if not dry_run and django_data.exists():
                # Django verilerini Supabase formatına çevir
                formatted_data = []
                for item in django_data:
                    formatted_data.append(item.to_dict())
                
                # Supabase'e senkronize et
                result = supabase_service.bulk_upsert_map_data(formatted_data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Django→Supabase senkronizasyonu: '
                        f'{result.get("created", 0)} yeni, '
                        f'{result.get("updated", 0)} güncellendi, '
                        f'{result.get("failed", 0)} hata'
                    )
                )
            else:
                self.stdout.write(f'DRY RUN: {django_data.count()} kayıt senkronize edilecekti')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Django ORM senkronizasyon hatası: {e}'))

    def display_sync_stats(self):
        """Senkronizasyon istatistiklerini göster"""
        try:
            stats = supabase_service.get_sync_stats()
            django_count = MapData.objects.count()
            supabase_count = stats.get("total_records", 0)
            
            self.stdout.write('\n--- Senkronizasyon İstatistikleri ---')
            self.stdout.write(f'Django kayıt sayısı: {django_count}')
            self.stdout.write(f'Supabase kayıt sayısı: {supabase_count}')
            self.stdout.write(f'Fark: {abs(django_count - supabase_count)}')
            self.stdout.write(f'Son 24 saatteki job sayısı: {stats.get("recent_jobs_count", 0)}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'İstatistik alma hatası: {e}'))
