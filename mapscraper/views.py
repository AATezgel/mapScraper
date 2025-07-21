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
        supabase_data = supabase_service.get_map_data(limit=1000)  # İlk yüklemede daha az
        map_data = supabase_data if supabase_data else []
    else:
        map_data = MapData.objects.all()[:1000]  # İlk yüklemede daha az
    
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
        
        Settings.set_setting('webhook_url', webhook_url, 'N8N Webhook URL')
        Settings.set_setting('auto_refresh', '1' if auto_refresh else '0', 'Otomatik yenileme açık/kapalı')
        
        messages.success(request, 'Ayarlar başarıyla kaydedildi!')
        return redirect('settings')
    
    # Mevcut ayarları al
    webhook_url = Settings.get_setting('webhook_url', 'https://notifyn8n.tezgel.com/webhook/90004c3a-f7d6-4030-ac04-539a5d38beb5')
    auto_refresh = Settings.get_setting('auto_refresh', '0') == '1'
    
    import django
    context = {
        'django_version': django.get_version(),
        'supabase_connected': supabase_service.is_connected(),
        'webhook_url': webhook_url,
        'auto_refresh': auto_refresh,
    }
    return render(request, 'settings.html', context)
