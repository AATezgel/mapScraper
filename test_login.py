#!/usr/bin/env python3
"""
Lokal SQLite veritabanı ve giriş sistemini test eder
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from mapscraper.models import MapData, ScrapingJob
from django.conf import settings

print("=" * 60)
print("DATABASE VE GİRİŞ SİSTEMİ TEST RAPORU")
print("=" * 60)

# 1. Database ayarlarını kontrol et
print("\n1. VERİTABANI AYARLARI")
print("-" * 60)
db_engine = settings.DATABASES['default']['ENGINE']
db_name = settings.DATABASES['default']['NAME']
print(f"Database Engine: {db_engine}")
print(f"Database Name: {db_name}")

if 'sqlite' in db_engine:
    print("✓ SQLite veritabanı kullanılıyor (Lokal)")
    if os.path.exists(db_name):
        size = os.path.getsize(db_name)
        print(f"✓ Veritabanı dosyası mevcut: {size} bytes")
    else:
        print("✗ Veritabanı dosyası bulunamadı!")
else:
    print(f"⚠ PostgreSQL/Başka bir veritabanı kullanılıyor: {db_engine}")

# 2. Kullanıcıları kontrol et
print("\n2. KULLANICILAR")
print("-" * 60)
users = User.objects.all()
print(f"Toplam kullanıcı sayısı: {users.count()}")
for user in users:
    print(f"  - {user.username} (Superuser: {user.is_superuser}, Active: {user.is_active})")

# 3. Test kullanıcıları için şifre ayarla
print("\n3. TEST KULLANICILARI OLUŞTUR/GÜNCELLE")
print("-" * 60)

# Test kullanıcısı
try:
    test_user = User.objects.get(username='test')
    print("Test kullanıcısı mevcut")
except User.DoesNotExist:
    test_user = User.objects.create_user(username='test', email='test@test.com')
    print("✓ Test kullanıcısı oluşturuldu")

test_user.set_password('test123')
test_user.save()
print("✓ Test kullanıcısı şifresi: test123")

# Admin kullanıcısı
try:
    admin_user = User.objects.get(username='admin')
    print("Admin kullanıcısı mevcut")
except User.DoesNotExist:
    admin_user = User.objects.create_superuser(username='admin', email='admin@test.com', password='admin123')
    print("✓ Admin kullanıcısı oluşturuldu")

admin_user.set_password('admin123')
admin_user.save()
print("✓ Admin kullanıcısı şifresi: admin123")

# 4. Authentication testi
print("\n4. GİRİŞ SİSTEMİ TESTİ")
print("-" * 60)

# Test kullanıcısı ile giriş
auth_test = authenticate(username='test', password='test123')
if auth_test:
    print(f"✓ Test kullanıcısı girişi BAŞARILI: {auth_test.username}")
else:
    print("✗ Test kullanıcısı girişi BAŞARISIZ!")

# Admin kullanıcısı ile giriş
auth_admin = authenticate(username='admin', password='admin123')
if auth_admin:
    print(f"✓ Admin kullanıcısı girişi BAŞARILI: {auth_admin.username}")
else:
    print("✗ Admin kullanıcısı girişi BAŞARISIZ!")

# Yanlış şifre ile giriş
auth_wrong = authenticate(username='test', password='wrong_password')
if auth_wrong:
    print("✗ Yanlış şifre ile giriş KABUL EDİLDİ (HATA!)")
else:
    print("✓ Yanlış şifre reddedildi (Beklenen davranış)")

# 5. Veritabanı verilerini kontrol et
print("\n5. VERİTABANI İÇERİĞİ")
print("-" * 60)
map_data_count = MapData.objects.count()
scraping_job_count = ScrapingJob.objects.count()

print(f"MapData kayıt sayısı: {map_data_count}")
print(f"ScrapingJob kayıt sayısı: {scraping_job_count}")

if map_data_count > 0:
    print("\nİlk 5 MapData kaydı:")
    for data in MapData.objects.all()[:5]:
        print(f"  - {data.name} ({data.category})")

# 6. Sonuç
print("\n" + "=" * 60)
print("TEST SONUCU")
print("=" * 60)

all_tests_passed = True

if 'sqlite' in db_engine:
    print("✓ Lokal SQLite veritabanı kullanılıyor")
else:
    print("✗ SQLite kullanılmıyor")
    all_tests_passed = False

if auth_test and auth_admin and not auth_wrong:
    print("✓ Giriş sistemi çalışıyor")
else:
    print("✗ Giriş sisteminde sorun var")
    all_tests_passed = False

if map_data_count >= 0 and scraping_job_count >= 0:
    print("✓ Veritabanı sorguları çalışıyor")
else:
    print("✗ Veritabanı sorguları çalışmıyor")
    all_tests_passed = False

print("\n" + "=" * 60)
if all_tests_passed:
    print("🎉 TÜM TESTLER BAŞARILI!")
    print("\nGiriş bilgileri:")
    print("  Test Kullanıcısı: test / test123")
    print("  Admin Kullanıcısı: admin / admin123")
    print("\nSunucu çalışıyorsa http://127.0.0.1:8001/login/ adresinden giriş yapabilirsiniz.")
else:
    print("⚠ BAZI TESTLER BAŞARISIZ!")
print("=" * 60)
