# 🚀 Django Map Scraper - Production Deployment Rehberi

## 📋 İçindekiler
1. [Render.com ile Deploy (ÖNERİLEN - ÜCRETSİZ)](#rendercom-ile-deploy)
2. [Railway.app ile Deploy (Alternatif)](#railwayapp-ile-deploy)
3. [DigitalOcean ile Deploy (Profesyonel)](#digitalocean-ile-deploy)
4. [Production Ayarları](#production-ayarları)

---

## 🎯 Render.com ile Deploy (ÖNERİLEN - ÜCRETSİZ)

Render.com, Django uygulamaları için en kolay ve ücretsiz deployment seçeneğidir.

### 1. Gerekli Dosyaları Oluşturun

#### `requirements.txt` Güncelleme
```bash
cd /Users/aatezgel/Projects/django-test/scraperApp/mapScraper
pip freeze > requirements.txt
```

Aşağıdaki paketlerin olduğundan emin olun:
```
Django==5.2.4
djangorestframework==3.15.2
requests==2.32.3
redis==5.0.0
celery==5.3.1
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
```

#### `build.sh` Dosyası Oluştur (Render için)
```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
```

Dosyayı executable yapın:
```bash
chmod +x build.sh
```

#### `render.yaml` Dosyası Oluştur
```yaml
services:
  - type: web
    name: map-scraper
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn mapscraper_project.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: .onrender.com
```

### 2. `settings.py` Production Ayarları

`mapscraper_project/settings.py` dosyasını güncelleyin:

```python
import os
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-dev-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database
# SQLite için (development)
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Production için PostgreSQL (Render otomatik sağlar)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE'),
            'USER': os.environ.get('PGUSER'),
            'PASSWORD': os.environ.get('PGPASSWORD'),
            'HOST': os.environ.get('PGHOST'),
            'PORT': os.environ.get('PGPORT', 5432),
        }
    }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise için (static dosya servisi)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Bu satırı ekleyin
    # ... diğer middleware'ler
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. Render.com'da Deploy

1. **GitHub'a Push Edin:**
```bash
cd /Users/aatezgel/Projects/django-test/scraperApp
git add .
git commit -m "Production deployment hazırlıkları"
git push origin main
```

2. **Render.com Hesabı:**
   - https://render.com adresine gidin
   - GitHub ile giriş yapın
   - "New +" → "Web Service" seçin

3. **Repository Bağlayın:**
   - GitHub repository'nizi seçin
   - Branch: `main`
   - Root Directory: `scraperApp/mapScraper`

4. **Ayarları Yapın:**
   - **Name:** `map-scraper`
   - **Environment:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn mapscraper_project.wsgi:application`
   - **Plan:** Free

5. **Environment Variables Ekleyin:**
   - `SECRET_KEY`: (otomatik generate edilecek)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com`
   - `SERP_API_KEY`: `your-serp-api-key`

6. **PostgreSQL Database Ekleyin:**
   - Dashboard'da "New +" → "PostgreSQL"
   - Database name: `map_scraper_db`
   - Free plan seçin
   - Web Service'e database'i bağlayın (otomatik environment variables ekler)

7. **Deploy Edin:**
   - "Create Web Service" butonuna tıklayın
   - Deploy süreci başlayacak (5-10 dakika)

8. **URL'nizi Alın:**
   - Deploy tamamlandığında: `https://your-app-name.onrender.com`

---

## 🚂 Railway.app ile Deploy (Alternatif)

Railway de ücretsiz başlangıç planı sunar ve çok kolaydır.

### 1. Railway Kurulumu

```bash
npm install -g @railway/cli
railway login
```

### 2. Procfile Oluştur

```
web: gunicorn mapscraper_project.wsgi:application --log-file -
```

### 3. railway.json Oluştur

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate"
  },
  "deploy": {
    "startCommand": "gunicorn mapscraper_project.wsgi:application",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 4. Deploy Komutu

```bash
cd /Users/aatezgel/Projects/django-test/scraperApp/mapScraper
railway init
railway up
```

Railway otomatik olarak:
- PostgreSQL database oluşturur
- Environment variables ayarlar
- Domain sağlar

---

## 🌊 DigitalOcean ile Deploy (Profesyonel)

Daha fazla kontrol istiyorsanız DigitalOcean App Platform kullanabilirsiniz.

### 1. .do/app.yaml Oluştur

```yaml
name: map-scraper
services:
- name: web
  github:
    repo: AATezgel/mapScraper
    branch: main
    deploy_on_push: true
  build_command: |
    pip install -r requirements.txt
    python manage.py collectstatic --noinput
    python manage.py migrate
  run_command: gunicorn mapscraper_project.wsgi:application
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    type: SECRET
  - key: ALLOWED_HOSTS
    value: ${APP_DOMAIN}
databases:
- name: db
  engine: PG
  production: false
```

### 2. DigitalOcean Deploy

1. https://cloud.digitalocean.com/apps
2. "Create App" → "GitHub" seçin
3. Repository seçin
4. `.do/app.yaml` dosyası otomatik algılanacak
5. "Launch App" tıklayın

**Maliyet:** ~$5/ay (Basic plan)

---

## ⚙️ Production Ayarları

### 1. Güvenlik Ayarları

`settings.py` dosyasına ekleyin:

```python
if not DEBUG:
    # HTTPS Zorunlu
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # X-Frame-Options
    X_FRAME_OPTIONS = 'DENY'
    
    # Content Type
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # XSS Protection
    SECURE_BROWSER_XSS_FILTER = True
```

### 2. Static Files için WhiteNoise

```bash
pip install whitenoise
```

`settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 2. sırada olmalı
    # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. Logging Ayarları

`settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### 4. Environment Variables

Hassas bilgileri `.env` dosyasında tutun (production'da platform sağlayacak):

```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SERP_API_KEY=your-serp-api-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

Python-decouple kullanın:
```bash
pip install python-decouple
```

`settings.py`:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

---

## 📝 Deployment Checklist

Deploy etmeden önce kontrol edin:

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` güvenli ve benzersiz
- [ ] `ALLOWED_HOSTS` doğru domain'leri içeriyor
- [ ] Database production ayarları yapıldı
- [ ] Static files toplanıyor (`collectstatic`)
- [ ] Requirements.txt güncel
- [ ] `.gitignore` dosyası `db.sqlite3`, `*.pyc`, `__pycache__` içeriyor
- [ ] HTTPS zorunlu
- [ ] Environment variables ayarlandı
- [ ] Migrations çalışıyor
- [ ] Superuser oluşturuldu

---

## 🔧 Deploy Sonrası İşlemler

### 1. Superuser Oluşturma

Render/Railway/DigitalOcean console'da:
```bash
python manage.py createsuperuser
```

### 2. Database Migration

Otomatik çalışmazsa manuel:
```bash
python manage.py migrate
```

### 3. Static Files

```bash
python manage.py collectstatic --noinput
```

### 4. Test Etme

- Ana sayfa: `https://your-app.onrender.com/`
- Admin: `https://your-app.onrender.com/admin/`
- Login: `https://your-app.onrender.com/login/`
- Map Scraper: `https://your-app.onrender.com/map-scraper/`

---

## 🐛 Troubleshooting

### Hata: "DisallowedHost"
**Çözüm:** `ALLOWED_HOSTS` environment variable'ına domain ekleyin

### Hata: "Static files not found"
**Çözüm:** 
```bash
python manage.py collectstatic --noinput
```
WhiteNoise middleware'i kontrol edin

### Hata: "Database connection failed"
**Çözüm:** Database environment variables'ları kontrol edin

### Hata: "Application timeout"
**Çözüm:** Gunicorn timeout artırın:
```bash
gunicorn mapscraper_project.wsgi:application --timeout 120
```

---

## 📊 Monitoring & Logs

### Render Logs
```bash
# Dashboard'dan "Logs" tab'ına gidin
# veya CLI:
render logs -s your-service-name
```

### Railway Logs
```bash
railway logs
```

### DigitalOcean Logs
Console → App → Runtime Logs

---

## 💰 Maliyet Karşılaştırması

| Platform | Ücretsiz Plan | Ücretli Plan | Database | SSL |
|----------|---------------|--------------|----------|-----|
| **Render** | ✅ 750 saat/ay | $7/ay | ✅ Ücretsiz PostgreSQL | ✅ Ücretsiz |
| **Railway** | ✅ $5 kredi/ay | $5+ kullanıma göre | ✅ Ücretsiz PostgreSQL | ✅ Ücretsiz |
| **DigitalOcean** | ❌ | $5/ay | $7/ay | ✅ Ücretsiz |
| **Heroku** | ❌ (kaldırıldı) | $7/ay | $5/ay | ✅ Ücretsiz |

**Öneri:** Başlangıç için **Render.com** en iyi seçenek (ücretsiz ve kolay).

---

## 🎯 Hızlı Başlangıç (Render.com)

```bash
# 1. Dosyaları hazırla
cd /Users/aatezgel/Projects/django-test/scraperApp/mapScraper

# 2. Build script oluştur
cat > build.sh << 'EOF'
#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
EOF

chmod +x build.sh

# 3. Git'e ekle
git add .
git commit -m "Production deployment hazırlıkları"
git push origin main

# 4. Render.com'a git ve yukarıdaki adımları takip et
```

Deploy linkiniz: `https://your-app-name.onrender.com` 🚀

---

## 📞 Destek

Sorun yaşarsanız:
1. Render/Railway/DigitalOcean logs kontrol edin
2. Settings.py dosyasını kontrol edin
3. Environment variables doğru mu kontrol edin
4. Database bağlantısını test edin
