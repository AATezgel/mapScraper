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
from .models import (
    MapData, ScrapingJob, Settings,
    InstagramData, FacebookData, TwitterData, LinkedInData, TikTokData
)

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
        
        # Django ORM'den veri sayısı ve istatistikler
        django_count = MapData.objects.count()
        
        # Sosyal medya platform sayıları
        instagram_count = InstagramData.objects.count()
        facebook_count = FacebookData.objects.count()
        twitter_count = TwitterData.objects.count()
        linkedin_count = LinkedInData.objects.count()
        tiktok_count = TikTokData.objects.count()
        
        category_stats = {}
        
        # Kategori istatistikleri - Django ORM'den al
        from django.db.models import Count
        category_data = MapData.objects.values('category').annotate(count=Count('category')).order_by('-count')
        for item in category_data:
            if item['category']:  # Boş kategorileri atla
                category_stats[item['category']] = item['count']
        
        context = {
            'recent_jobs': recent_jobs,
            'total_jobs': total_jobs,
            'django_count': django_count,
            'instagram_count': instagram_count,
            'facebook_count': facebook_count,
            'twitter_count': twitter_count,
            'linkedin_count': linkedin_count,
            'tiktok_count': tiktok_count,
            'recent_24h_jobs': recent_24h_jobs,
            'successful_jobs': successful_jobs,
            'category_stats': category_stats,
        }
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        # Hata durumunda basit dashboard
        context = {
            'recent_jobs': [],
            'total_jobs': 0,
            'django_count': 0,
            'instagram_count': 0,
            'facebook_count': 0,
            'twitter_count': 0,
            'linkedin_count': 0,
            'tiktok_count': 0,
            'recent_24h_jobs': 0,
            'successful_jobs': 0,
            'category_stats': {},
            'error': str(e)
        }
        return render(request, 'dashboard.html', context)

@login_required
def map_scraper_view(request):
    # Django ORM'den veri çek
    map_data = list(MapData.objects.all()[:1000].values())
    jobs = ScrapingJob.objects.filter(user=request.user)[:10]
    context = {
        'map_data': map_data,
        'jobs': jobs,
    }
    return render(request, 'map_scraper.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def trigger_n8n_api(request):
    # Login kontrolü AJAX için
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Lütfen giriş yapın.'}, status=401)
    
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        
        if not query:
            return JsonResponse({'error': 'Query gereklidir.'}, status=400)
        
        # Scraping job kaydet
        job = ScrapingJob.objects.create(
            user=request.user,
            query=query,
            status='running'
        )
        
        # SERP API ile Google Maps'ten veri çek
        serp_api_key = Settings.get_setting('serp_api_key', '19b8cfa3a27fb5b568411275ca980abbba9cdc077b6a1ee93bf5c18ca556b397')
        
        serp_params = {
            'engine': 'google_maps',
            'q': query,
            'type': 'search',
            'api_key': serp_api_key
        }
        
        try:
            response = requests.get('https://serpapi.com/search.json', params=serp_params, timeout=30)
            
            if response.status_code == 200:
                serp_data = response.json()
                local_results = serp_data.get('local_results', [])
                
                # Verileri parse et ve kaydet
                saved_count = 0
                updated_count = 0
                
                for item in local_results:
                    gps = item.get('gps_coordinates', {})
                    
                    map_data = {
                        'name': item.get('title', ''),
                        'address': item.get('address', ''),
                        'phone': item.get('phone', ''),
                        'rating': float(item.get('rating', 0)) if item.get('rating') else None,
                        'category': item.get('type', ''),
                        'website': item.get('website', ''),
                        'latitude': gps.get('latitude') if gps.get('latitude') else None,
                        'longitude': gps.get('longitude') if gps.get('longitude') else None,
                    }
                    
                    # Aynı isimli kayıt varsa güncelle, yoksa oluştur
                    obj, created = MapData.objects.update_or_create(
                        name=map_data['name'],
                        defaults=map_data
                    )
                    
                    if created:
                        saved_count += 1
                    else:
                        updated_count += 1
                
                # Job'u tamamlandı olarak işaretle
                job.status = 'completed'
                job.save()
                
                return JsonResponse({
                    'success': True,
                    'job_id': job.id,
                    'message': f'{saved_count} yeni kayıt eklendi, {updated_count} kayıt güncellendi.',
                    'saved_count': saved_count,
                    'updated_count': updated_count,
                    'total_results': len(local_results)
                })
            else:
                job.status = 'failed'
                job.error_message = f'SERP API hatası: {response.status_code}'
                job.save()
                return JsonResponse({'error': f'SERP API hatası: {response.status_code}'}, status=500)
                
        except requests.exceptions.Timeout:
            job.status = 'failed'
            job.error_message = 'SERP API zaman aşımına uğradı'
            job.save()
            return JsonResponse({'error': 'SERP API zaman aşımına uğradı'}, status=500)
            
    except Exception as e:
        if 'job' in locals():
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def test_n8n_webhook(request):
    """SERP API bağlantısını test et"""
    try:
        data = json.loads(request.body)
        api_key = data.get('api_key', '')
        
        if not api_key:
            api_key = Settings.get_setting('serp_api_key', '19b8cfa3a27fb5b568411275ca980abbba9cdc077b6a1ee93bf5c18ca556b397')
            
        if not api_key:
            return JsonResponse({'error': 'SERP API key bulunamadı.'}, status=400)
        
        # Test query
        test_params = {
            'engine': 'google_maps',
            'q': 'restaurant istanbul',
            'type': 'search',
            'api_key': api_key
        }
        
        response = requests.get('https://serpapi.com/search.json', params=test_params, timeout=10)
        
        if response.status_code == 200:
            result_data = response.json()
            local_results = result_data.get('local_results', [])
            
            return JsonResponse({
                'success': True,
                'message': f'SERP API başarıyla test edildi! {len(local_results)} sonuç bulundu.',
                'status_code': response.status_code,
                'sample_result': local_results[0] if local_results else None
            })
        else:
            return JsonResponse({
                'error': f'SERP API test edilemedi: {response.status_code}',
                'status_code': response.status_code,
                'response': response.text[:200]
            }, status=500)
            
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'error': 'SERP API sunucusuna bağlanılamadı.',
        }, status=500)
    except requests.exceptions.Timeout:
        return JsonResponse({
            'error': 'SERP API zaman aşımına uğradı.',
        }, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@login_required
def get_map_data(request):
    try:
        # Django ORM'den veri çek
        map_data = list(MapData.objects.all().values())
        
        # created_at alanını kontrol et ve düzelt
        for item in map_data:
            if 'created_at' not in item or not item['created_at']:
                item['created_at'] = '2024-01-01T00:00:00Z'
            elif hasattr(item['created_at'], 'isoformat'):
                item['created_at'] = item['created_at'].isoformat()
                
        return JsonResponse({
            'success': True,
            'data': map_data, 
            'source': 'django_orm',
            'count': len(map_data)
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
def add_map_data(request):
    """Manuel olarak map data ekler (Django ORM)"""
    # Login kontrolü AJAX için
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Lütfen giriş yapın.'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        if not data.get('name') or not data.get('address'):
            return JsonResponse({'error': 'İsim ve adres alanları gereklidir.'}, status=400)
        
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
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def settings_view(request):
    """Ayarlar sayfası"""
    if request.method == 'POST':
        # Ayarları kaydet
        serp_api_key = request.POST.get('serp_api_key', '')
        auto_refresh = request.POST.get('auto_refresh', 'off') == 'on'
        
        # Sosyal medya webhook URL'leri
        instagram_webhook_url = request.POST.get('instagram_webhook_url', '')
        facebook_webhook_url = request.POST.get('facebook_webhook_url', '')
        twitter_webhook_url = request.POST.get('twitter_webhook_url', '')
        linkedin_webhook_url = request.POST.get('linkedin_webhook_url', '')
        tiktok_webhook_url = request.POST.get('tiktok_webhook_url', '')
        
        Settings.set_setting('serp_api_key', serp_api_key, 'SERP API Key for Google Maps')
        Settings.set_setting('auto_refresh', '1' if auto_refresh else '0', 'Otomatik yenileme açık/kapalı')
        Settings.set_setting('instagram_webhook_url', instagram_webhook_url, 'Instagram N8N Webhook URL')
        Settings.set_setting('facebook_webhook_url', facebook_webhook_url, 'Facebook N8N Webhook URL')
        Settings.set_setting('twitter_webhook_url', twitter_webhook_url, 'Twitter N8N Webhook URL')
        Settings.set_setting('linkedin_webhook_url', linkedin_webhook_url, 'LinkedIn N8N Webhook URL')
        Settings.set_setting('tiktok_webhook_url', tiktok_webhook_url, 'TikTok N8N Webhook URL')
        
        messages.success(request, 'Ayarlar başarıyla kaydedildi!')
        return redirect('settings')
    
    # Mevcut ayarları al
    serp_api_key = Settings.get_setting('serp_api_key', '19b8cfa3a27fb5b568411275ca980abbba9cdc077b6a1ee93bf5c18ca556b397')
    auto_refresh = Settings.get_setting('auto_refresh', '0') == '1'
    instagram_webhook_url = Settings.get_setting('instagram_webhook_url', 'https://notifyn8n.tezgel.com/webhook/instagram-scraper')
    facebook_webhook_url = Settings.get_setting('facebook_webhook_url', 'https://notifyn8n.tezgel.com/webhook/facebook-scraper')
    twitter_webhook_url = Settings.get_setting('twitter_webhook_url', 'https://notifyn8n.tezgel.com/webhook/twitter-scraper')
    linkedin_webhook_url = Settings.get_setting('linkedin_webhook_url', 'https://notifyn8n.tezgel.com/webhook/linkedin-scraper')
    tiktok_webhook_url = Settings.get_setting('tiktok_webhook_url', 'https://notifyn8n.tezgel.com/webhook/tiktok-scraper')
    
    import django
    context = {
        'django_version': django.get_version(),
        'serp_api_key': serp_api_key,
        'auto_refresh': auto_refresh,
        'instagram_webhook_url': instagram_webhook_url,
        'facebook_webhook_url': facebook_webhook_url,
        'twitter_webhook_url': twitter_webhook_url,
        'linkedin_webhook_url': linkedin_webhook_url,
        'tiktok_webhook_url': tiktok_webhook_url,
    }
    return render(request, 'settings.html', context)

# Social Media Scrapers
@login_required
def instagram_scraper_view(request):
    instagram_data = list(InstagramData.objects.all()[:50].values())
    context = {
        'instagram_data': instagram_data,
    }
    return render(request, 'instagram_scraper.html', context)

@login_required
def facebook_scraper_view(request):
    facebook_data = list(FacebookData.objects.all()[:50].values())
    context = {
        'facebook_data': facebook_data,
    }
    return render(request, 'facebook_scraper.html', context)

@login_required
def twitter_scraper_view(request):
    twitter_data = list(TwitterData.objects.all()[:50].values())
    context = {
        'twitter_data': twitter_data,
    }
    return render(request, 'twitter_scraper.html', context)

@login_required
def linkedin_scraper_view(request):
    linkedin_data = list(LinkedInData.objects.all()[:50].values())
    context = {
        'linkedin_data': linkedin_data,
    }
    return render(request, 'linkedin_scraper.html', context)

@login_required
def tiktok_scraper_view(request):
    tiktok_data = list(TikTokData.objects.all()[:50].values())
    context = {
        'tiktok_data': tiktok_data,
    }
    return render(request, 'tiktok_scraper.html', context)

# Social Media API endpoints
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_instagram_scraper(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '')
        hashtag = data.get('hashtag', '')
        url = data.get('url', '')
        
        instagram_webhook_url = Settings.get_setting('instagram_webhook_url', 'https://notifyn8n.tezgel.com/webhook/instagram-scraper')
        
        if not (username or hashtag or url):
            return JsonResponse({'error': 'Username, hashtag veya URL gereklidir.'}, status=400)
        
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"Instagram: {username or hashtag or url}",
            n8n_webhook_url=instagram_webhook_url,
            status='running'
        )
        
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
                'message': f'Instagram scraping başlatıldı'
            })
        else:
            job.status = 'failed'
            job.error_message = f'Webhook hatası: {response.status_code}'
            job.save()
            return JsonResponse({'error': f'Webhook hatası: {response.status_code}'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Similar functions for other social platforms
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_facebook_scraper(request):
    try:
        data = json.loads(request.body)
        page_name = data.get('page_name', '')
        
        facebook_webhook_url = Settings.get_setting('facebook_webhook_url', 'https://notifyn8n.tezgel.com/webhook/facebook-scraper')
        
        if not page_name:
            return JsonResponse({'error': 'Page name gereklidir.'}, status=400)
        
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"Facebook: {page_name}",
            n8n_webhook_url=facebook_webhook_url,
            status='running'
        )
        
        payload = {
            'platform': 'facebook',
            'page_name': page_name,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(facebook_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({'success': True, 'job_id': job.id, 'message': 'Facebook scraping başlatıldı'})
        else:
            job.status = 'failed'
            job.error_message = f'Webhook hatası: {response.status_code}'
            job.save()
            return JsonResponse({'error': f'Webhook hatası: {response.status_code}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_twitter_scraper(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '')
        
        twitter_webhook_url = Settings.get_setting('twitter_webhook_url', 'https://notifyn8n.tezgel.com/webhook/twitter-scraper')
        
        if not username:
            return JsonResponse({'error': 'Username gereklidir.'}, status=400)
        
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"Twitter: {username}",
            n8n_webhook_url=twitter_webhook_url,
            status='running'
        )
        
        payload = {
            'platform': 'twitter',
            'username': username,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(twitter_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({'success': True, 'job_id': job.id, 'message': 'Twitter scraping başlatıldı'})
        else:
            job.status = 'failed'
            job.error_message = f'Webhook hatası: {response.status_code}'
            job.save()
            return JsonResponse({'error': f'Webhook hatası: {response.status_code}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_linkedin_scraper(request):
    try:
        data = json.loads(request.body)
        profile_name = data.get('profile_name', '')
        
        linkedin_webhook_url = Settings.get_setting('linkedin_webhook_url', 'https://notifyn8n.tezgel.com/webhook/linkedin-scraper')
        
        if not profile_name:
            return JsonResponse({'error': 'Profile name gereklidir.'}, status=400)
        
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"LinkedIn: {profile_name}",
            n8n_webhook_url=linkedin_webhook_url,
            status='running'
        )
        
        payload = {
            'platform': 'linkedin',
            'profile_name': profile_name,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(linkedin_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({'success': True, 'job_id': job.id, 'message': 'LinkedIn scraping başlatıldı'})
        else:
            job.status = 'failed'
            job.error_message = f'Webhook hatası: {response.status_code}'
            job.save()
            return JsonResponse({'error': f'Webhook hatası: {response.status_code}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_tiktok_scraper(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '')
        
        tiktok_webhook_url = Settings.get_setting('tiktok_webhook_url', 'https://notifyn8n.tezgel.com/webhook/tiktok-scraper')
        
        if not username:
            return JsonResponse({'error': 'Username gereklidir.'}, status=400)
        
        job = ScrapingJob.objects.create(
            user=request.user,
            query=f"TikTok: {username}",
            n8n_webhook_url=tiktok_webhook_url,
            status='running'
        )
        
        payload = {
            'platform': 'tiktok',
            'username': username,
            'job_id': job.id,
            'user_id': request.user.id
        }
        
        response = requests.get(tiktok_webhook_url, params=payload, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse({'success': True, 'job_id': job.id, 'message': 'TikTok scraping başlatıldı'})
        else:
            job.status = 'failed'
            job.error_message = f'Webhook hatası: {response.status_code}'
            job.save()
            return JsonResponse({'error': f'Webhook hatası: {response.status_code}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Webhook receivers for social media data
@csrf_exempt
@require_http_methods(["POST"])
def instagram_webhook(request):
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        instagram_data_list = data.get('instagram_data', [])
        
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
            except ScrapingJob.DoesNotExist:
                pass
        
        saved_count = 0
        for item in instagram_data_list:
            try:
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
                saved_count += 1
            except Exception as e:
                print(f"Instagram veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} Instagram verisi kaydedildi.',
            'saved_count': saved_count
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Webhook receivers for other platforms
@csrf_exempt
@require_http_methods(["POST"])
def facebook_webhook(request):
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        facebook_data_list = data.get('facebook_data', [])
        
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
            except ScrapingJob.DoesNotExist:
                pass
        
        saved_count = 0
        for item in facebook_data_list:
            try:
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
                saved_count += 1
            except Exception as e:
                print(f"Facebook veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} Facebook verisi kaydedildi.',
            'saved_count': saved_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def twitter_webhook(request):
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        twitter_data_list = data.get('twitter_data', [])
        
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
            except ScrapingJob.DoesNotExist:
                pass
        
        saved_count = 0
        for item in twitter_data_list:
            try:
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
                saved_count += 1
            except Exception as e:
                print(f"Twitter veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} Twitter verisi kaydedildi.',
            'saved_count': saved_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def linkedin_webhook(request):
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        linkedin_data_list = data.get('linkedin_data', [])
        
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
            except ScrapingJob.DoesNotExist:
                pass
        
        saved_count = 0
        for item in linkedin_data_list:
            try:
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
                saved_count += 1
            except Exception as e:
                print(f"LinkedIn veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} LinkedIn verisi kaydedildi.',
            'saved_count': saved_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def tiktok_webhook(request):
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        tiktok_data_list = data.get('tiktok_data', [])
        
        if job_id:
            try:
                job = ScrapingJob.objects.get(id=job_id)
                job.status = 'completed'
                job.save()
            except ScrapingJob.DoesNotExist:
                pass
        
        saved_count = 0
        for item in tiktok_data_list:
            try:
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
                saved_count += 1
            except Exception as e:
                print(f"TikTok veri kaydedilirken hata: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'{saved_count} TikTok verisi kaydedildi.',
            'saved_count': saved_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Data getters for social platforms
@login_required
@require_http_methods(["GET"])
def get_facebook_data(request):
    try:
        facebook_data = list(FacebookData.objects.all().values())
        return JsonResponse({
            'success': True,
            'data': facebook_data,
            'count': len(facebook_data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["GET"])
def get_twitter_data(request):
    try:
        twitter_data = list(TwitterData.objects.all().values())
        return JsonResponse({
            'success': True,
            'data': twitter_data,
            'count': len(twitter_data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["GET"])
def get_linkedin_data(request):
    try:
        linkedin_data = list(LinkedInData.objects.all().values())
        return JsonResponse({
            'success': True,
            'data': linkedin_data,
            'count': len(linkedin_data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["GET"])
def get_tiktok_data(request):
    try:
        tiktok_data = list(TikTokData.objects.all().values())
        return JsonResponse({
            'success': True,
            'data': tiktok_data,
            'count': len(tiktok_data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["GET"])
def get_instagram_data(request):
    try:
        instagram_data = list(InstagramData.objects.all().values())
        
        return JsonResponse({
            'success': True,
            'data': instagram_data,
            'count': len(instagram_data),
            'message': f'{len(instagram_data)} Instagram verisi bulundu'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
