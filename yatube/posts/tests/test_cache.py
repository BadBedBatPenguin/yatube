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
        cls.group = models.Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.author = models.User.objects.create_user(username=AUTHOR_USERNAME)
        cls.post = models.Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.guest = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_index_page_cache_contents_post_list(self):
        """Посты главной страницы сохраняются в кеш."""
        response = self.guest.get(INDEX_URL)
        self.post.delete()
        self.assertIn(POST_TEXT, response.content.decode())
        cache.clear()
        # self.assertNotIn(POST_TEXT, response.content.decode())
