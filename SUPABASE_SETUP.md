# Supabase Entegrasyonu ve Otomatik Senkronizasyon

Bu Django uygulaması artık **Supabase PostgreSQL** veritabanı kullanacak şekilde yapılandırıldı ve scraping verilerini otomatik olarak senkronize edebilir.

## 🚀 Özellikler

- ✅ **Supabase PostgreSQL** veritabanı entegrasyonu
- ✅ **Google Sheets** otomatik senkronizasyonu  
- ✅ **N8N** workflow entegrasyonu
- ✅ **Celery** ile background task'lar
- ✅ **Redis** ile periyodik senkronizasyon
- ✅ **Realtime** veri güncellemeleri
- ✅ **Manuel senkronizasyon** özellikleri

## 📋 Kurulum Adımları

### 1. Gereksinimler

```bash
# Tüm paketleri kur
pip install -r requirements.txt
```

### 2. Supabase Kurulumu

1. [Supabase](https://supabase.com) hesabı oluşturun
2. Yeni bir proje oluşturun
3. **Settings > API** bölümünden şu bilgileri alın:
   - Project URL
   - API Keys (anon/public key)
4. **Settings > Database** bölümünden PostgreSQL connection string'ini alın

### 3. .env Dosyası Konfigürasyonu

`.env` dosyasındaki değerleri gerçek Supabase bilgilerinizle güncelleyin:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key-here

# Database Configuration (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres

# Redis ayarları (yerel Redis kullanıyorsanız)
REDIS_URL=redis://localhost:6379/0
```

### 4. Veritabanı Migrasyonları

```bash
# Django modellerini Supabase'e migrate et
python manage.py makemigrations
python manage.py migrate
```

### 5. Redis Kurulumu (Celery için)

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

## 🔧 Kullanım

### Manuel Test

```bash
# Supabase entegrasyonunu test et
python test_supabase_integration.py

# Manuel senkronizasyon komutu
python manage.py sync_supabase_data --source=both

# Sadece Google Sheets'ten senkronize et
python manage.py sync_supabase_data --source=google_sheets

# Dry run (sadece kontrol)
python manage.py sync_supabase_data --dry-run
```

### Otomatik Senkronizasyon (Celery)

**1. Celery Worker'ı Başlat:**
```bash
celery -A mapscraper_project worker --loglevel=info
```

**2. Celery Beat'i Başlat (Periyodik Task'lar):**
```bash
celery -A mapscraper_project beat --loglevel=info
```

**3. Her İkisini Birlikte Başlat:**
```bash
celery -A mapscraper_project worker --beat --loglevel=info
```

### Web Arayüzünden Kullanım

**Django Sunucusunu Başlat:**
```bash
python manage.py runserver
```

**Manuel Senkronizasyon API:**
```bash
# Google Sheets'ten senkronize et
curl -X POST http://localhost:8000/api/manual-sync-supabase/ \
  -H "Content-Type: application/json" \
  -d '{"source": "google_sheets"}'

# İstatistikleri al
curl http://localhost:8000/api/supabase-stats/
```

## 📊 Senkronizasyon Zamanlaması

Otomatik senkronizasyon periyotları:

- **Google Sheets Sync**: Her saat başında
- **Eski Job Temizleme**: Her gün saat 02:00'da
- **Manuel Tetikleme**: API endpoint'i ile

## 🔍 Veri Akışı

```
Google Sheets → Django → Supabase PostgreSQL
     ↓              ↓            ↓
   Parse         Process      Store
     ↓              ↓            ↓
 N8N Tasks    Background     Realtime
               Tasks         Updates
```

## 📁 Dosya Yapısı

```
mapscraper/
├── supabase_service.py      # Supabase entegrasyonu
├── tasks.py                 # Celery background tasks
├── google_sheets.py         # Google Sheets entegrasyonu
├── views.py                 # Web API endpoints
├── models.py                # Django modelleri
└── management/commands/
    └── sync_supabase_data.py # Senkronizasyon komutu
```

## 🛠️ Sorun Giderme

### Supabase Bağlantı Sorunları

```bash
# Test komutu
python test_supabase_integration.py
```

Hata alıyorsanız:
1. `.env` dosyasındaki Supabase bilgilerini kontrol edin
2. Supabase projesi aktif mi kontrol edin
3. Network bağlantısını kontrol edin

### Celery Sorunları

```bash
# Redis çalışıyor mu?
redis-cli ping  # PONG döndürmeli

# Celery worker durumu
celery -A mapscraper_project inspect active
```

### Migration Sorunları

```bash
# Reset migrations (dikkatli kullanın!)
python manage.py migrate mapscraper zero
python manage.py makemigrations mapscraper
python manage.py migrate
```

## 📈 İzleme ve Loglar

**Celery Task'larını İzleme:**
```bash
# Flower (web arayüzü)
pip install flower
celery -A mapscraper_project flower
# http://localhost:5555 adresine gidin
```

**Django Logları:**
Tüm senkronizasyon işlemleri Django loglarında görüntülenir.

## 🔄 Realtime Özellikler

Supabase realtime subscriptions kuruldu:
- Veri değişiklikleri otomatik algılanır
- Frontend'e push notification gönderilebilir
- WebSocket bağlantıları desteklenir

## 📝 API Endpoints

```
GET  /api/map-data/              # Harita verilerini al
GET  /api/supabase-stats/        # Senkronizasyon istatistikleri
POST /api/manual-sync-supabase/  # Manuel senkronizasyon
POST /api/sync-google-sheets/    # Google Sheets senkronizasyonu
```

## 📞 Destek

Sorun yaşıyorsanız:

1. `test_supabase_integration.py` dosyasını çalıştırın
2. `python manage.py check` komutu ile Django ayarlarını kontrol edin
3. Celery ve Redis servislerinin çalıştığından emin olun
4. `.env` dosyasındaki tüm değerlerin doğru olduğunu kontrol edin

---

**Not:** Bu dokümantasyon Django uygulamanızın Supabase ile tam entegrasyonu için gerekli tüm adımları içerir. Gerçek Supabase bilgilerinizi ekledikten sonra tüm özellikler aktif olacaktır.
