from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from .. import models

SLUG = 'test-slug'
TEXT = 'Тестовый текст'
AUTHOR_USERNAME = 'TestAuthor'
POST_TEXT = 'Тестовый текст'
INDEX_URL = reverse('posts:index')


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = models.User.objects.create_user(username=AUTHOR_USERNAME)
        cls.post = models.Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
        )
        cls.author_client = Client()

    def setUp(self):
        self.guest = Client()

    def test_index_page_cache_contents_post_list(self):
        """Посты главной страницы сохраняются в кеш."""
        response = self.guest.get(INDEX_URL)
        content = response.content.decode()
        self.post.delete()
        response = self.guest.get(INDEX_URL)
        content_after_delete = response.content.decode()
        self.assertEqual(content, content_after_delete)
        cache.clear()
        response = self.guest.get(INDEX_URL)
        content_after_clear = response.content.decode()
        self.assertNotEqual(content_after_delete, content_after_clear)
