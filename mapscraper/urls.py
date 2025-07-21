from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('map-scraper/', views.map_scraper_view, name='map_scraper'),
    path('settings/', views.settings_view, name='settings'),
    path('api/trigger-n8n/', views.trigger_n8n_api, name='trigger_n8n'),
    path('api/map-data/', views.get_map_data, name='get_map_data'),
    path('api/receive-n8n-data/', views.receive_n8n_data, name='receive_n8n_data'),
    path('api/test-n8n-webhook/', views.test_n8n_webhook, name='test_n8n_webhook'),
    # Supabase endpoints
    path('api/add-map-data/', views.add_map_data, name='add_map_data'),
    path('api/manual-sync-supabase/', views.manual_sync_supabase, name='manual_sync_supabase'),
    path('api/supabase-stats/', views.get_supabase_stats, name='get_supabase_stats'),
]
