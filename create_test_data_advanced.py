#!/usr/bin/env python3
"""
Test verilerini veritabanına ekleyen script
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Django settings'i ayarla
sys.path.append('/Users/aatezgel/Projects/django/mapToplayici')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from mapscraper.models import (
    MapData, InstagramData, FacebookData, TwitterData, 
    LinkedInData, TikTokData, ScrapingJob
)
from django.contrib.auth.models import User

def create_test_map_data():
    """Test map verileri oluştur"""
    test_data = [
        {
            'name': 'Starbucks Kadıköy',
            'address': 'Kadıköy Mah. Moda Cad. No:123 Kadıköy/İstanbul',
            'phone': '+90 216 123 4567',
            'website': 'https://starbucks.com.tr',
            'rating': 4.5,
            'reviews_count': 234,
            'latitude': 40.9892,
            'longitude': 29.0254,
            'category': 'Kahvehane'
        },
        {
            'name': 'McDonald\'s Taksim',
            'address': 'Taksim Mey. İstiklal Cad. No:89 Beyoğlu/İstanbul',
            'phone': '+90 212 987 6543',
            'website': 'https://mcdonalds.com.tr',
            'rating': 4.2,
            'reviews_count': 456,
            'latitude': 41.0369,
            'longitude': 28.9850,
            'category': 'Fast Food'
        },
        {
            'name': 'Teknosa Ataşehir',
            'address': 'Ataşehir AVM Kat:2 No:45 Ataşehir/İstanbul',
            'phone': '+90 216 555 1234',
            'website': 'https://teknosa.com',
            'rating': 4.1,
            'reviews_count': 189,
            'latitude': 40.9823,
            'longitude': 29.1234,
            'category': 'Elektronik'
        },
        {
            'name': 'Yapı Kredi Bankası Beşiktaş',
            'address': 'Beşiktaş Mah. Barbaros Bulvarı No:67 Beşiktaş/İstanbul',
            'phone': '+90 212 444 0444',
            'website': 'https://yapikredi.com.tr',
            'rating': 3.8,
            'reviews_count': 92,
            'latitude': 41.0422,
            'longitude': 29.0084,
            'category': 'Banka'
        },
        {
            'name': 'Migros Bahçelievler',
            'address': 'Bahçelievler Mah. E-5 Yanyol No:234 Bahçelievler/İstanbul',
            'phone': '+90 212 333 2222',
            'website': 'https://migros.com.tr',
            'rating': 4.3,
            'reviews_count': 167,
            'latitude': 40.9978,
            'longitude': 28.8567,
            'category': 'Süpermarket'
        }
    ]
    
    created_count = 0
    for data in test_data:
        map_obj, created = MapData.objects.get_or_create(
            name=data['name'],
            address=data['address'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✓ Map data created: {data['name']}")
    
    print(f"Created {created_count} new map data entries")

def create_test_instagram_data():
    """Test Instagram verileri oluştur"""
    test_data = [
        {
            'username': 'cafe_istanbul',
            'full_name': 'Cafe Istanbul',
            'bio': 'İstanbul\'un en lezzetli kahveleri ☕ #coffee #istanbul',
            'followers_count': 15420,
            'following_count': 892,
            'posts_count': 2341,
            'external_url': 'https://cafeistanbul.com',
            'is_verified': False,
            'is_private': False,
            'category': 'Kahvehane'
        },
        {
            'username': 'restoran_bosphorus',
            'full_name': 'Restoran Bosphorus',
            'bio': 'Boğaz manzaralı lezzet durağı 🌊 Rezervasyon: 0212-XXX-XXXX',
            'followers_count': 8934,
            'following_count': 456,
            'posts_count': 1876,
            'external_url': 'https://bosphorusrestaurant.com',
            'is_verified': True,
            'is_private': False,
            'category': 'Restoran'
        },
        {
            'username': 'fitness_center_kadikoy',
            'full_name': 'Fitness Center Kadıköy',
            'bio': '💪 Kadıköy\'ün en modern spor salonu | Ücretsiz deneme',
            'followers_count': 3245,
            'following_count': 234,
            'posts_count': 945,
            'external_url': 'https://fitnesscenterkadikoy.com',
            'is_verified': False,
            'is_private': False,
            'category': 'Spor Salonu'
        }
    ]
    
    created_count = 0
    for data in test_data:
        insta_obj, created = InstagramData.objects.get_or_create(
            username=data['username'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✓ Instagram data created: {data['username']}")
    
    print(f"Created {created_count} new Instagram data entries")

def create_test_facebook_data():
    """Test Facebook verileri oluştur"""
    test_data = [
        {
            'page_name': 'İstanbul Kafe',
            'page_url': 'https://facebook.com/istanbulkafe',
            'description': 'İstanbul\'un kalbi Sultanahmet\'te tarihi atmosferde kahve keyfi',
            'likes_count': 12450,
            'followers_count': 13200,
            'phone': '+90 212 123 4567',
            'email': 'info@istanbulkafe.com',
            'website': 'https://istanbulkafe.com',
            'address': 'Sultanahmet Mah. Divanyolu Cad. No:45 Fatih/İstanbul',
            'category': 'Kahvehane',
            'is_verified': True
        },
        {
            'page_name': 'Teknoloji Mağazası',
            'page_url': 'https://facebook.com/teknomagazasi',
            'description': 'En yeni teknoloji ürünleri, uygun fiyatlar ve kaliteli hizmet',
            'likes_count': 5672,
            'followers_count': 6123,
            'phone': '+90 216 789 0123',
            'email': 'satis@teknomagazasi.com',
            'website': 'https://teknomagazasi.com',
            'address': 'Ataşehir Mah. Atatürk Bulvarı No:123 Ataşehir/İstanbul',
            'category': 'Elektronik',
            'is_verified': False
        }
    ]
    
    created_count = 0
    for data in test_data:
        fb_obj, created = FacebookData.objects.get_or_create(
            page_name=data['page_name'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✓ Facebook data created: {data['page_name']}")
    
    print(f"Created {created_count} new Facebook data entries")

def create_test_twitter_data():
    """Test Twitter verileri oluştur"""
    test_data = [
        {
            'username': 'istanbulnews',
            'display_name': 'İstanbul News',
            'bio': 'İstanbul\'dan son dakika haberleri ve gelişmeler 📰 #İstanbul #Haber',
            'followers_count': 45230,
            'following_count': 1890,
            'tweets_count': 12450,
            'location': 'İstanbul, Turkey',
            'website': 'https://istanbulnews.com',
            'is_verified': True,
            'is_private': False
        },
        {
            'username': 'coffeelover_ist',
            'display_name': 'Coffee Lover Istanbul',
            'bio': '☕ İstanbul\'un en iyi kahve mekanları | Kahve tutkunu',
            'followers_count': 8934,
            'following_count': 567,
            'tweets_count': 3421,
            'location': 'İstanbul',
            'website': 'https://coffeeguide.istanbul',
            'is_verified': False,
            'is_private': False
        }
    ]
    
    created_count = 0
    for data in test_data:
        twitter_obj, created = TwitterData.objects.get_or_create(
            username=data['username'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✓ Twitter data created: {data['username']}")
    
    print(f"Created {created_count} new Twitter data entries")

def create_test_linkedin_data():
    """Test LinkedIn verileri oluştur"""
    test_data = [
        {
            'profile_name': 'Tech Solutions Istanbul',
            'headline': 'Software Development Company',
            'summary': 'İstanbul merkezli yazılım geliştirme ve danışmanlık firması. Modern teknolojilerle çözümler üretiyoruz.',
            'connections_count': 2340,
            'profile_url': 'https://linkedin.com/company/tech-solutions-istanbul',
            'location': 'İstanbul, Turkey',
            'industry': 'Bilgi Teknolojileri',
            'current_company': 'Tech Solutions Istanbul',
            'current_position': 'CEO & Founder',
            'experience_years': 8
        },
        {
            'profile_name': 'Digital Marketing Pro',
            'headline': 'Digital Marketing Specialist',
            'summary': 'Dijital pazarlama stratejileri ve sosyal medya yönetimi konusunda uzman. 5+ yıl deneyim.',
            'connections_count': 1567,
            'profile_url': 'https://linkedin.com/company/digital-marketing-pro',
            'location': 'İstanbul, Turkey',
            'industry': 'Pazarlama ve Reklamcılık',
            'current_company': 'Digital Marketing Pro',
            'current_position': 'Marketing Director',
            'experience_years': 5
        }
    ]
    
    created_count = 0
    for data in test_data:
        linkedin_obj, created = LinkedInData.objects.get_or_create(
            profile_name=data['profile_name'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✓ LinkedIn data created: {data['profile_name']}")
    
    print(f"Created {created_count} new LinkedIn data entries")

def create_test_tiktok_data():
    """Test TikTok verileri oluştur"""
    test_data = [
        {
            'username': 'istanbulfood',
            'display_name': 'Istanbul Food',
            'bio': '🍽️ İstanbul\'un en lezzetli yemekleri | Food blogger',
            'followers_count': 234500,
            'following_count': 890,
            'likes_count': 5670000,
            'videos_count': 456,
            'is_verified': True,
            'is_private': False,
            'external_url': 'https://istanbulfood.com'
        },
        {
            'username': 'istanbul_travel',
            'display_name': 'Istanbul Travel Guide',
            'bio': '🏛️ İstanbul\'u keşfet | Gezi rehberi',
            'followers_count': 156700,
            'following_count': 234,
            'likes_count': 2340000,
            'videos_count': 289,
            'is_verified': False,
            'is_private': False,
            'external_url': 'https://istanbultravel.com'
        }
    ]
    
    created_count = 0
    for data in test_data:
        tiktok_obj, created = TikTokData.objects.get_or_create(
            username=data['username'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✓ TikTok data created: {data['username']}")
    
    print(f"Created {created_count} new TikTok data entries")

def create_test_scraping_jobs():
    """Test scraping job'ları oluştur"""
    try:
        test_user = User.objects.get(username='test')
    except User.DoesNotExist:
        print("Test kullanıcısı bulunamadı, oluşturuluyor...")
        test_user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='test123'
        )
    
    job_types = ['Map Scraping', 'Instagram Scraping', 'Facebook Scraping', 'Twitter Scraping', 'LinkedIn Scraping', 'TikTok Scraping']
    statuses = ['completed', 'completed', 'completed', 'running', 'failed']
    
    created_count = 0
    for i in range(10):
        job_type = random.choice(job_types)
        status = random.choice(statuses)
        
        # Geçmiş tarihler oluştur
        days_ago = random.randint(1, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        job = ScrapingJob.objects.create(
            user=test_user,
            query=f"{job_type} - Test Query {i+1}",
            status=status,
            created_at=created_at
        )
        created_count += 1
        print(f"✓ Scraping job created: {job.query}")
    
    print(f"Created {created_count} new scraping jobs")

def main():
    print("🚀 Test verilerini oluşturuyor...")
    print("=" * 50)
    
    try:
        create_test_map_data()
        print()
        
        create_test_instagram_data()
        print()
        
        create_test_facebook_data()
        print()
        
        create_test_twitter_data()
        print()
        
        create_test_linkedin_data()
        print()
        
        create_test_tiktok_data()
        print()
        
        create_test_scraping_jobs()
        print()
        
        print("=" * 50)
        print("✅ Tüm test verileri başarıyla oluşturuldu!")
        
        # Toplam veri sayıları
        print("\n📊 Veri Sayıları:")
        print(f"Map Data: {MapData.objects.count()}")
        print(f"Instagram Data: {InstagramData.objects.count()}")
        print(f"Facebook Data: {FacebookData.objects.count()}")
        print(f"Twitter Data: {TwitterData.objects.count()}")
        print(f"LinkedIn Data: {LinkedInData.objects.count()}")
        print(f"TikTok Data: {TikTokData.objects.count()}")
        print(f"Scraping Jobs: {ScrapingJob.objects.count()}")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
