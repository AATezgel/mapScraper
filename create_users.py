#!/usr/bin/env python
import os
import sys
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapscraper_project.settings')
django.setup()

from django.contrib.auth.models import User

# Test kullanıcısı oluştur
user, created = User.objects.get_or_create(username='test')
if created:
    user.set_password('test123')
    user.save()
    print('Test kullanıcısı oluşturuldu: test/test123')
else:
    user.set_password('test123')
    user.save()
    print('Test kullanıcısının şifresi güncellendi: test/test123')

# Admin kullanıcısının şifresini de güncelle
try:
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    print('Admin kullanıcısının şifresi güncellendi: admin/admin123')
except User.DoesNotExist:
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin kullanıcısı oluşturuldu: admin/admin123')

print('\nGiriş bilgileri:')
print('Kullanıcı: test, Şifre: test123')
print('Kullanıcı: admin, Şifre: admin123')
