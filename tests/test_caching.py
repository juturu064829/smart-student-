import unittest
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from utils.cache import cache_store, cached, invalidate_cache, clear_all_cache
from models import db, Department

class TestCachingSystem(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['CACHE_ENABLED'] = True
        self.client = self.app.test_client()
        clear_all_cache()

    def tearDown(self):
        clear_all_cache()

    def test_static_asset_cache_headers(self):
        """Requirement 3 & 4: Static assets have proper Cache-Control headers with long max-age and immutability."""
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        cache_header = response.headers.get('Cache-Control', '')
        self.assertIn('public', cache_header)
        self.assertIn('max-age=', cache_header)
        self.assertIn('immutable', cache_header)

    def test_sensitive_endpoints_no_cache_headers(self):
        """Requirement 6: Sensitive/authenticated endpoints have no-store/no-cache headers to protect user privacy."""
        # Login page
        res_login = self.client.get('/login')
        cache_header = res_login.headers.get('Cache-Control', '')
        self.assertIn('no-store', cache_header)
        self.assertIn('no-cache', cache_header)
        self.assertIn('private', cache_header)
        self.assertEqual(res_login.headers.get('Pragma'), 'no-cache')

    def test_in_memory_cache_hit_and_miss(self):
        """Requirement 2 & 5: In-memory cache stores and retrieves values with TTL."""
        cache_store.set('test_key', {'data': 123}, ttl=10)
        self.assertEqual(cache_store.get('test_key'), {'data': 123})
        self.assertIsNone(cache_store.get('non_existent_key'))

    def test_cache_ttl_expiration(self):
        """Requirement 5: Cache expires after configured TTL."""
        cache_store.set('short_ttl_key', 'hello', ttl=1)
        self.assertEqual(cache_store.get('short_ttl_key'), 'hello')
        time.sleep(1.2)
        self.assertIsNone(cache_store.get('short_ttl_key'))

    def test_cache_invalidation_on_mutation(self):
        """Requirement 7: Cache is automatically invalidated when data is updated."""
        cache_store.set('api_departments:1', [{'name': 'Computer Science'}], ttl=60)
        cache_store.set('api_departments:2', [{'name': 'Electrical Eng'}], ttl=60)
        cache_store.set('other_data:1', 'keep_this', ttl=60)

        self.assertIsNotNone(cache_store.get('api_departments:1'))
        self.assertIsNotNone(cache_store.get('api_departments:2'))

        # Invalidate department cache
        invalidate_cache('api_departments')

        self.assertIsNone(cache_store.get('api_departments:1'))
        self.assertIsNone(cache_store.get('api_departments:2'))
        self.assertEqual(cache_store.get('other_data:1'), 'keep_this')

    def test_cached_api_endpoint(self):
        """Requirement 5: Public API endpoints utilize caching."""
        res1 = self.client.get('/api/v1/departments')
        self.assertEqual(res1.status_code, 200)

        res2 = self.client.get('/api/v1/departments')
        self.assertEqual(res2.status_code, 200)

        stats = cache_store.get_stats()
        self.assertGreaterEqual(stats['hits'], 1)

    def test_cache_busting_versioning(self):
        """Requirement 9: Static files are served with versioned cache-busting query strings in HTML."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('/static/css/style.css?v=', html)

if __name__ == '__main__':
    unittest.main()
