"""
Celery task'ları
Otomatik temizleme ve background işlemler için
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import ScrapingJob

logger = logging.getLogger(__name__)

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
