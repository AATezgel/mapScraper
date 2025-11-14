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
    path('api/test-serp-api/', views.test_n8n_webhook, name='test_serp_api'),
    path('api/add-map-data/', views.add_map_data, name='add_map_data'),
    
    # Instagram Scraper APIs
    path('api/trigger-instagram-scraper/', views.trigger_instagram_scraper, name='trigger_instagram_scraper'),
    path('api/instagram-data/', views.get_instagram_data, name='get_instagram_data'),
    path('api/instagram-webhook/', views.instagram_webhook, name='instagram_webhook'),
    
    # Facebook Scraper APIs
    path('api/trigger-facebook-scraper/', views.trigger_facebook_scraper, name='trigger_facebook_scraper'),
    path('api/facebook-data/', views.get_facebook_data, name='get_facebook_data'),
    path('api/facebook-webhook/', views.facebook_webhook, name='facebook_webhook'),
    
    # Twitter Scraper APIs
    path('api/trigger-twitter-scraper/', views.trigger_twitter_scraper, name='trigger_twitter_scraper'),
    path('api/twitter-data/', views.get_twitter_data, name='get_twitter_data'),
    path('api/twitter-webhook/', views.twitter_webhook, name='twitter_webhook'),
    
    # LinkedIn Scraper APIs
    path('api/trigger-linkedin-scraper/', views.trigger_linkedin_scraper, name='trigger_linkedin_scraper'),
    path('api/linkedin-data/', views.get_linkedin_data, name='get_linkedin_data'),
    path('api/linkedin-webhook/', views.linkedin_webhook, name='linkedin_webhook'),
    
    # TikTok Scraper APIs
    path('api/trigger-tiktok-scraper/', views.trigger_tiktok_scraper, name='trigger_tiktok_scraper'),
    path('api/tiktok-data/', views.get_tiktok_data, name='get_tiktok_data'),
    path('api/tiktok-webhook/', views.tiktok_webhook, name='tiktok_webhook'),
]
