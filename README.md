# 🗺️ Django Map Scraper - SERP API Integration

Google Maps verilerini SERP API kullanarak çeken Django web uygulaması.

## 🚀 Hızlı Başlangıç

### Lokal Çalıştırma

```bash
# 1. Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Paketleri yükle
pip install -r requirements.txt

# 3. Database migration
python manage.py migrate

# 4. Superuser oluştur
python manage.py createsuperuser

# 5. Server'ı başlat
python manage.py runserver 8001
```

Uygulama: http://localhost:8001

## 📦 Production Deployment

### Render.com (ÜCRETSİZ)

1. **GitHub'a Push:**
```bash
git push origin main
```

2. **Render.com Setup:**
   - https://render.com adresine git
   - GitHub ile giriş yap
   - "New +" → "Web Service"
   - Repository seç: `AATezgel/mapScraper`
   - Root Directory: `scraperApp/mapScraper`

3. **Ayarlar:**
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn mapscraper_project.wsgi:application`
   - **Environment:** Python 3

4. **Environment Variables:**
   ```
   SECRET_KEY = (otomatik generate)
   DEBUG = False
   ALLOWED_HOSTS = .onrender.com
   SERP_API_KEY = your-api-key-here
   ```

5. **Database:**
   - "New +" → "PostgreSQL"
   - Free plan seç
   - Web Service'e bağla

6. **Deploy:**
   - "Create Web Service" tıkla
   - 5-10 dakika bekle

**Deploy URL:** `https://your-app-name.onrender.com`

## 📚 Detaylı Rehber

Detaylı deployment rehberi için: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 🔑 Özellikler

- ✅ Google Maps veri çekme (SERP API)
- ✅ SQLite/PostgreSQL database
- ✅ User authentication
- ✅ REST API endpoints
- ✅ Responsive dashboard
- ✅ Celery task queue (opsiyonel)
- ✅ Production-ready settings

## 🛠️ Teknolojiler

- Django 5.2.4
- Django REST Framework
- SERP API
- PostgreSQL (production)
- SQLite (development)
- Gunicorn
- WhiteNoise
- Celery + Redis (opsiyonel)

## 📝 API Key

SERP API key: `19b8cfa3a27fb5b568411275ca980abbba9cdc077b6a1ee93bf5c18ca556b397`

## 🔒 Güvenlik

Production ortamında:
- `DEBUG = False`
- Güvenli `SECRET_KEY`
- HTTPS zorunlu
- HSTS enabled
- XSS protection
- CSRF protection

## 📞 Destek

Sorun yaşarsanız `DEPLOYMENT_GUIDE.md` dosyasındaki troubleshooting bölümüne bakın.

---

**Made with ❤️ for easy Google Maps data scraping**
