from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
import json
import time
from .models import MapData, ScrapingJob
from .supabase_service import supabase_service

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('login')

@login_required
def dashboard_view(request):
    try:
        # Son işler
        recent_jobs = ScrapingJob.objects.filter(user=request.user).order_by('-created_at')[:10]
        total_jobs = ScrapingJob.objects.filter(user=request.user).count()
        
        # Son 24 saatteki işler
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(days=1)
        recent_24h_jobs = ScrapingJob.objects.filter(
            user=request.user, 
            created_at__gte=yesterday
        ).count()
        
        # Başarılı işler
        successful_jobs = ScrapingJob.objects.filter(
            user=request.user,
            status='completed'
        ).count()
        
        # Supabase bağlantı durumu ve veri sayısı
        supabase_connected = supabase_service.is_connected()
        supabase_count = 0
        django_count = 0  # Artık sadece Supabase kullanıyoruz
        category_stats = {}
        
        if supabase_connected:
            try:
                supabase_stats = supabase_service.get_sync_stats()
                supabase_count = supabase_stats.get('total_records', 0)
                django_count = supabase_count  # Sadece Supabase verisi
                
                # Kategori istatistikleri - Supabase'den al
                all_data = supabase_service.get_all_map_data()
                for item in all_data:
                    category = item.get('category')
                    if category:  # Boş kategorileri atla
                        category_stats[category] = category_stats.get(category, 0) + 1
                
                # En çok olan kategorileri sırala
                category_stats = dict(sorted(category_stats.items(), key=lambda x: x[1], reverse=True))
                
            except Exception as e:
                print(f"Supabase dashboard verileri alınırken hata: {e}")
                supabase_connected = False
        
        context = {
            'recent_jobs': recent_jobs,
            'total_jobs': total_jobs,
            'django_count': django_count,  # Artık Supabase verisi
            'supabase_count': supabase_count,
            'supabase_connected': supabase_connected,
            'recent_24h_jobs': recent_24h_jobs,
            'successful_jobs': successful_jobs,
            'category_stats': category_stats,
            'sync_diff': abs(django_count - supabase_count) if supabase_connected else 0,
        }
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        # Hata durumunda basit dashboard
        context = {
            'recent_jobs': [],
            'total_jobs': 0,
            'django_count': 0,
            'supabase_count': 0,
            'supabase_connected': False,
            'recent_24h_jobs': 0,
            'successful_jobs': 0,
            'category_stats': {},
            'sync_diff': 0,
            'error': str(e)
        }
        return render(request, 'dashboard.html', context)

@login_required
def map_scraper_view(request):
    # Supabase'den veri çekmeyi dene, başarısız olursa Django ORM kullan
    if supabase_service.is_connected():
        # Limit'i çok yüksek yap, tüm veriyi çek
        supabase_data = supabase_service.get_map_data(limit=10000)
        map_data = supabase_data if supabase_data else []
        
        # Eğer Supabase'den hiç veri gelmiyorsa Django ORM'e fallback
        if not map_data:
            map_data = list(MapData.objects.all()[:1000].values())
    else:
        map_data = list(MapData.objects.all()[:1000].values())
    
    jobs = ScrapingJob.objects.filter(user=request.user)[:10]
    context = {
        'map_data': map_data,
        'jobs': jobs,
        'supabase_connected': supabase_service.is_connected(),
    }
    return render(request, 'map_scraper.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@csrf_exempt
def trigger_n8n_api(request):
    try:
        from .models import Settings
        
        print(f"Request body: {request.body}")  # Debug için
        data = json.loads(request.body)
        query = data.get('query', '')
        
        # Webhook URL'ini ayarlardan al
        n8n_webhook_url = Settings.get_setting('webhook_url', 'https://notifyn8n.tezgel.com/webhook/90004c3a-f7d6-4030-ac04-539a5d38beb5')
        
        print(f"Query: {query}, Webhook URL: {n8n_webhook_url}")  # Debug için
        
        if not query or not n8n_webhook_url:
            return JsonResponse({'error': 'Query ve webhook URL gereklidir.'}, status=400)
        
        # Scraping job kaydet
        job = ScrapingJob.objects.create(
            user=request.user,
            query=query,
            n8n_webhook_url=n8n_webhook_url,
            status='running'
        )
        
        print(f"Job created with ID: {job.id}")  # Debug için
        
        # N8N webhook'u tetikle (GET request)
        payload = {
            'query': query,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        print(f"Sending payload to N8N: {payload}")  # Debug için
        
        # GET request olarak gönder
        response = requests.get(n8n_webhook_url, params=payload, timeout=30)
        
        print(f"N8N response status: {response.status_code}")  # Debug için
        print(f"N8N response text: {response.text}")  # Debug için
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'job_id': job.id,
                'message': 'N8N workflow tetiklendi.'
            })
        else:
            job.status = 'failed'
            job.error_message = f'N8N webhook hatası: {response.status_code} - {response.text}'
            job.save()
            return JsonResponse({'error': f'N8N webhook hatası: {response.status_code} - {response.text}'}, status=500)
            
    except Exception as e:
        print(f"Error in trigger_n8n_api: {str(e)}")  # Debug için
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def test_n8n_webhook(request):
    """N8N webhook bağlantısını test et"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        webhook_url = data.get('webhook_url', '')
        
        if not webhook_url:
            # Ayarlardan webhook URL'ini al
            webhook_url = Settings.get_setting('webhook_url')
            
        if not webhook_url:
            return JsonResponse({'error': 'Webhook URL bulunamadı.'}, status=400)
        
        # Test payload
        test_payload = {
            'test': True,
            'query': 'test query',
            'user_id': request.user.id,
            'timestamp': int(time.time())
        }
        
        print(f"Testing webhook URL: {webhook_url}")  # Debug için
        print(f"Test payload: {test_payload}")  # Debug için
        
        # GET request ile test et
        response = requests.get(webhook_url, params=test_payload, timeout=10)
        
        print(f"Test response status: {response.status_code}")  # Debug için
        print(f"Test response text: {response.text}")  # Debug için
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'N8N webhook başarıyla test edildi!',
                'status_code': response.status_code
            })
        elif response.status_code == 404:
            return JsonResponse({
                'error': 'N8N webhook bulunamadı. Workflow\'un çalıştığından ve webhook\'un aktif olduğundan emin olun.',
                'status_code': response.status_code,
                'hint': 'N8N\'de "Test workflow" butonuna tıklayıp tekrar deneyin.'
            }, status=404)
        else:
            return JsonResponse({
                'error': f'N8N webhook test edilemedi: {response.status_code}',
                'status_code': response.status_code,
                'response': response.text[:200]  # İlk 200 karakteri al
            }, status=500)
            
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'error': 'N8N sunucusuna bağlanılamadı. URL\'in doğru olduğundan emin olun.',
            'hint': 'N8N sunucusunun çalıştığını kontrol edin.'
        }, status=500)
    except requests.exceptions.Timeout:
        return JsonResponse({
            'error': 'N8N webhook zaman aşımına uğradı.',
            'hint': 'N8N sunucusu yavaş yanıt veriyor.'
        }, status=500)
    except Exception as e:
        print(f"Error in test_n8n_webhook: {str(e)}")  # Debug için
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@login_required
def get_map_data(request):
    try:
        # Sadece Supabase'den veri çek
        if supabase_service.is_connected():
            supabase_data = supabase_service.get_map_data(limit=50000)  # Çok yüksek limit
            if supabase_data:
                # created_at alanını kontrol et ve düzelt
                for item in supabase_data:
                    if 'created_at' not in item or not item['created_at']:
                        item['created_at'] = '2024-01-01T00:00:00Z'
                return JsonResponse({
                    'success': True,
                    'data': supabase_data, 
                    'source': 'supabase',
                    'count': len(supabase_data)
                })
        
        # Supabase bağlantısı yoksa boş döndür
        return JsonResponse({
            'success': False,
            'data': [],
            'source': 'none',
            'count': 0,
            'error': 'Supabase bağlantısı bulunamadı'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': [],
            'source': 'error',
            'count': 0
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def receive_n8n_data(request):
    """N8N'den gelen veriyi almak için endpoint"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        map_data_list = data.get('map_data', [])
        
        print(f"N8N'den gelen veri: {data}")  # Debug için
        
        # Job ID varsa job durumunu güncelle
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
                print(f"Job {job_id} tamamlandı olarak işaretlendi")
            except ScrapingJob.DoesNotExist:
                print(f"Job {job_id} bulunamadı")
        
        # Gelen veriyi kaydet - önce Supabase'e, sonra Django'ya
        saved_count = 0
        
        # Supabase'e kaydet
        if supabase_service.is_connected():
            supabase_result = supabase_service.upsert_map_data(map_data_list)
            if supabase_result.get('success'):
                saved_count = supabase_result.get('upserted_count', 0)
                print(f"Supabase'e {saved_count} veri kaydedildi")
        
        # Django ORM'e de kaydet (fallback ve senkronizasyon için)
        for item in map_data_list:
            try:
                obj, created = MapData.objects.update_or_create(
                    name=item.get('name'),
                    address=item.get('address'),
                    defaults={
                        'phone': item.get('phone'),
                        'website': item.get('website'),
                        'rating': float(item.get('rating')) if item.get('rating') else None,
                        'reviews_count': int(item.get('reviews_count')) if item.get('reviews_count') else None,
                        'latitude': float(item.get('latitude')) if item.get('latitude') else None,
                        'longitude': float(item.get('longitude')) if item.get('longitude') else None,
                        'category': item.get('category'),
                    }
                )
                if not supabase_service.is_connected():
                    saved_count += 1
                print(f"Django ORM'e veri kaydedildi: {item.get('name')}")
            except Exception as e:
                print(f"Django ORM'e veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True, 
            'message': f'{saved_count} veri başarıyla kaydedildi.',
            'saved_count': saved_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz JSON formatı'}, status=400)
    except Exception as e:
        print(f"Genel hata: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def test_n8n_webhook(request):
    """N8N webhook'u test etmek için endpoint"""
    try:
        data = json.loads(request.body)
        query = data.get('query', 'istanbul kafe')
        
        # Simüle edilmiş N8N response
        test_response = {
            "job_id": data.get('job_id'),
            "query": query,
            "map_data": [
                {
                    "name": f"Test Kafe 1 - {query}",
                    "address": "Test Adres 1, İstanbul",
                    "phone": "+90 212 123 45 67",
                    "website": "https://example.com",
                    "rating": 4.5,
                    "reviews_count": 100,
                    "latitude": 41.0082,
                    "longitude": 28.9784,
                    "category": "Kafe"
                },
                {
                    "name": f"Test Kafe 2 - {query}",
                    "address": "Test Adres 2, İstanbul", 
                    "phone": "+90 212 987 65 43",
                    "website": "https://example2.com",
                    "rating": 4.2,
                    "reviews_count": 85,
                    "latitude": 41.0092,
                    "longitude": 28.9794,
                    "category": "Kafe"
                }
            ]
        }
        
        # Django'ya direkt gönder (kendi kendine request yapmak yerine)
        from django.http import HttpRequest
        
        # Fake request objesi oluştur
        fake_request = HttpRequest()
        fake_request.method = 'POST'
        fake_request.META = {}
        fake_request._body = json.dumps(test_response).encode('utf-8')
        
        # receive_n8n_data fonksiyonunu direkt çağır
        result = receive_n8n_data(fake_request)
        
        return JsonResponse({
            'success': True,
            'message': 'Test verisi başarıyla işlendi',
            'result': json.loads(result.content.decode('utf-8'))
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_map_data(request):
    """Manuel olarak map data ekler (Supabase + Django)"""
    try:
        data = json.loads(request.body)
        
        # Gerekli alanları kontrol et
        if not data.get('name') or not data.get('address'):
            return JsonResponse({'error': 'İsim ve adres alanları gereklidir.'}, status=400)
        
        # Supabase'e ekle
        supabase_result = None
        if supabase_service.is_connected():
            supabase_result = supabase_service.create_map_data(data)
        
        # Django ORM'e ekle
        try:
            obj, created = MapData.objects.update_or_create(
                name=data.get('name'),
                address=data.get('address'),
                defaults={
                    'phone': data.get('phone', ''),
                    'website': data.get('website', ''),
                    'rating': float(data.get('rating')) if data.get('rating') else None,
                    'reviews_count': int(data.get('reviews_count')) if data.get('reviews_count') else None,
                    'latitude': float(data.get('latitude')) if data.get('latitude') else None,
                    'longitude': float(data.get('longitude')) if data.get('longitude') else None,
                    'category': data.get('category', ''),
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Veri {"oluşturuldu" if created else "güncellendi"}',
                'data': {
                    'id': obj.id,
                    'name': obj.name,
                    'address': obj.address
                },
                'supabase_connected': supabase_service.is_connected(),
                'supabase_saved': supabase_result is not None
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Veri kaydedilirken hata: {str(e)}'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz JSON formatı'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def manual_sync_supabase(request):
    """Manuel Supabase senkronizasyonu tetikler"""
    try:
        data = json.loads(request.body)
        source = data.get('source', 'both')  # 'supabase', 'django_orm', 'both'
        
        # Celery task'ını tetikle
        from .tasks import manual_sync_task
        task = manual_sync_task.delay(source=source)
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'message': f'Senkronizasyon başlatıldı (kaynak: {source})',
            'source': source
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@login_required
def get_supabase_stats(request):
    """Supabase detaylı istatistiklerini getir"""
    try:
        from .models import Settings
        from datetime import timedelta, datetime
        from collections import Counter
        import re
        
        # Supabase bağlantısı kontrolü
        if not supabase_service.is_connected():
            return JsonResponse({
                'success': False,
                'error': 'Supabase bağlantısı yok',
                'stats': {}
            })
        
        # Supabase'den tüm verileri al
        all_data = supabase_service.get_all_map_data()
        total_entries = len(all_data)
        
        # Temel istatistikler
        total_jobs = ScrapingJob.objects.count()
        recent_jobs = ScrapingJob.objects.order_by('-created_at')[:10]
        recent_24h_jobs = ScrapingJob.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=1)
        ).count()
        
        # Kategori dağılımı
        categories = Counter()
        ratings = []
        cities = Counter()
        rating_distribution = Counter()
        phone_providers = Counter()
        websites_domains = Counter()
        review_ranges = Counter()
        high_rated_places = []  # 4.5+ puanlı yerler
        business_types = Counter()  # İşletme türleri
        location_density = Counter()  # Koordinat yoğunluğu
        
        for item in all_data:
            # Kategori
            if item.get('category'):
                category = item['category']
                categories[category] += 1
                
                # İşletme türü analizi (kategori bazlı)
                if 'restaurant' in category.lower() or 'food' in category.lower():
                    business_types['Yemek & İçecek'] += 1
                elif 'coffee' in category.lower() or 'café' in category.lower():
                    business_types['Kahve & Kafe'] += 1
                elif 'shop' in category.lower() or 'store' in category.lower():
                    business_types['Mağaza & Alışveriş'] += 1
                elif 'health' in category.lower() or 'medical' in category.lower():
                    business_types['Sağlık & Tıp'] += 1
                elif 'beauty' in category.lower() or 'salon' in category.lower():
                    business_types['Güzellik & Bakım'] += 1
                elif 'hotel' in category.lower() or 'lodging' in category.lower():
                    business_types['Konaklama'] += 1
                elif 'gas' in category.lower() or 'station' in category.lower():
                    business_types['Yakıt & Servis'] += 1
                else:
                    business_types['Diğer'] += 1
            
            # Rating
            if item.get('rating'):
                rating = float(item['rating'])
                ratings.append(rating)
                
                # Rating aralığı
                if rating >= 4.5:
                    rating_distribution['4.5+ Mükemmel'] += 1
                    high_rated_places.append(item.get('name', 'İsimsiz'))
                elif rating >= 4.0:
                    rating_distribution['4.0-4.4 Çok İyi'] += 1
                elif rating >= 3.5:
                    rating_distribution['3.5-3.9 İyi'] += 1
                elif rating >= 3.0:
                    rating_distribution['3.0-3.4 Orta'] += 1
                else:
                    rating_distribution['3.0 Altı Zayıf'] += 1
            
            # Review sayısı analizi
            if item.get('reviews_count'):
                reviews = int(item['reviews_count'])
                if reviews >= 1000:
                    review_ranges['1000+ Çok Popüler'] += 1
                elif reviews >= 500:
                    review_ranges['500-999 Popüler'] += 1
                elif reviews >= 100:
                    review_ranges['100-499 Orta'] += 1
                elif reviews >= 10:
                    review_ranges['10-99 Az'] += 1
                else:
                    review_ranges['10 Altı Yeni'] += 1
            
            # Şehir (adres'ten çıkar)
            if item.get('address'):
                address = item['address']
                # Türkiye şehir isimlerini yakala (daha kapsamlı)
                city_patterns = [
                    r'/([A-ZÜĞŞIÖÇ][a-züğşiöç]{2,})/İstanbul',
                    r'/([A-ZÜĞŞIÖÇ][a-züğşiöç]{2,})/Ankara',
                    r'/([A-ZÜĞŞIÖÇ][a-züğşiöç]{2,})/İzmir',
                    r'/([A-ZÜĞŞIÖÇ][a-züğşiöç]{2,})/Bursa',
                    r'/([A-ZÜĞŞIÖÇ][a-züğşiöç]{2,})/Antalya',
                    r'/([A-ZÜĞŞIÖÇ][a-züğşiöç]{2,})/Adana',
                    r'/([A-ZÜĞŞIÖÇ][a-züğşiöç]{3,})/',
                    r'([A-ZÜĞŞIÖÇ][a-züğşiöç]{2,})\s+\d{5}',
                    r'([A-ZÜĞŞIÖÇ][a-züğşiöç]{2,}),\s*Türkiye'
                ]
                for pattern in city_patterns:
                    match = re.search(pattern, address)
                    if match:
                        city = match.group(1)
                        if len(city) >= 3 and city not in ['Mah', 'Cad', 'Sok', 'No']:
                            cities[city] += 1
                        break
            
            # Telefon sağlayıcısı analizi
            if item.get('phone'):
                phone = item['phone']
                if '0532' in phone or '0533' in phone or '0534' in phone:
                    phone_providers['Vodafone'] += 1
                elif '0542' in phone or '0543' in phone or '0544' in phone:
                    phone_providers['Turkcell'] += 1
                elif '0505' in phone or '0506' in phone or '0507' in phone:
                    phone_providers['Türk Telekom'] += 1
                elif '0530' in phone or '0531' in phone:
                    phone_providers['Avea'] += 1
                else:
                    phone_providers['Diğer/Sabit'] += 1
            
            # Website domain analizi
            if item.get('website'):
                website = item['website']
                if 'instagram.com' in website:
                    websites_domains['Instagram'] += 1
                elif 'facebook.com' in website:
                    websites_domains['Facebook'] += 1
                elif 'google.com' in website:
                    websites_domains['Google My Business'] += 1
                elif any(domain in website for domain in ['.com.tr', '.com', '.net', '.org']):
                    websites_domains['Kendi Websitesi'] += 1
                else:
                    websites_domains['Diğer'] += 1
            
            # Konum yoğunluğu (koordinat bazlı)
            if item.get('latitude') and item.get('longitude'):
                lat = round(float(item['latitude']), 2)
                lon = round(float(item['longitude']), 2)
                location_key = f"{lat},{lon}"
                location_density[location_key] += 1
        
        # Job query istatistikleri
        job_queries = Counter()
        for job in recent_jobs:
            if job.query:
                # Query'den anahtar kelime çıkar
                words = job.query.lower().split()
                for word in words:
                    if len(word) > 3:  # Kısa kelimeleri filtrele
                        job_queries[word] += 1
        
        # Ortalama rating
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        max_rating = max(ratings) if ratings else 0
        min_rating = min(ratings) if ratings else 0
        
        # En yoğun lokasyonlar
        top_dense_locations = dict(location_density.most_common(5))
        
        # Data kalite skorları
        data_quality_score = 0
        quality_factors = {
            'rating': len([x for x in all_data if x.get('rating')]),
            'phone': len([x for x in all_data if x.get('phone')]),
            'website': len([x for x in all_data if x.get('website')]),
            'category': len([x for x in all_data if x.get('category')]),
            'address': len([x for x in all_data if x.get('address')])
        }
        
        if total_entries > 0:
            quality_percentage = (sum(quality_factors.values()) / (total_entries * 5)) * 100
            data_quality_score = round(quality_percentage, 1)
        
        # Sync durumu
        django_count = 0  # Artık sadece Supabase kullanıyoruz
        sync_diff = 0
        sync_health = 'excellent' if data_quality_score > 80 else 'good' if data_quality_score > 60 else 'fair'
        
        # En son sync zamanı
        last_sync = recent_jobs[0].created_at if recent_jobs else None
        
        stats = {
            'total_entries': total_entries,
            'supabase_entries': total_entries,
            'django_entries': django_count,
            'total_jobs': total_jobs,
            'recent_jobs_count': recent_24h_jobs,
            'sync_diff': sync_diff,
            'sync_health': sync_health,
            'avg_rating': round(avg_rating, 2),
            'max_rating': max_rating,
            'min_rating': min_rating,
            'total_ratings': len(ratings),
            'categories': dict(categories.most_common(20)),  # Top 20 kategori
            'business_types': dict(business_types.most_common()),  # İşletme türleri
            'cities': dict(cities.most_common(15)),  # Top 15 şehir
            'rating_distribution': dict(rating_distribution.most_common()),
            'review_ranges': dict(review_ranges.most_common()),
            'phone_providers': dict(phone_providers.most_common()),
            'website_domains': dict(websites_domains.most_common()),
            'job_queries': dict(job_queries.most_common(15)),  # Top 15 arama
            'last_sync': last_sync.isoformat() if last_sync else None,
            'high_rated_count': len([r for r in ratings if r >= 4.5]),
            'top_dense_locations': top_dense_locations,
            'data_quality_score': data_quality_score,
            'data_quality': quality_factors,
            'data_completeness': {
                'rating_pct': round((quality_factors['rating'] / total_entries) * 100, 1) if total_entries > 0 else 0,
                'phone_pct': round((quality_factors['phone'] / total_entries) * 100, 1) if total_entries > 0 else 0,
                'website_pct': round((quality_factors['website'] / total_entries) * 100, 1) if total_entries > 0 else 0,
                'category_pct': round((quality_factors['category'] / total_entries) * 100, 1) if total_entries > 0 else 0,
                'address_pct': round((quality_factors['address'] / total_entries) * 100, 1) if total_entries > 0 else 0,
            }
        }
        
        return JsonResponse({
            'success': True,
            'connected': True,
            'stats': stats,
            'message': f'Toplam {total_entries} veri analiz edildi'
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'stats': {}
        }, status=500)

@login_required
def settings_view(request):
    """Ayarlar sayfası"""
    from .models import Settings
    
    if request.method == 'POST':
        # Ayarları kaydet
        webhook_url = request.POST.get('webhook_url', '')
        auto_refresh = request.POST.get('auto_refresh', 'off') == 'on'
        
        # Sosyal medya webhook URL'leri
        instagram_webhook_url = request.POST.get('instagram_webhook_url', '')
        facebook_webhook_url = request.POST.get('facebook_webhook_url', '')
        twitter_webhook_url = request.POST.get('twitter_webhook_url', '')
        linkedin_webhook_url = request.POST.get('linkedin_webhook_url', '')
        tiktok_webhook_url = request.POST.get('tiktok_webhook_url', '')
        
        Settings.set_setting('webhook_url', webhook_url, 'N8N Map Webhook URL')
        Settings.set_setting('auto_refresh', '1' if auto_refresh else '0', 'Otomatik yenileme açık/kapalı')
        
        # Sosyal medya webhook URL'lerini kaydet
        Settings.set_setting('instagram_webhook_url', instagram_webhook_url, 'Instagram N8N Webhook URL')
        Settings.set_setting('facebook_webhook_url', facebook_webhook_url, 'Facebook N8N Webhook URL')
        Settings.set_setting('twitter_webhook_url', twitter_webhook_url, 'Twitter N8N Webhook URL')
        Settings.set_setting('linkedin_webhook_url', linkedin_webhook_url, 'LinkedIn N8N Webhook URL')
        Settings.set_setting('tiktok_webhook_url', tiktok_webhook_url, 'TikTok N8N Webhook URL')
        
        messages.success(request, 'Ayarlar başarıyla kaydedildi!')
        return redirect('settings')
    
    # Mevcut ayarları al
    webhook_url = Settings.get_setting('webhook_url', 'https://notifyn8n.tezgel.com/webhook/90004c3a-f7d6-4030-ac04-539a5d38beb5')
    auto_refresh = Settings.get_setting('auto_refresh', '0') == '1'
    
    # Sosyal medya webhook URL'leri
    instagram_webhook_url = Settings.get_setting('instagram_webhook_url', 'https://notifyn8n.tezgel.com/webhook/instagram-scraper')
    facebook_webhook_url = Settings.get_setting('facebook_webhook_url', 'https://notifyn8n.tezgel.com/webhook/facebook-scraper')
    twitter_webhook_url = Settings.get_setting('twitter_webhook_url', 'https://notifyn8n.tezgel.com/webhook/twitter-scraper')
    linkedin_webhook_url = Settings.get_setting('linkedin_webhook_url', 'https://notifyn8n.tezgel.com/webhook/linkedin-scraper')
    tiktok_webhook_url = Settings.get_setting('tiktok_webhook_url', 'https://notifyn8n.tezgel.com/webhook/tiktok-scraper')
    
    import django
    context = {
        'django_version': django.get_version(),
        'supabase_connected': supabase_service.is_connected(),
        'webhook_url': webhook_url,
        'auto_refresh': auto_refresh,
        'instagram_webhook_url': instagram_webhook_url,
        'facebook_webhook_url': facebook_webhook_url,
        'twitter_webhook_url': twitter_webhook_url,
        'linkedin_webhook_url': linkedin_webhook_url,
        'tiktok_webhook_url': tiktok_webhook_url,
    }
    return render(request, 'settings.html', context)

# Multi-platform scraper views
@login_required
def instagram_scraper_view(request):
    """Instagram Scraper sayfası"""
    # Supabase'den Instagram verilerini çek
    instagram_data = supabase_service.get_instagram_data(limit=50)
    
    # Eğer Supabase'den veri gelmezse Django ORM'den fallback
    if not instagram_data:
        try:
            from .models import InstagramData
            instagram_data = list(InstagramData.objects.all()[:50].values())
        except Exception as e:
            print(f"Instagram Django ORM'den veri alınamadı: {e}")
            instagram_data = []
    
    context = {
        'instagram_data': instagram_data,
        'supabase_connected': supabase_service.is_connected(),
    }
    return render(request, 'instagram_scraper.html', context)

@login_required
def facebook_scraper_view(request):
    """Facebook Scraper sayfası"""
    # Supabase'den Facebook verilerini çek
    facebook_data = supabase_service.get_facebook_data(limit=50)
    
    # Eğer Supabase'den veri gelmezse Django ORM'den fallback
    if not facebook_data:
        try:
            from .models import FacebookData
            facebook_data = list(FacebookData.objects.all()[:50].values())
        except:
            facebook_data = []
    
    context = {
        'facebook_data': facebook_data,
        'supabase_connected': supabase_service.is_connected(),
    }
    return render(request, 'facebook_scraper.html', context)

@login_required
def twitter_scraper_view(request):
    """Twitter Scraper sayfası"""
    # Supabase'den Twitter verilerini çek
    twitter_data = supabase_service.get_twitter_data(limit=50)
    
    # Eğer Supabase'den veri gelmezse Django ORM'den fallback
    if not twitter_data:
        try:
            from .models import TwitterData
            twitter_data = list(TwitterData.objects.all()[:50].values())
        except:
            twitter_data = []
    
    context = {
        'twitter_data': twitter_data,
        'supabase_connected': supabase_service.is_connected(),
    }
    return render(request, 'twitter_scraper.html', context)

@login_required
def linkedin_scraper_view(request):
    """LinkedIn Scraper sayfası"""
    # Supabase'den LinkedIn verilerini çek
    linkedin_data = supabase_service.get_linkedin_data(limit=50)
    
    # Eğer Supabase'den veri gelmezse Django ORM'den fallback
    if not linkedin_data:
        try:
            from .models import LinkedInData
            linkedin_data = list(LinkedInData.objects.all()[:50].values())
        except:
            linkedin_data = []
    
    context = {
        'linkedin_data': linkedin_data,
        'supabase_connected': supabase_service.is_connected(),
    }
    return render(request, 'linkedin_scraper.html', context)

@login_required
def tiktok_scraper_view(request):
    """TikTok Scraper sayfası"""
    # Supabase'den TikTok verilerini çek
    tiktok_data = supabase_service.get_tiktok_data(limit=50)
    
    # Eğer Supabase'den veri gelmezse Django ORM'den fallback
    if not tiktok_data:
        try:
            from .models import TikTokData
            tiktok_data = list(TikTokData.objects.all()[:50].values())
        except:
            tiktok_data = []
    
    context = {
        'tiktok_data': tiktok_data,
        'supabase_connected': supabase_service.is_connected(),
    }
    return render(request, 'tiktok_scraper.html', context)

# API endpoints for social media platforms
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_instagram_scraper(request):
    """Instagram scraper'ı tetikle"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        username = data.get('username', '')
        hashtag = data.get('hashtag', '')
        url = data.get('url', '')
        
        # Instagram webhook URL'ini ayarlardan al
        instagram_webhook_url = Settings.get_setting('instagram_webhook_url', 'https://notifyn8n.tezgel.com/webhook/instagram-scraper')
        
        if not (username or hashtag or url):
            return JsonResponse({'error': 'Username, hashtag veya URL gereklidir.'}, status=400)
        
        # Scraping job kaydet
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"Instagram: {username or hashtag or url}",
            n8n_webhook_url=instagram_webhook_url,
            status='running'
        )
        
        # N8N webhook'u tetikle
        payload = {
            'platform': 'instagram',
            'username': username,
            'hashtag': hashtag,
            'url': url,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(instagram_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'job_id': job.id,
                'message': f'Instagram scraping başlatıldı - Kullanıcı: {username}, Hashtag: {hashtag}, URL: {url}'
            })
        else:
            job.status = 'failed'
            job.error_message = f'Instagram webhook hatası: {response.status_code} - {response.text}'
            job.save()
            return JsonResponse({'error': f'Instagram webhook hatası: {response.status_code}'}, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_facebook_scraper(request):
    """Facebook scraper'ı tetikle"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        page_name = data.get('page_name', '')
        page_url = data.get('page_url', '')
        
        # Facebook webhook URL'ini ayarlardan al
        facebook_webhook_url = Settings.get_setting('facebook_webhook_url', 'https://notifyn8n.tezgel.com/webhook/facebook-scraper')
        
        if not (page_name or page_url):
            return JsonResponse({'error': 'Page name veya URL gereklidir.'}, status=400)
        
        # Scraping job kaydet
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"Facebook: {page_name or page_url}",
            n8n_webhook_url=facebook_webhook_url,
            status='running'
        )
        
        # N8N webhook'u tetikle
        payload = {
            'platform': 'facebook',
            'page_name': page_name,
            'page_url': page_url,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(facebook_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'job_id': job.id,
                'message': f'Facebook scraping başlatıldı - Sayfa: {page_name or page_url}'
            })
        else:
            job.status = 'failed'
            job.error_message = f'Facebook webhook hatası: {response.status_code} - {response.text}'
            job.save()
            return JsonResponse({'error': f'Facebook webhook hatası: {response.status_code}'}, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_twitter_scraper(request):
    """Twitter scraper'ı tetikle"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        username = data.get('username', '')
        hashtag = data.get('hashtag', '')
        keyword = data.get('keyword', '')
        
        # Twitter webhook URL'ini ayarlardan al
        twitter_webhook_url = Settings.get_setting('twitter_webhook_url', 'https://notifyn8n.tezgel.com/webhook/twitter-scraper')
        
        if not (username or hashtag or keyword):
            return JsonResponse({'error': 'Username, hashtag veya keyword gereklidir.'}, status=400)
        
        # Scraping job kaydet
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"Twitter: {username or hashtag or keyword}",
            n8n_webhook_url=twitter_webhook_url,
            status='running'
        )
        
        # N8N webhook'u tetikle
        payload = {
            'platform': 'twitter',
            'username': username,
            'hashtag': hashtag,
            'keyword': keyword,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(twitter_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'job_id': job.id,
                'message': f'Twitter scraping başlatıldı - {username or hashtag or keyword}'
            })
        else:
            job.status = 'failed'
            job.error_message = f'Twitter webhook hatası: {response.status_code} - {response.text}'
            job.save()
            return JsonResponse({'error': f'Twitter webhook hatası: {response.status_code}'}, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_linkedin_scraper(request):
    """LinkedIn scraper'ı tetikle"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        profile_name = data.get('profile_name', '')
        company_name = data.get('company_name', '')
        job_title = data.get('job_title', '')
        
        # LinkedIn webhook URL'ini ayarlardan al
        linkedin_webhook_url = Settings.get_setting('linkedin_webhook_url', 'https://notifyn8n.tezgel.com/webhook/linkedin-scraper')
        
        if not (profile_name or company_name or job_title):
            return JsonResponse({'error': 'Profile name, company name veya job title gereklidir.'}, status=400)
        
        # Scraping job kaydet
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"LinkedIn: {profile_name or company_name or job_title}",
            n8n_webhook_url=linkedin_webhook_url,
            status='running'
        )
        
        # N8N webhook'u tetikle
        payload = {
            'platform': 'linkedin',
            'profile_name': profile_name,
            'company_name': company_name,
            'job_title': job_title,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(linkedin_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'job_id': job.id,
                'message': f'LinkedIn scraping başlatıldı - {profile_name or company_name or job_title}'
            })
        else:
            job.status = 'failed'
            job.error_message = f'LinkedIn webhook hatası: {response.status_code} - {response.text}'
            job.save()
            return JsonResponse({'error': f'LinkedIn webhook hatası: {response.status_code}'}, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_tiktok_scraper(request):
    """TikTok scraper'ı tetikle"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        username = data.get('username', '')
        hashtag = data.get('hashtag', '')
        sound_id = data.get('sound_id', '')
        
        # TikTok webhook URL'ini ayarlardan al
        tiktok_webhook_url = Settings.get_setting('tiktok_webhook_url', 'https://notifyn8n.tezgel.com/webhook/tiktok-scraper')
        
        if not (username or hashtag or sound_id):
            return JsonResponse({'error': 'Username, hashtag veya sound ID gereklidir.'}, status=400)
        
        # Scraping job kaydet
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"TikTok: {username or hashtag or sound_id}",
            n8n_webhook_url=tiktok_webhook_url,
            status='running'
        )
        
        # N8N webhook'u tetikle
        payload = {
            'platform': 'tiktok',
            'username': username,
            'hashtag': hashtag,
            'sound_id': sound_id,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(tiktok_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'job_id': job.id,
                'message': f'TikTok scraping başlatıldı - {username or hashtag or sound_id}'
            })
        else:
            job.status = 'failed'
            job.error_message = f'TikTok webhook hatası: {response.status_code} - {response.text}'
            job.save()
            return JsonResponse({'error': f'TikTok webhook hatası: {response.status_code}'}, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Data retrieval endpoints for social media platforms
@login_required
@require_http_methods(["GET"])
def get_instagram_data(request):
    """Instagram verilerini getir"""
    try:
        from .models import InstagramData
        
        instagram_data = InstagramData.objects.all()
        data = []
        
        for item in instagram_data:
            data.append({
                'id': item.id,
                'username': item.username,
                'full_name': item.full_name,
                'bio': item.bio,
                'followers_count': item.followers_count,
                'following_count': item.following_count,
                'posts_count': item.posts_count,
                'is_verified': item.is_verified,
                'category': item.category,
                'created_at': item.created_at.isoformat() if item.created_at else None
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'count': len(data),
            'message': f'{len(data)} Instagram verisi bulundu'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["GET"])
def get_facebook_data(request):
    """Facebook verilerini getir"""
    try:
        from .models import FacebookData
        
        facebook_data = FacebookData.objects.all()
        data = []
        
        for item in facebook_data:
            data.append({
                'id': item.id,
                'page_name': item.page_name,
                'description': item.description,
                'likes_count': item.likes_count,
                'followers_count': item.followers_count,
                'page_url': item.page_url,
                'is_verified': item.is_verified,
                'category': item.category,
                'phone': item.phone,
                'email': item.email,
                'website': item.website,
                'address': item.address,
                'created_at': item.created_at.isoformat() if item.created_at else None
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'count': len(data),
            'message': f'{len(data)} Facebook verisi bulundu'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["GET"])
def get_twitter_data(request):
    """Twitter verilerini getir"""
    try:
        from .models import TwitterData
        
        twitter_data = TwitterData.objects.all()
        data = []
        
        for item in twitter_data:
            data.append({
                'id': item.id,
                'username': item.username,
                'display_name': item.display_name,
                'bio': item.bio,
                'followers_count': item.followers_count,
                'following_count': item.following_count,
                'tweets_count': item.tweets_count,
                'is_verified': item.is_verified,
                'location': item.location,
                'website': item.website,
                'created_at': item.created_at.isoformat() if item.created_at else None
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'count': len(data),
            'message': f'{len(data)} Twitter verisi bulundu'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["GET"])
def get_linkedin_data(request):
    """LinkedIn verilerini getir"""
    try:
        from .models import LinkedInData
        
        linkedin_data = LinkedInData.objects.all()
        data = []
        
        for item in linkedin_data:
            data.append({
                'id': item.id,
                'profile_name': item.profile_name,
                'headline': item.headline,
                'summary': item.summary,
                'connections_count': item.connections_count,
                'location': item.location,
                'industry': item.industry,
                'current_company': item.current_company,
                'current_position': item.current_position,
                'experience_years': item.experience_years,
                'created_at': item.created_at.isoformat() if item.created_at else None
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'count': len(data),
            'message': f'{len(data)} LinkedIn verisi bulundu'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["GET"])
def get_tiktok_data(request):
    """TikTok verilerini getir"""
    try:
        from .models import TikTokData
        
        tiktok_data = TikTokData.objects.all()
        data = []
        
        for item in tiktok_data:
            data.append({
                'id': item.id,
                'username': item.username,
                'display_name': item.display_name,
                'bio': item.bio,
                'followers_count': item.followers_count,
                'following_count': item.following_count,
                'likes_count': item.likes_count,
                'videos_count': item.videos_count,
                'is_verified': item.is_verified,
                'external_url': item.external_url,
                'created_at': item.created_at.isoformat() if item.created_at else None
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'count': len(data),
            'message': f'{len(data)} TikTok verisi bulundu'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Webhook endpoints for receiving data from N8N
@csrf_exempt
@require_http_methods(["POST"])
def instagram_webhook(request):
    """Instagram webhook endpoint - N8N'den veri al"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        instagram_data_list = data.get('instagram_data', [])
        
        print(f"Instagram N8N'den gelen veri: {data}")
        
        # Job ID varsa job durumunu güncelle
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
                print(f"Instagram Job {job_id} tamamlandı")
            except ScrapingJob.DoesNotExist:
                print(f"Instagram Job {job_id} bulunamadı")
        
        # Gelen veriyi Supabase'e kaydet
        saved_count = 0
        if supabase_service.is_connected():
            supabase_result = supabase_service.upsert_instagram_data(instagram_data_list)
            if supabase_result.get('success'):
                saved_count = supabase_result.get('upserted_count', 0)
                print(f"Supabase'e {saved_count} Instagram verisi kaydedildi")
        
        # Django ORM'e de kaydet
        for item in instagram_data_list:
            try:
                from .models import InstagramData
                obj, created = InstagramData.objects.update_or_create(
                    username=item.get('username'),
                    defaults={
                        'full_name': item.get('full_name'),
                        'bio': item.get('bio'),
                        'followers_count': int(item.get('followers_count')) if item.get('followers_count') else None,
                        'following_count': int(item.get('following_count')) if item.get('following_count') else None,
                        'posts_count': int(item.get('posts_count')) if item.get('posts_count') else None,
                        'is_verified': item.get('is_verified', False),
                        'category': item.get('category'),
                    }
                )
                if not supabase_service.is_connected():
                    saved_count += 1
            except Exception as e:
                print(f"Instagram Django ORM'e veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} Instagram verisi başarıyla kaydedildi.',
            'saved_count': saved_count
        })
        
    except Exception as e:
        print(f"Instagram webhook hatası: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def facebook_webhook(request):
    """Facebook webhook endpoint - N8N'den veri al"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        facebook_data_list = data.get('facebook_data', [])
        
        print(f"Facebook N8N'den gelen veri: {data}")
        
        # Job ID varsa job durumunu güncelle
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
                print(f"Facebook Job {job_id} tamamlandı")
            except ScrapingJob.DoesNotExist:
                print(f"Facebook Job {job_id} bulunamadı")
        
        # Gelen veriyi Supabase'e kaydet
        saved_count = 0
        if supabase_service.is_connected():
            supabase_result = supabase_service.upsert_facebook_data(facebook_data_list)
            if supabase_result.get('success'):
                saved_count = supabase_result.get('upserted_count', 0)
                print(f"Supabase'e {saved_count} Facebook verisi kaydedildi")
        
        # Django ORM'e de kaydet
        for item in facebook_data_list:
            try:
                from .models import FacebookData
                obj, created = FacebookData.objects.update_or_create(
                    page_name=item.get('page_name'),
                    defaults={
                        'description': item.get('description'),
                        'likes_count': int(item.get('likes_count')) if item.get('likes_count') else None,
                        'followers_count': int(item.get('followers_count')) if item.get('followers_count') else None,
                        'page_url': item.get('page_url'),
                        'is_verified': item.get('is_verified', False),
                        'category': item.get('category'),
                        'phone': item.get('phone'),
                        'email': item.get('email'),
                        'website': item.get('website'),
                        'address': item.get('address'),
                    }
                )
                if not supabase_service.is_connected():
                    saved_count += 1
            except Exception as e:
                print(f"Facebook Django ORM'e veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} Facebook verisi başarıyla kaydedildi.',
            'saved_count': saved_count
        })
        
    except Exception as e:
        print(f"Facebook webhook hatası: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def twitter_webhook(request):
    """Twitter webhook endpoint - N8N'den veri al"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        twitter_data_list = data.get('twitter_data', [])
        
        print(f"Twitter N8N'den gelen veri: {data}")
        
        # Job ID varsa job durumunu güncelle
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
                print(f"Twitter Job {job_id} tamamlandı")
            except ScrapingJob.DoesNotExist:
                print(f"Twitter Job {job_id} bulunamadı")
        
        # Gelen veriyi Supabase'e kaydet
        saved_count = 0
        if supabase_service.is_connected():
            supabase_result = supabase_service.upsert_twitter_data(twitter_data_list)
            if supabase_result.get('success'):
                saved_count = supabase_result.get('upserted_count', 0)
                print(f"Supabase'e {saved_count} Twitter verisi kaydedildi")
        
        # Django ORM'e de kaydet
        for item in twitter_data_list:
            try:
                from .models import TwitterData
                obj, created = TwitterData.objects.update_or_create(
                    username=item.get('username'),
                    defaults={
                        'display_name': item.get('display_name'),
                        'bio': item.get('bio'),
                        'followers_count': int(item.get('followers_count')) if item.get('followers_count') else None,
                        'following_count': int(item.get('following_count')) if item.get('following_count') else None,
                        'tweets_count': int(item.get('tweets_count')) if item.get('tweets_count') else None,
                        'is_verified': item.get('is_verified', False),
                        'location': item.get('location'),
                        'website': item.get('website'),
                    }
                )
                if not supabase_service.is_connected():
                    saved_count += 1
            except Exception as e:
                print(f"Twitter Django ORM'e veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} Twitter verisi başarıyla kaydedildi.',
            'saved_count': saved_count
        })
        
    except Exception as e:
        print(f"Twitter webhook hatası: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def linkedin_webhook(request):
    """LinkedIn webhook endpoint - N8N'den veri al"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        linkedin_data_list = data.get('linkedin_data', [])
        
        print(f"LinkedIn N8N'den gelen veri: {data}")
        
        # Job ID varsa job durumunu güncelle
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
                print(f"LinkedIn Job {job_id} tamamlandı")
            except ScrapingJob.DoesNotExist:
                print(f"LinkedIn Job {job_id} bulunamadı")
        
        # Gelen veriyi Supabase'e kaydet
        saved_count = 0
        if supabase_service.is_connected():
            supabase_result = supabase_service.upsert_linkedin_data(linkedin_data_list)
            if supabase_result.get('success'):
                saved_count = supabase_result.get('upserted_count', 0)
                print(f"Supabase'e {saved_count} LinkedIn verisi kaydedildi")
        
        # Django ORM'e de kaydet
        for item in linkedin_data_list:
            try:
                from .models import LinkedInData
                obj, created = LinkedInData.objects.update_or_create(
                    profile_name=item.get('profile_name'),
                    defaults={
                        'headline': item.get('headline'),
                        'summary': item.get('summary'),
                        'connections_count': int(item.get('connections_count')) if item.get('connections_count') else None,
                        'location': item.get('location'),
                        'industry': item.get('industry'),
                        'current_company': item.get('current_company'),
                        'current_position': item.get('current_position'),
                        'experience_years': int(item.get('experience_years')) if item.get('experience_years') else None,
                    }
                )
                if not supabase_service.is_connected():
                    saved_count += 1
            except Exception as e:
                print(f"LinkedIn Django ORM'e veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} LinkedIn verisi başarıyla kaydedildi.',
            'saved_count': saved_count
        })
        
    except Exception as e:
        print(f"LinkedIn webhook hatası: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def tiktok_webhook(request):
    """TikTok webhook endpoint - N8N'den veri al"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        tiktok_data_list = data.get('tiktok_data', [])
        
        print(f"TikTok N8N'den gelen veri: {data}")
        
        # Job ID varsa job durumunu güncelle
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
                print(f"TikTok Job {job_id} tamamlandı")
            except ScrapingJob.DoesNotExist:
                print(f"TikTok Job {job_id} bulunamadı")
        
        # Gelen veriyi Supabase'e kaydet
        saved_count = 0
        if supabase_service.is_connected():
            supabase_result = supabase_service.upsert_tiktok_data(tiktok_data_list)
            if supabase_result.get('success'):
                saved_count = supabase_result.get('upserted_count', 0)
                print(f"Supabase'e {saved_count} TikTok verisi kaydedildi")
        
        # Django ORM'e de kaydet
        for item in tiktok_data_list:
            try:
                from .models import TikTokData
                obj, created = TikTokData.objects.update_or_create(
                    username=item.get('username'),
                    defaults={
                        'display_name': item.get('display_name'),
                        'bio': item.get('bio'),
                        'followers_count': int(item.get('followers_count')) if item.get('followers_count') else None,
                        'following_count': int(item.get('following_count')) if item.get('following_count') else None,
                        'likes_count': int(item.get('likes_count')) if item.get('likes_count') else None,
                        'videos_count': int(item.get('videos_count')) if item.get('videos_count') else None,
                        'is_verified': item.get('is_verified', False),
                        'external_url': item.get('external_url'),
                    }
                )
                if not supabase_service.is_connected():
                    saved_count += 1
            except Exception as e:
                print(f"TikTok Django ORM'e veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} TikTok verisi başarıyla kaydedildi.',
            'saved_count': saved_count
        })
        
    except Exception as e:
        print(f"TikTok webhook hatası: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Settings API Views
@login_required
def get_supabase_settings(request):
    """Supabase ayarlarını döndür"""
    try:
        from django.conf import settings
        return JsonResponse({
            'success': True,
            'settings': {
                'connected': supabase_service.is_connected(),
                'url': getattr(settings, 'SUPABASE_URL', '')[:50] + '...' if getattr(settings, 'SUPABASE_URL', '') else '',
                'key': '***' if getattr(settings, 'SUPABASE_ANON_KEY', '') else '',
                'status': 'Bağlı' if supabase_service.is_connected() else 'Bağlantı Yok'
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def get_n8n_settings(request):
    """N8N ayarlarını döndür"""
    try:
        from django.conf import settings
        return JsonResponse({
            'success': True,
            'settings': {
                'webhook_url': getattr(settings, 'N8N_WEBHOOK_URL', ''),
                'api_key': '***' if getattr(settings, 'N8N_API_KEY', '') else '',
                'status': 'Aktif'
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def get_webhook_settings(request):
    """Webhook ayarlarını döndür"""
    try:
        from .models import Settings
        
        webhook_settings = {
            'map_webhook': '/api/receive-n8n-data/',
            'instagram_webhook': '/api/instagram-webhook/',
            'facebook_webhook': '/api/facebook-webhook/',
            'twitter_webhook': '/api/twitter-webhook/',
            'linkedin_webhook': '/api/linkedin-webhook/',
            'tiktok_webhook': '/api/tiktok-webhook/',
            'webhook_urls': {
                'map_scraper': Settings.get_setting('webhook_url', 'https://notifyn8n.tezgel.com/webhook/90004c3a-f7d6-4030-ac04-539a5d38beb5'),
                'instagram_scraper': Settings.get_setting('instagram_webhook_url', 'https://notifyn8n.tezgel.com/webhook/instagram-scraper'),
                'facebook_scraper': Settings.get_setting('facebook_webhook_url', 'https://notifyn8n.tezgel.com/webhook/facebook-scraper'),
                'twitter_scraper': Settings.get_setting('twitter_webhook_url', 'https://notifyn8n.tezgel.com/webhook/twitter-scraper'),
                'linkedin_scraper': Settings.get_setting('linkedin_webhook_url', 'https://notifyn8n.tezgel.com/webhook/linkedin-scraper'),
                'tiktok_scraper': Settings.get_setting('tiktok_webhook_url', 'https://notifyn8n.tezgel.com/webhook/tiktok-scraper'),
            }
        }
        
        return JsonResponse({
            'success': True,
            'settings': webhook_settings
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Platform webhook test fonksiyonları
@require_http_methods(["POST"])
@login_required
@csrf_exempt
def test_instagram_webhook(request):
    """Instagram webhook bağlantısını test et"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        webhook_url = data.get('webhook_url', '') or Settings.get_setting('instagram_webhook_url', 'https://notifyn8n.tezgel.com/webhook/instagram-scraper')
        
        if not webhook_url:
            return JsonResponse({'error': 'Instagram webhook URL bulunamadı.'}, status=400)
        
        test_payload = {
            'test': True,
            'platform': 'instagram',
            'username': 'test_user',
            'user_id': request.user.id,
            'timestamp': int(time.time())
        }
        
        response = requests.get(webhook_url, params=test_payload, timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'Instagram webhook başarıyla test edildi!',
                'status_code': response.status_code
            })
        else:
            return JsonResponse({
                'error': f'Instagram webhook test edilemedi: {response.status_code}',
                'status_code': response.status_code
            }, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def test_facebook_webhook(request):
    """Facebook webhook bağlantısını test et"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        webhook_url = data.get('webhook_url', '') or Settings.get_setting('facebook_webhook_url', 'https://notifyn8n.tezgel.com/webhook/facebook-scraper')
        
        if not webhook_url:
            return JsonResponse({'error': 'Facebook webhook URL bulunamadı.'}, status=400)
        
        test_payload = {
            'test': True,
            'platform': 'facebook',
            'page_name': 'test_page',
            'user_id': request.user.id,
            'timestamp': int(time.time())
        }
        
        response = requests.get(webhook_url, params=test_payload, timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'Facebook webhook başarıyla test edildi!',
                'status_code': response.status_code
            })
        else:
            return JsonResponse({
                'error': f'Facebook webhook test edilemedi: {response.status_code}',
                'status_code': response.status_code
            }, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def test_twitter_webhook(request):
    """Twitter webhook bağlantısını test et"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        webhook_url = data.get('webhook_url', '') or Settings.get_setting('twitter_webhook_url', 'https://notifyn8n.tezgel.com/webhook/twitter-scraper')
        
        if not webhook_url:
            return JsonResponse({'error': 'Twitter webhook URL bulunamadı.'}, status=400)
        
        test_payload = {
            'test': True,
            'platform': 'twitter',
            'username': 'test_user',
            'user_id': request.user.id,
            'timestamp': int(time.time())
        }
        
        response = requests.get(webhook_url, params=test_payload, timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'Twitter webhook başarıyla test edildi!',
                'status_code': response.status_code
            })
        else:
            return JsonResponse({
                'error': f'Twitter webhook test edilemedi: {response.status_code}',
                'status_code': response.status_code
            }, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def test_linkedin_webhook(request):
    """LinkedIn webhook bağlantısını test et"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        webhook_url = data.get('webhook_url', '') or Settings.get_setting('linkedin_webhook_url', 'https://notifyn8n.tezgel.com/webhook/linkedin-scraper')
        
        if not webhook_url:
            return JsonResponse({'error': 'LinkedIn webhook URL bulunamadı.'}, status=400)
        
        test_payload = {
            'test': True,
            'platform': 'linkedin',
            'profile_name': 'test_profile',
            'user_id': request.user.id,
            'timestamp': int(time.time())
        }
        
        response = requests.get(webhook_url, params=test_payload, timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'LinkedIn webhook başarıyla test edildi!',
                'status_code': response.status_code
            })
        else:
            return JsonResponse({
                'error': f'LinkedIn webhook test edilemedi: {response.status_code}',
                'status_code': response.status_code
            }, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def test_tiktok_webhook(request):
    """TikTok webhook bağlantısını test et"""
    try:
        from .models import Settings
        
        data = json.loads(request.body)
        webhook_url = data.get('webhook_url', '') or Settings.get_setting('tiktok_webhook_url', 'https://notifyn8n.tezgel.com/webhook/tiktok-scraper')
        
        if not webhook_url:
            return JsonResponse({'error': 'TikTok webhook URL bulunamadı.'}, status=400)
        
        test_payload = {
            'test': True,
            'platform': 'tiktok',
            'username': 'test_user',
            'user_id': request.user.id,
            'timestamp': int(time.time())
        }
        
        response = requests.get(webhook_url, params=test_payload, timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'TikTok webhook başarıyla test edildi!',
                'status_code': response.status_code
            })
        else:
            return JsonResponse({
                'error': f'TikTok webhook test edilemedi: {response.status_code}',
                'status_code': response.status_code
            }, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_system_settings(request):
    """Sistem ayarlarını döndür"""
    try:
        return JsonResponse({
            'success': True,
            'settings': {
                'debug_mode': True,
                'auto_sync': True,
                'backup_enabled': False,
                'log_level': 'INFO'
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def get_system_status(request):
    """Sistem durumunu döndür"""
    try:
        from django.contrib.auth.models import User
        
        # Kullanıcı sayısı
        user_count = User.objects.count()
        
        # Supabase durum
        supabase_status = supabase_service.is_connected()
        
        # Veri sayıları
        total_data = 0
        if supabase_status:
            try:
                stats = supabase_service.get_sync_stats()
                total_data = stats.get('total_records', 0)
            except:
                pass
        
        # Son 24 saatteki işler
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(days=1)
        recent_jobs = ScrapingJob.objects.filter(created_at__gte=yesterday).count()
        
        return JsonResponse({
            'success': True,
            'status': {
                'database': 'Aktif',
                'supabase': 'Bağlı' if supabase_status else 'Bağlantı Yok',
                'users': user_count,
                'total_records': total_data,
                'recent_jobs': recent_jobs,
                'uptime': '1 gün+'  # Bu gerçek uptime hesaplanabilir
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
