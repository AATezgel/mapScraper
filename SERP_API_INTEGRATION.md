# SERP API Entegrasyonu - Map Scraper

## 🎯 Yapılan Değişiklikler

### 1. N8N Workflow'undan SERP API'ye Geçiş

**Önceki Sistem:**
- N8N webhook'a istek gönderiliyordu
- N8N, SERP API'yi çağırıp Supabase'e veri kaydediyordu
- Django, N8N'den gelen verileri dinliyordu

**Yeni Sistem:**
- Django direkt SERP API'yi çağırıyor
- Veriler direkt lokal SQLite veritabanına kaydediliyor
- N8N middleware'i kaldırıldı
- Supabase bağımlılığı tamamen kaldırıldı

### 2. Değiştirilen Dosyalar

#### `mapscraper/views.py`

**`trigger_n8n_api()` Fonksiyonu:**
```python
# ❌ Eskiden:
- N8N webhook'una GET isteği gönderiyordu
- Job oluşturup N8N'den sonuç bekliyordu

# ✅ Şimdi:
- SERP API'ye direkt GET isteği gönderiyor
- Gelen verileri parse edip SQLite'a kaydediyor
- Update/Create işlemini otomatik yapıyor
```

**`test_n8n_webhook()` → `test_serp_api()`:**
```python
# ❌ Eskiden:
- N8N webhook bağlantısını test ediyordu

# ✅ Şimdi:
- SERP API bağlantısını test ediyor
- Örnek bir query ile sonuç dönüyor
```

**`receive_n8n_data()` Fonksiyonu:**
```python
# ❌ Tamamen kaldırıldı
- N8N'den webhook callback'i bekliyordu
```

**`settings_view()` Fonksiyonu:**
```python
# ❌ Eskiden:
- webhook_url (N8N webhook URL'i)

# ✅ Şimdi:
- serp_api_key (SERP API anahtarı)
```

#### `mapscraper/urls.py`

```python
# ❌ Kaldırılan:
path('api/receive-n8n-data/', views.receive_n8n_data, name='receive_n8n_data')
path('api/test-n8n-webhook/', views.test_n8n_webhook, name='test_n8n_webhook')

# ✅ Eklenen:
path('api/test-serp-api/', views.test_n8n_webhook, name='test_serp_api')
```

#### `templates/settings.html`

```html
<!-- ❌ Kaldırılan: -->
<input name="webhook_url" placeholder="N8N Webhook URL">

<!-- ✅ Eklenen: -->
<input name="serp_api_key" placeholder="Your SERP API Key">
```

### 3. SERP API Parametreleri

```python
params = {
    'engine': 'google_maps',      # Google Maps'ten veri çeker
    'q': query,                     # Arama sorgusu (örn: "restaurant istanbul")
    'type': 'search',               # Arama tipi
    'api_key': serp_api_key        # SERP API anahtarı
}
```

**API Endpoint:**
```
https://serpapi.com/search.json
```

### 4. Veri Akışı

**Yeni Akış:**
```
1. Kullanıcı query girer (örn: "restaurant istanbul")
2. Django backend trigger_n8n_api() fonksiyonunu çağırır
3. SERP API'ye istek gönderilir
4. SERP API Google Maps'ten verileri çeker
5. Django gelen JSON'u parse eder
6. Her sonuç için MapData modeline kaydedilir
7. Aynı isimli kayıt varsa güncellenir (update_or_create)
8. Başarı mesajı döner
```

**Kaydedilen Veriler:**
- `name` (title)
- `address`
- `phone`
- `rating`
- `category` (type)
- `website`
- `latitude` (gps_coordinates.latitude)
- `longitude` (gps_coordinates.longitude)

## 🚀 Kullanım

### 1. Ayarları Yapılandırma

1. `http://localhost:8001/settings/` adresine gidin
2. "SERP API Key" alanına API anahtarınızı girin
3. Kaydet butonuna basın

**SERP API Key Alma:**
- https://serpapi.com/ adresine gidin
- Ücretsiz hesap açın
- Dashboard'dan API key'inizi kopyalayın

### 2. Map Scraper Kullanımı

1. `http://localhost:8001/map-scraper/` adresine gidin
2. Arama kutusuna sorgunuzu girin (örn: "cafe kadıköy")
3. "Ara" butonuna basın
4. Veriler otomatik olarak çekilip veritabanına kaydedilir
5. Haritada işaretleyiciler olarak görünür

### 3. Test Script'i Çalıştırma

```bash
cd /Users/aatezgel/Projects/django-test/scraperApp/mapScraper
python3 test_serp_integration.py
```

**Test Script:**
- SERP API bağlantısını test eder
- "restaurant istanbul" sorgusuyla örnek veri çeker
- Verileri veritabanına kaydeder
- İstatistikleri gösterir

## 📊 API Response Örneği

**SERP API Response:**
```json
{
  "local_results": [
    {
      "title": "Cafe Moda",
      "address": "Kadıköy, Istanbul",
      "phone": "+90 216 123 4567",
      "rating": 4.5,
      "type": "Cafe",
      "website": "https://example.com",
      "gps_coordinates": {
        "latitude": 40.9876,
        "longitude": 29.0234
      }
    }
  ]
}
```

## 🎨 Avantajlar

### ✅ Yeni Sistem Avantajları:

1. **Daha Hızlı:** N8N middleware'i olmadan direkt SERP API çağrısı
2. **Daha Basit:** Tek bir istek-cevap döngüsü
3. **Daha Güvenilir:** Daha az bileşen = daha az hata noktası
4. **Lokal:** Tüm veriler SQLite'ta, Supabase gerekmez
5. **Offline:** Internet olmadan da mevcut verilerle çalışır
6. **Bakımı Kolay:** Tek bir kod tabanı, daha az karmaşıklık

### ❌ Eski Sistemin Sorunları:

1. N8N'e bağımlılık
2. Supabase'e bağımlılık
3. Çoklu network isteği (Django → N8N → SERP API → Supabase)
4. Webhook callback karmaşıklığı
5. Senkronizasyon problemleri

## 🔧 Geliştirici Notları

### Önemli Değişiklikler:

1. **Job Status Management:**
   - Job oluşturulur (`status='running'`)
   - SERP API başarılıysa `status='completed'`
   - Hata varsa `status='failed'` ve `error_message` set edilir

2. **Update or Create:**
   ```python
   obj, created = MapData.objects.update_or_create(
       name=map_data['name'],
       defaults=map_data
   )
   ```
   - Aynı isimli kayıt varsa günceller
   - Yoksa yeni kayıt oluşturur

3. **Error Handling:**
   - `requests.exceptions.Timeout` - 30 saniye timeout
   - `response.status_code != 200` - SERP API hataları
   - Generic `Exception` - Beklenmeyen hatalar

## 📝 TODO (Gelecek Geliştirmeler)

- [ ] SERP API quota kontrolü (aylık limit tracking)
- [ ] Batch processing (birden fazla query aynı anda)
- [ ] Cache mekanizması (aynı query tekrar çağrılmasın)
- [ ] Rate limiting (SERP API limit aşımını önle)
- [ ] Advanced filtering (kategori, rating, vs.)
- [ ] Export to CSV/Excel
- [ ] API response logging (debugging için)

## 🐛 Troubleshooting

### Problem: "SERP API hatası: 401"
**Çözüm:** API key'iniz geçersiz. Settings sayfasından doğru key'i girin.

### Problem: "SERP API zaman aşımına uğradı"
**Çözüm:** Internet bağlantınızı kontrol edin veya timeout süresini artırın.

### Problem: "Sonuç bulunamadı"
**Çözüm:** Query'nizi değiştirin veya daha genel bir arama yapın.

### Problem: Import errors (django, requests)
**Çözüm:** Bu linting hataları, kod çalışacaktır. Python environment doğru ayarlanmış.

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. `test_serp_integration.py` script'ini çalıştırın
2. Console output'unu kontrol edin
3. Database'de kayıtları kontrol edin: `MapData.objects.all()`
