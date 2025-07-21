"""
Celery konfigürasyonu
Otomatik senkronizasyon ve background task'lar için
"""

import os
from celery import Celery
from celery.schedules import crontab

# Django settings modülünü belirle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')

# Celery app oluştur
app = Celery('mapscraper_project')

# Django settings'ten konfigürasyon al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django app'lerinden task'ları otomatik keşfet
app.autodiscover_tasks()

# Periyodik task'lar
app.conf.beat_schedule = {
    # Her 10 dakikada bir otomatik senkronizasyon
    'auto-sync-every-10-minutes': {
        'task': 'mapscraper.tasks.auto_sync_task',
        'schedule': crontab(minute='*/10'),  # Her 10 dakika
    },
    # Her gece saat 2'de eski job'ları temizle
    'cleanup-old-jobs-daily': {
        'task': 'mapscraper.tasks.cleanup_old_jobs_task',
        'schedule': crontab(hour=2, minute=0),  # Her gece 02:00
    },
    # Her 30 dakikada bir Supabase bağlantısını test et
    'test-supabase-connection': {
        'task': 'mapscraper.tasks.test_supabase_connection_task',
        'schedule': crontab(minute='*/30'),  # Her 30 dakika
    },
}

app.conf.timezone = 'Europe/Istanbul'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
