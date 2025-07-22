from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Scraper Pages
    path('map-scraper/', views.map_scraper_view, name='map_scraper'),
    path('instagram-scraper/', views.instagram_scraper_view, name='instagram_scraper'),
    path('facebook-scraper/', views.facebook_scraper_view, name='facebook_scraper'),
    path('twitter-scraper/', views.twitter_scraper_view, name='twitter_scraper'),
    path('linkedin-scraper/', views.linkedin_scraper_view, name='linkedin_scraper'),
    path('tiktok-scraper/', views.tiktok_scraper_view, name='tiktok_scraper'),
    
    path('settings/', views.settings_view, name='settings'),
    
    # Map Scraper APIs
    path('api/trigger-n8n/', views.trigger_n8n_api, name='trigger_n8n'),
    path('api/map-data/', views.get_map_data, name='get_map_data'),
    path('api/receive-n8n-data/', views.receive_n8n_data, name='receive_n8n_data'),
    path('api/test-n8n-webhook/', views.test_n8n_webhook, name='test_n8n_webhook'),
    
    # Instagram Scraper APIs
    path('api/trigger-instagram-scraper/', views.trigger_instagram_scraper, name='trigger_instagram_scraper'),
    path('api/instagram-data/', views.get_instagram_data, name='get_instagram_data'),
    path('api/instagram-webhook/', views.instagram_webhook, name='instagram_webhook'),
    path('api/test-instagram-webhook/', views.test_instagram_webhook, name='test_instagram_webhook'),
    
    # Facebook Scraper APIs
    path('api/trigger-facebook-scraper/', views.trigger_facebook_scraper, name='trigger_facebook_scraper'),
    path('api/facebook-data/', views.get_facebook_data, name='get_facebook_data'),
    path('api/facebook-webhook/', views.facebook_webhook, name='facebook_webhook'),
    path('api/test-facebook-webhook/', views.test_facebook_webhook, name='test_facebook_webhook'),
    
    # Twitter Scraper APIs
    path('api/trigger-twitter-scraper/', views.trigger_twitter_scraper, name='trigger_twitter_scraper'),
    path('api/twitter-data/', views.get_twitter_data, name='get_twitter_data'),
    path('api/twitter-webhook/', views.twitter_webhook, name='twitter_webhook'),
    path('api/test-twitter-webhook/', views.test_twitter_webhook, name='test_twitter_webhook'),
    
    # LinkedIn Scraper APIs
    path('api/trigger-linkedin-scraper/', views.trigger_linkedin_scraper, name='trigger_linkedin_scraper'),
    path('api/linkedin-data/', views.get_linkedin_data, name='get_linkedin_data'),
    path('api/linkedin-webhook/', views.linkedin_webhook, name='linkedin_webhook'),
    path('api/test-linkedin-webhook/', views.test_linkedin_webhook, name='test_linkedin_webhook'),
    
    # TikTok Scraper APIs
    path('api/trigger-tiktok-scraper/', views.trigger_tiktok_scraper, name='trigger_tiktok_scraper'),
    path('api/tiktok-data/', views.get_tiktok_data, name='get_tiktok_data'),
    path('api/tiktok-webhook/', views.tiktok_webhook, name='tiktok_webhook'),
    path('api/test-tiktok-webhook/', views.test_tiktok_webhook, name='test_tiktok_webhook'),
    
    # Supabase endpoints
    path('api/add-map-data/', views.add_map_data, name='add_map_data'),
    path('api/manual-sync-supabase/', views.manual_sync_supabase, name='manual_sync_supabase'),
    path('api/supabase-stats/', views.get_supabase_stats, name='get_supabase_stats'),
    
    # Settings APIs
    path('api/settings/supabase/', views.get_supabase_settings, name='get_supabase_settings'),
    path('api/settings/n8n/', views.get_n8n_settings, name='get_n8n_settings'),
    path('api/settings/webhooks/', views.get_webhook_settings, name='get_webhook_settings'),
    path('api/settings/system/', views.get_system_settings, name='get_system_settings'),
    path('api/system/status/', views.get_system_status, name='get_system_status'),
]
