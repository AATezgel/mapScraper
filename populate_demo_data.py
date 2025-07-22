"""
Django veritabanında demo veriler oluşturmak için script
"""
import os
import sys
import django
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from mapscraper.models import *

def create_demo_data():
    """Demo verilerini Django veritabanında oluşturur"""
    print("🚀 Demo veriler oluşturuluyor...")
    
    # Kullanıcı oluştur (eğer yoksa)
    user, created = User.objects.get_or_create(
        username='admin', 
        defaults={
            'email': 'admin@test.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print('✅ Admin kullanıcı oluşturuldu')
    
    # Map data oluştur
    MapData.objects.all().delete()
    map_data = [
        {
            'name': 'Cafe İstanbul',
            'category': 'Kafe',
            'rating': 4.5,
            'reviews_count': 234,
            'phone': '0212 123 4567',
            'address': 'Beyoğlu, İstanbul',
        },
        {
            'name': 'Teknoloji Mağazası',
            'category': 'Elektronik',
            'rating': 4.2,
            'reviews_count': 189,
            'phone': '0312 456 7890',
            'address': 'Çankaya, Ankara',
        },
        {
            'name': 'Spor Salonu',
            'category': 'Fitness',
            'rating': 4.7,
            'reviews_count': 456,
            'phone': '0232 789 0123',
            'address': 'Konak, İzmir',
        },
        {
            'name': 'Restoran Lezzet',
            'category': 'Restoran',
            'rating': 4.3,
            'reviews_count': 312,
            'phone': '0224 345 6789',
            'address': 'Nilüfer, Bursa',
        },
        {
            'name': 'Kuaför Salon',
            'category': 'Güzellik',
            'rating': 4.6,
            'reviews_count': 167,
            'phone': '0242 678 9012',
            'address': 'Muratpaşa, Antalya',
        }
    ]
    
    for data in map_data:
        MapData.objects.create(**data)
    
    print(f'✅ {len(map_data)} Map verisi oluşturuldu')
    
    # Instagram data oluştur
    InstagramData.objects.all().delete()
    instagram_data = [
        {
            'username': 'teknoloji_rehberi',
            'full_name': 'Teknoloji Rehberi',
            'bio': 'En son teknoloji haberleri ve incelemeler',
            'followers_count': 234000,
            'following_count': 1200,
            'posts_count': 456,
            'is_verified': True,
            'category': 'Teknoloji',
        },
        {
            'username': 'yemek_dunyasi',
            'full_name': 'Yemek Dünyası',
            'bio': 'Lezzetli tarifler ve restoran önerileri',
            'followers_count': 189000,
            'following_count': 890,
            'posts_count': 1200,
            'is_verified': False,
            'category': 'Yemek',
        },
        {
            'username': 'spor_motivasyon',
            'full_name': 'Spor Motivasyon',
            'bio': 'Günlük antrenman ve motivasyon',
            'followers_count': 345000,
            'following_count': 567,
            'posts_count': 789,
            'is_verified': True,
            'category': 'Spor',
        },
        {
            'username': 'seyahat_gunlugu',
            'full_name': 'Seyahat Günlüğü',
            'bio': 'Dünyadan seyahat deneyimleri',
            'followers_count': 123000,
            'following_count': 2100,
            'posts_count': 678,
            'is_verified': False,
            'category': 'Seyahat',
        },
        {
            'username': 'moda_trendleri',
            'full_name': 'Moda Trendleri',
            'bio': 'En son moda trendleri ve stil önerileri',
            'followers_count': 456000,
            'following_count': 1800,
            'posts_count': 2100,
            'is_verified': True,
            'category': 'Moda',
        }
    ]
    
    for data in instagram_data:
        InstagramData.objects.create(**data)
    
    print(f'✅ {len(instagram_data)} Instagram verisi oluşturuldu')
    
    # Facebook data oluştur
    FacebookData.objects.all().delete()
    facebook_data = [
        {
            'page_name': 'Teknoloji Dünyası',
            'description': 'Teknoloji haberlerinin merkezi',
            'likes_count': 125000,
            'followers_count': 142000,
            'category': 'Teknoloji',
            'phone': '0212 123 4567',
            'website': 'https://teknolojidunyasi.com',
            'address': 'Istanbul',
            'is_verified': True,
        },
        {
            'page_name': 'Yemek Tarifleri',
            'description': 'Ev yapımı lezzetli tarifler',
            'likes_count': 89000,
            'followers_count': 95000,
            'category': 'Yemek & İçecek',
            'phone': '0312 456 7890',
            'website': 'https://yemektarifleri.com',
            'address': 'Ankara',
            'is_verified': False,
        },
        {
            'page_name': 'Spor Haberleri',
            'description': 'Türkiye ve dünyadan spor haberleri',
            'likes_count': 203000,
            'followers_count': 225000,
            'category': 'Spor',
            'website': 'https://sporhaberleri.com',
            'address': 'Istanbul',
            'is_verified': True,
        },
        {
            'page_name': 'Gezi Rehberi',
            'description': 'Türkiye turları ve seyahat tavsiyeleri',
            'likes_count': 67000,
            'followers_count': 73000,
            'category': 'Seyahat',
            'website': 'https://gezirehberi.com',
            'address': 'Izmir',
            'is_verified': False,
        },
        {
            'page_name': 'Moda Trendleri',
            'description': 'En güncel moda haberleri',
            'likes_count': 156000,
            'followers_count': 178000,
            'category': 'Moda & Güzellik',
            'website': 'https://modatrendleri.com',
            'address': 'Istanbul',
            'is_verified': True,
        }
    ]
    
    for data in facebook_data:
        FacebookData.objects.create(**data)
    
    print(f'✅ {len(facebook_data)} Facebook verisi oluşturuldu')
    
    # Twitter data oluştur
    TwitterData.objects.all().delete()
    twitter_data = [
        {
            'username': 'istanbul_daily',
            'display_name': 'Istanbul Daily News',
            'bio': 'Daily news from Istanbul',
            'followers_count': 234000,
            'following_count': 1200,
            'tweets_count': 15600,
            'is_verified': True,
            'location': 'Istanbul',
        },
        {
            'username': 'turkish_tech',
            'display_name': 'Turkish Tech Community',
            'bio': 'Technology community in Turkey',
            'followers_count': 89000,
            'following_count': 567,
            'tweets_count': 8900,
            'is_verified': False,
            'location': 'Ankara',
        },
        {
            'username': 'bosphorus_view',
            'display_name': 'Bosphorus View',
            'bio': 'Beautiful views of Bosphorus',
            'followers_count': 156000,
            'following_count': 234,
            'tweets_count': 12300,
            'is_verified': True,
            'location': 'Istanbul',
        },
        {
            'username': 'turkish_cuisine',
            'display_name': 'Turkish Cuisine',
            'bio': 'Traditional Turkish food recipes',
            'followers_count': 78000,
            'following_count': 445,
            'tweets_count': 5400,
            'is_verified': False,
            'location': 'Izmir',
        },
        {
            'username': 'ankara_events',
            'display_name': 'Ankara Events',
            'bio': 'Events happening in Ankara',
            'followers_count': 45000,
            'following_count': 678,
            'tweets_count': 3200,
            'is_verified': False,
            'location': 'Ankara',
        }
    ]
    
    for data in twitter_data:
        TwitterData.objects.create(**data)
    
    print(f'✅ {len(twitter_data)} Twitter verisi oluşturuldu')
    
    # LinkedIn data oluştur
    LinkedInData.objects.all().delete()
    linkedin_data = [
        {
            'profile_name': 'Ahmet Yılmaz',
            'headline': 'Software Engineer at Turkish Airlines',
            'current_company': 'Turkish Airlines',
            'current_position': 'Software Engineer',
            'connections_count': 1200,
            'experience_years': 8,
            'industry': 'Aviation',
            'location': 'Istanbul',
        },
        {
            'profile_name': 'Elif Demir',
            'headline': 'Data Scientist at Turkcell',
            'current_company': 'Turkcell',
            'current_position': 'Data Scientist',
            'connections_count': 890,
            'experience_years': 5,
            'industry': 'Telecommunications',
            'location': 'Ankara',
        },
        {
            'profile_name': 'Mehmet Kaya',
            'headline': 'Product Manager at Garanti BBVA',
            'current_company': 'Garanti BBVA',
            'current_position': 'Product Manager',
            'connections_count': 1500,
            'experience_years': 12,
            'industry': 'Finance',
            'location': 'Istanbul',
        },
        {
            'profile_name': 'Zeynep Özkan',
            'headline': 'UX Designer at Trendyol',
            'current_company': 'Trendyol',
            'current_position': 'UX Designer',
            'connections_count': 734,
            'experience_years': 6,
            'industry': 'E-commerce',
            'location': 'Istanbul',
        },
        {
            'profile_name': 'Can Erdoğan',
            'headline': 'Marketing Manager at Getir',
            'current_company': 'Getir',
            'current_position': 'Marketing Manager',
            'connections_count': 2100,
            'experience_years': 7,
            'industry': 'Technology',
            'location': 'Istanbul',
        }
    ]
    
    for data in linkedin_data:
        LinkedInData.objects.create(**data)
    
    print(f'✅ {len(linkedin_data)} LinkedIn verisi oluşturuldu')
    
    # TikTok data oluştur
    TikTokData.objects.all().delete()
    tiktok_data = [
        {
            'username': 'yemekkanalim',
            'display_name': 'Yemek Kanalım',
            'bio': 'En lezzetli tarifler burada',
            'followers_count': 2300000,
            'following_count': 1200,
            'likes_count': 45600000,
            'videos_count': 1200,
            'is_verified': True,
        },
        {
            'username': 'dansci_murat',
            'display_name': 'Dansçı Murat',
            'bio': 'Dans ve eğlence',
            'followers_count': 890000,
            'following_count': 567,
            'likes_count': 23400000,
            'videos_count': 567,
            'is_verified': False,
        },
        {
            'username': 'teknoaliinfo',
            'display_name': 'TeknoAli',
            'bio': 'Teknoloji ve telefon incelemeleri',
            'followers_count': 1500000,
            'following_count': 789,
            'likes_count': 34200000,
            'videos_count': 890,
            'is_verified': True,
        },
        {
            'username': 'komeditime',
            'display_name': 'Komedi Time',
            'bio': 'Günlük komedi içerikleri',
            'followers_count': 3100000,
            'following_count': 234,
            'likes_count': 67800000,
            'videos_count': 2300,
            'is_verified': True,
        },
        {
            'username': 'seyahattutkusu',
            'display_name': 'Seyahat Tutkusu',
            'bio': 'Dünyayı gezip görmeyi seviyorum',
            'followers_count': 756000,
            'following_count': 1800,
            'likes_count': 18900000,
            'videos_count': 423,
            'is_verified': False,
        }
    ]
    
    for data in tiktok_data:
        TikTokData.objects.create(**data)
    
    print(f'✅ {len(tiktok_data)} TikTok verisi oluşturuldu')
    
    print("\n🎉 Tüm demo veriler Django veritabanında başarıyla oluşturuldu!")
    print("📝 Admin kullanıcı: admin / admin123")
    print("🔍 Şimdi tüm scraper sayfalarında veriler görünecek")

if __name__ == "__main__":
    create_demo_data()
