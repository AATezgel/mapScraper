"""
Supabase entegrasyonu için servis dosyası
"""
from supabase import create_client, Client
from django.conf import settings
import json
from typing import List, Dict, Any

class SupabaseService:
    def __init__(self):
        """Supabase client'ı başlatır"""
        self.supabase: Client = None
        self._init_client()
    
    def _init_client(self):
        """Supabase client'ı initialize eder"""
        try:
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                print("Supabase client başarıyla başlatıldı")
            else:
                print("Supabase URL veya KEY tanımlanmamış")
        except Exception as e:
            print(f"Supabase client başlatılırken hata: {e}")
    
    def is_connected(self) -> bool:
        """Supabase bağlantısının aktif olup olmadığını kontrol eder"""
        return self.supabase is not None
    
    def test_connection(self) -> bool:
        """Supabase bağlantısını test eder"""
        if not self.is_connected():
            return False
        
        try:
            # Basit bir test sorgusu yap
            response = self.supabase.table('mapscraper_mapdata').select('id').limit(1).execute()
            return True
        except Exception as e:
            print(f"Supabase bağlantı test hatası: {e}")
            return False
    
    def get_map_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Supabase'den map verilerini çeker
        """
        if not self.is_connected():
            return []
        try:
            try:
                query = self.supabase.table('map_data').select('*')
                if limit > 0:
                    query = query.limit(limit)
                if offset > 0:
                    query = query.offset(offset)
                query = query.order('created_at', desc=True)
                response = query.execute()
                return response.data
            except Exception as e:
                # Eski tablo ismiyle dene
                query = self.supabase.table('mapscraper_mapdata').select('*')
                if limit > 0:
                    query = query.limit(limit)
                if offset > 0:
                    query = query.offset(offset)
                query = query.order('created_at', desc=True)
                response = query.execute()
                return response.data
        except Exception as e:
            print(f"Supabase'den map verisi çekerken hata: {e}")
            return []

    def get_instagram_data(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Instagram verilerini Supabase'den çeker"""
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('instagram_data').select('*')
            
            if limit > 0:
                query = query.limit(limit)
            if offset > 0:
                query = query.offset(offset)
                
            query = query.order('created_at', desc=True)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Supabase'den Instagram verisi çekerken hata: {e}")
            return []

    def get_facebook_data(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Facebook verilerini Supabase'den çeker"""
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('facebook_data').select('*')
            
            if limit > 0:
                query = query.limit(limit)
            if offset > 0:
                query = query.offset(offset)
                
            query = query.order('created_at', desc=True)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Supabase'den Facebook verisi çekerken hata: {e}")
            return []

    def get_twitter_data(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Twitter verilerini Supabase'den çeker"""
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('twitter_data').select('*')
            
            if limit > 0:
                query = query.limit(limit)
            if offset > 0:
                query = query.offset(offset)
                
            query = query.order('created_at', desc=True)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Supabase'den Twitter verisi çekerken hata: {e}")
            return []

    def get_linkedin_data(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """LinkedIn verilerini Supabase'den çeker"""
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('linkedin_data').select('*')
            
            if limit > 0:
                query = query.limit(limit)
            if offset > 0:
                query = query.offset(offset)
                
            query = query.order('created_at', desc=True)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Supabase'den LinkedIn verisi çekerken hata: {e}")
            return []

    def get_tiktok_data(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """TikTok verilerini Supabase'den çeker"""
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('tiktok_data').select('*')
            
            if limit > 0:
                query = query.limit(limit)
            if offset > 0:
                query = query.offset(offset)
                
            query = query.order('created_at', desc=True)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Supabase'den TikTok verisi çekerken hata: {e}")
            return []
    
    def insert_map_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Supabase'e map verilerini ekler
        
        Args:
            data: Eklenecek veri listesi
            
        Returns:
            Dict: İşlem sonucu
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            # Verileri Supabase formatına çevir
            formatted_data = []
            for item in data:
                formatted_item = {
                    'name': item.get('name', ''),
                    'address': item.get('address', ''),
                    'phone': item.get('phone', ''),
                    'website': item.get('website', ''),
                    'rating': item.get('rating'),
                    'reviews_count': item.get('reviews_count'),
                    'latitude': item.get('latitude'),
                    'longitude': item.get('longitude'),
                    'category': item.get('category', ''),
                }
                formatted_data.append(formatted_item)
            
            # Supabase'e ekle
            response = self.supabase.table('mapscraper_mapdata').insert(formatted_data).execute()
            
            return {
                'success': True,
                'inserted_count': len(response.data),
                'data': response.data
            }
            
        except Exception as e:
            print(f"Supabase'e veri eklerken hata: {e}")
            return {'success': False, 'error': str(e)}
    
    def upsert_map_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Supabase'e map verilerini upsert eder (var olan günceller, yeni olanı ekler)
        
        Args:
            data: Upsert edilecek veri listesi
            
        Returns:
            Dict: İşlem sonucu
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            # Verileri Supabase formatına çevir
            formatted_data = []
            for item in data:
                formatted_item = {
                    'name': item.get('name', ''),
                    'address': item.get('address', ''),
                    'phone': item.get('phone', ''),
                    'website': item.get('website', ''),
                    'rating': item.get('rating'),
                    'reviews_count': item.get('reviews_count'),
                    'latitude': item.get('latitude'),
                    'longitude': item.get('longitude'),
                    'category': item.get('category', ''),
                }
                formatted_data.append(formatted_item)
            
            # Supabase'e upsert et (name ve address kombinasyonu unique olarak kabul edelim)
            response = self.supabase.table('mapscraper_mapdata').upsert(
                formatted_data, 
                on_conflict='name,address'
            ).execute()
            
            return {
                'success': True,
                'upserted_count': len(response.data),
                'data': response.data
            }
            
        except Exception as e:
            print(f"Supabase'e veri upsert ederken hata: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_scraping_jobs(self, user_id: int = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Supabase'den scraping job'larını çeker
        
        Args:
            user_id: Kullanıcı ID'si (opsiyonel)
            limit: Çekilecek maksimum veri sayısı
            
        Returns:
            List[Dict]: Scraping jobs listesi
        """
        if not self.is_connected():
            return []
        
        try:
            query = self.supabase.table('mapscraper_scrapingjob').select('*')
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.limit(limit).order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Supabase'den scraping jobs çekerken hata: {e}")
            return []
    
    def create_scraping_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Supabase'de yeni scraping job oluşturur
        
        Args:
            job_data: Job verisi
            
        Returns:
            Dict: İşlem sonucu
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            response = self.supabase.table('mapscraper_scrapingjob').insert(job_data).execute()
            
            return {
                'success': True,
                'job': response.data[0] if response.data else None
            }
            
        except Exception as e:
            print(f"Supabase'de job oluştururken hata: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_scraping_job(self, job_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Supabase'de scraping job'u günceller
        
        Args:
            job_id: Job ID'si
            updates: Güncellenecek alanlar
            
        Returns:
            Dict: İşlem sonucu
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            response = self.supabase.table('mapscraper_scrapingjob').update(updates).eq('id', job_id).execute()
            
            return {
                'success': True,
                'job': response.data[0] if response.data else None
            }
            
        except Exception as e:
            print(f"Supabase'de job güncellerken hata: {e}")
            return {'success': False, 'error': str(e)}
    
    def setup_realtime_sync(self, table_name: str, callback):
        """
        Supabase realtime sync kurulumu
        
        Args:
            table_name: İzlenecek tablo adı
            callback: Değişiklik olduğunda çağrılacak fonksiyon
        """
        if not self.is_connected():
            print("Supabase bağlantısı yok, realtime sync kurulamıyor")
            return
        
        try:
            # Realtime subscription kurulumu
            self.supabase.table(table_name).on('*', callback).subscribe()
            print(f"Realtime sync kuruldu: {table_name}")
        except Exception as e:
            print(f"Realtime sync kurulurken hata: {e}")
    
    def get_all_map_data(self):
        """Tüm map data verilerini Supabase'den çeker"""
        try:
            response = self.supabase.table('mapscraper_mapdata').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Supabase'den tüm veri çekerken hata: {e}")
            return []

    def get_sync_stats(self):
        """Senkronizasyon istatistiklerini döndürür"""
        try:
            # Toplam kayıt sayısı
            all_data = self.get_all_map_data()
            
            # Son job'ları çek
            jobs = self.get_scraping_jobs(limit=10)
            
            return {
                'total_records': len(all_data),
                'recent_jobs': jobs,
                'recent_jobs_count': len(jobs)
            }
        except Exception as e:
            print(f"Stats alınırken hata: {e}")
            return {
                'total_records': 0,
                'recent_jobs': [],
                'recent_jobs_count': 0
            }

    def bulk_upsert_map_data(self, data_list):
        """Toplu upsert işlemi yapar"""
        try:
            created = 0
            updated = 0
            failed = 0
            
            for item in data_list:
                result = self.upsert_map_data([item])
                if result.get('success'):
                    created += result.get('upserted_count', 0)
                else:
                    failed += 1
            
            return {
                'created': created,
                'updated': updated,
                'failed': failed
            }
        except Exception as e:
            print(f"Bulk upsert hatası: {e}")
            return {
                'created': 0,
                'updated': 0,
                'failed': len(data_list)
            }

    # Instagram Data Methods
    def get_instagram_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Supabase'den Instagram verilerini çeker"""
        if not self.is_connected():
            return []
        try:
            response = self.supabase.table('instagram_data').select('*').range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Instagram verileri alınırken hata: {e}")
            return []

    def upsert_instagram_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Instagram verilerini Supabase'e upsert eder"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            response = self.supabase.table('instagram_data').upsert(data_list, on_conflict='username').execute()
            return {
                'success': True,
                'upserted_count': len(response.data) if response.data else 0,
                'data': response.data
            }
        except Exception as e:
            print(f"Instagram upsert hatası: {e}")
            return {'success': False, 'error': str(e)}

    # Facebook Data Methods
    def get_facebook_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Supabase'den Facebook verilerini çeker"""
        if not self.is_connected():
            return []
        try:
            response = self.supabase.table('facebook_data').select('*').range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Facebook verileri alınırken hata: {e}")
            return []

    def upsert_facebook_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Facebook verilerini Supabase'e upsert eder"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            response = self.supabase.table('facebook_data').upsert(data_list, on_conflict='page_name').execute()
            return {
                'success': True,
                'upserted_count': len(response.data) if response.data else 0,
                'data': response.data
            }
        except Exception as e:
            print(f"Facebook upsert hatası: {e}")
            return {'success': False, 'error': str(e)}

    # Twitter Data Methods
    def get_twitter_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Supabase'den Twitter verilerini çeker"""
        if not self.is_connected():
            return []
        try:
            response = self.supabase.table('twitter_data').select('*').range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Twitter verileri alınırken hata: {e}")
            return []

    def upsert_twitter_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Twitter verilerini Supabase'e upsert eder"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            response = self.supabase.table('twitter_data').upsert(data_list, on_conflict='username').execute()
            return {
                'success': True,
                'upserted_count': len(response.data) if response.data else 0,
                'data': response.data
            }
        except Exception as e:
            print(f"Twitter upsert hatası: {e}")
            return {'success': False, 'error': str(e)}

    # LinkedIn Data Methods
    def get_linkedin_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Supabase'den LinkedIn verilerini çeker"""
        if not self.is_connected():
            return []
        try:
            response = self.supabase.table('linkedin_data').select('*').range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"LinkedIn verileri alınırken hata: {e}")
            return []

    def upsert_linkedin_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """LinkedIn verilerini Supabase'e upsert eder"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            response = self.supabase.table('linkedin_data').upsert(data_list, on_conflict='profile_name').execute()
            return {
                'success': True,
                'upserted_count': len(response.data) if response.data else 0,
                'data': response.data
            }
        except Exception as e:
            print(f"LinkedIn upsert hatası: {e}")
            return {'success': False, 'error': str(e)}

    # TikTok Data Methods
    def get_tiktok_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Supabase'den TikTok verilerini çeker"""
        if not self.is_connected():
            return []
        try:
            response = self.supabase.table('tiktok_data').select('*').range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"TikTok verileri alınırken hata: {e}")
            return []

    def upsert_tiktok_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """TikTok verilerini Supabase'e upsert eder"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase bağlantısı yok'}
        
        try:
            response = self.supabase.table('tiktok_data').upsert(data_list, on_conflict='username').execute()
            return {
                'success': True,
                'upserted_count': len(response.data) if response.data else 0,
                'data': response.data
            }
        except Exception as e:
            print(f"TikTok upsert hatası: {e}")
            return {'success': False, 'error': str(e)}


# Global Supabase service instance
supabase_service = SupabaseService()
