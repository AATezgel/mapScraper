"""
Celery task'ları
Otomatik senkronizasyon ve background işlemler için
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .supabase_service import supabase_service
from .models import ScrapingJob
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def sync_data_from_n8n_task():
    """
    N8N'den gelen verileri Supabase ile senkronize eder
    Bu task N8N webhook'larından sonra çalıştırılabilir
    """
    try:
        logger.info("N8N veri senkronizasyon task'ı başlatıldı")
        
        # Supabase bağlantısını kontrol et
        if not supabase_service.is_connected():
            logger.error("Supabase bağlantısı kurulamadı")
            return {"success": False, "error": "Supabase bağlantısı yok"}
        
        # Son ScrapingJob'ları kontrol et (completed olanları)
        from .models import ScrapingJob
        recent_jobs = ScrapingJob.objects.filter(
            status='completed',
            created_at__gte=timezone.now() - timedelta(minutes=30)
        )
        
        processed_count = 0
        for job in recent_jobs:
            # Job ile ilişkili MapData'ları Supabase'e sync et
            logger.info(f"Job {job.id} için veri senkronize ediliyor")
            processed_count += 1
        
        result = {
            "success": True,
            "processed_jobs": processed_count,
            "message": f"{processed_count} job verisi işlendi"
        }
        
        logger.info(f"N8N veri senkronizasyonu tamamlandı: {result}")
        return result
        
    except Exception as e:
        logger.error(f"N8N veri senkronizasyon task'ında hata: {e}")
        return {"success": False, "error": str(e)}

@shared_task
def sync_supabase_to_django_task():
    """
    Supabase'den Django ORM'e senkronizasyon yapar
    Backup ve fallback için kullanılır
    """
    try:
        logger.info("Supabase-Django senkronizasyon task'ı başlatıldı")
        
        if not supabase_service.is_connected():
            logger.error("Supabase bağlantısı kurulamadı")
            return {"success": False, "error": "Supabase bağlantısı yok"}
        
        # Supabase'den tüm verileri al
        supabase_data = supabase_service.get_all_map_data()
        
        if not supabase_data:
            logger.warning("Supabase'de veri bulunamadı")
            return {"success": False, "error": "Supabase'de veri yok"}
        
        # Django ORM'e kaydet
        from .models import MapData
        
        created_count = 0
        updated_count = 0
        failed_count = 0
        
        for item in supabase_data:
            try:
                obj, created = MapData.objects.update_or_create(
                    name=item.get('name'),
                    address=item.get('address'),
                    defaults={
                        'phone': item.get('phone'),
                        'website': item.get('website'),
                        'rating': item.get('rating'),
                        'reviews_count': item.get('reviews_count'),
                        'latitude': item.get('latitude'),
                        'longitude': item.get('longitude'),
                        'category': item.get('category'),
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Django ORM'e kayıt hatası: {e}")
                failed_count += 1
        
        result = {
            "success": True,
            "created": created_count,
            "updated": updated_count,
            "failed": failed_count,
            "total_processed": len(supabase_data)
        }
        
        logger.info(f"Supabase-Django senkronizasyonu tamamlandı: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Supabase-Django senkronizasyon task'ında hata: {e}")
        return {"success": False, "error": str(e)}

@shared_task
def cleanup_old_jobs_task():
    """
    30 günden eski ScrapingJob kayıtlarını temizler
    """
    try:
        logger.info("Eski job temizleme task'ı başlatıldı")
        
        # 30 gün öncesinden eski kayıtları sil
        cutoff_date = timezone.now() - timedelta(days=30)
        old_jobs = ScrapingJob.objects.filter(created_at__lt=cutoff_date)
        
        deleted_count = old_jobs.count()
        old_jobs.delete()
        
        logger.info(f"{deleted_count} eski job kaydı silindi")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Job temizleme task'ında hata: {e}")
        return {"success": False, "error": str(e)}

@shared_task
def test_supabase_connection_task():
    """
    Supabase bağlantısını test eder
    """
    try:
        if supabase_service.test_connection():
            logger.info("Supabase bağlantı testi başarılı")
            return {"success": True, "message": "Supabase bağlantısı aktif"}
        else:
            logger.error("Supabase bağlantı testi başarısız")
            return {"success": False, "error": "Supabase bağlantısı başarısız"}
            
    except Exception as e:
        logger.error(f"Supabase bağlantı testi sırasında hata: {e}")
        return {"success": False, "error": str(e)}

@shared_task
def manual_sync_task(source='supabase'):
    """
    Manuel senkronizasyon task'ı
    Args:
        source (str): 'supabase', 'django_orm', veya 'both'
    """
    try:
        logger.info(f"Manuel senkronizasyon başlatıldı: {source}")
        results = {}
        
        if source in ['supabase', 'both']:
            results['supabase_test'] = test_supabase_connection_task.delay().get()
        
        if source in ['django_orm', 'both']:
            results['django_sync'] = sync_supabase_to_django_task.delay().get()
        
        logger.info(f"Manuel senkronizasyon tamamlandı: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Manuel senkronizasyon task'ında hata: {e}")
        return {"success": False, "error": str(e)}

@shared_task
def auto_sync_task():
    """
    Otomatik periyodik senkronizasyon task'ı
    Bu task düzenli aralıklarla çalışarak veri tutarlılığını sağlar
    """
    try:
        logger.info("Otomatik senkronizasyon task'ı başlatıldı")
        
        # Supabase bağlantısını test et
        if not supabase_service.is_connected():
            logger.warning("Supabase bağlantısı yok, otomatik senkronizasyon atlanıyor")
            return {"success": False, "error": "Supabase bağlantısı yok"}
        
        # İstatistikleri al
        from .models import MapData
        django_count = MapData.objects.count()
        supabase_stats = supabase_service.get_sync_stats()
        supabase_count = supabase_stats.get('total_records', 0)
        
        logger.info(f"Veri sayıları - Django: {django_count}, Supabase: {supabase_count}")
        
        # Eğer fark 10'dan fazla ise senkronizasyon yap
        diff = abs(django_count - supabase_count)
        if diff > 10:
            logger.info(f"Veri farkı {diff}, senkronizasyon başlatılıyor")
            
            # Hem Django'dan Supabase'e hem Supabase'den Django'ya sync
            django_to_supabase_result = sync_django_to_supabase_task.delay().get()
            supabase_to_django_result = sync_supabase_to_django_task.delay().get()
            
            result = {
                "success": True,
                "initial_diff": diff,
                "django_to_supabase": django_to_supabase_result,
                "supabase_to_django": supabase_to_django_result,
                "auto_sync": True
            }
            
            logger.info(f"Otomatik senkronizasyon tamamlandı: {result}")
            return result
        else:
            logger.info(f"Veri farkı küçük ({diff}), senkronizasyon gerekmiyor")
            return {
                "success": True,
                "diff": diff,
                "action": "no_sync_needed",
                "django_count": django_count,
                "supabase_count": supabase_count
            }
        
    except Exception as e:
        logger.error(f"Otomatik senkronizasyon task'ında hata: {e}")
        return {"success": False, "error": str(e)}

@shared_task
def sync_django_to_supabase_task():
    """
    Django ORM'deki verileri Supabase'e senkronize eder
    """
    try:
        logger.info("Django-Supabase senkronizasyon task'ı başlatıldı")
        
        # Supabase bağlantısını kontrol et
        if not supabase_service.is_connected():
            logger.error("Supabase bağlantısı kurulamadı")
            return {"success": False, "error": "Supabase bağlantısı yok"}
        
        # Django'daki tüm MapData'ları al
        from .models import MapData
        django_data = MapData.objects.all()
        
        # Batch olarak Supabase'e gönder
        batch_size = 100
        total_processed = 0
        success_count = 0
        
        for i in range(0, django_data.count(), batch_size):
            batch = django_data[i:i+batch_size]
            
            # Veriyi format et
            formatted_data = []
            for item in batch:
                formatted_data.append({
                    'name': item.name,
                    'address': item.address,
                    'phone': item.phone or '',
                    'website': item.website or '',
                    'rating': float(item.rating) if item.rating else None,
                    'reviews_count': int(item.reviews_count) if item.reviews_count else None,
                    'latitude': float(item.latitude) if item.latitude else None,
                    'longitude': float(item.longitude) if item.longitude else None,
                    'category': item.category or '',
                })
            
            # Supabase'e upsert et
            result = supabase_service.upsert_map_data(formatted_data)
            if result.get('success'):
                success_count += result.get('upserted_count', 0)
            
            total_processed += len(formatted_data)
            logger.info(f"Django-Supabase batch {i//batch_size + 1} işlendi: {len(formatted_data)} kayıt")
        
        result = {
            "success": True,
            "total_processed": total_processed,
            "success_count": success_count,
            "message": f"{success_count}/{total_processed} kayıt Supabase'e senkronize edildi"
        }
        
        logger.info(f"Django-Supabase senkronizasyonu tamamlandı: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Django-Supabase senkronizasyon task'ında hata: {e}")
        return {"success": False, "error": str(e)}
