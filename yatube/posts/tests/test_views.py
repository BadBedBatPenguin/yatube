import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .. import models

SLUG = 'test-slug'
SLUG_2 = 'test-slug-2'
AUTHOR_USERNAME = 'TestAuthor'
ANOTHER_USERNAME = 'TestAnother'
INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', args=[SLUG])
SECOND_GROUP_LIST_URL = reverse('posts:group_list', args=[SLUG_2])
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
FOLLOW_AUTHOR_URL = reverse('posts:profile_follow', args=[AUTHOR_USERNAME])
UNFOLLOW_AUTHOR_URL = reverse('posts:profile_unfollow', args=[AUTHOR_USERNAME])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = models.Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.second_group = models.Group.objects.create(
            title='Тестовый заголовок 2',
            slug=SLUG_2,
            description='Тестовое описание 2'
        )
        cls.author = models.User.objects.create_user(username=AUTHOR_USERNAME)
        cls.another = models.User.objects.create_user(
            username=ANOTHER_USERNAME
        )
        cls.post = models.Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
            image=UPLOADED,
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id}
        )
        cls.guest_client = Client()
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.authorized_another = Client()
        cls.authorized_another.force_login(cls.another)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_pages_show_correct_context(self):
        """Шаблоны приложения сформированы с правильным контекстом."""
        urls = [
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL,
            self.POST_DETAIL_URL,
            FOLLOW_INDEX_URL,

        ]
        models.Follow.objects.create(user=self.another, author=self.author)
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_another.get(url)
                if 'page_obj' in response.context:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                else:
                    post = response.context['post']
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image, self.post.image)
                self.assertEqual(post.id, self.post.id)

    def test_group_list_page_show_correct_context(self):
        """В шаблон страницы group_list передана правильная группа."""
        response = self.authorized_author.get(GROUP_LIST_URL)
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.id, self.group.id)

    def test_profile_page_show_correct_context(self):
        """В шаблон страницы profile передан правильный пользователь."""
        response = self.authorized_author.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.author)

    def test_post_is_not_shown_in_wrong_group(self):
        """Проверяем не отображается ли новый пост
        в другой группе
        """
        response = self.guest_client.get(SECOND_GROUP_LIST_URL)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_follow(self):
        """Проверяем появляется ли подписка после подписки
        """
        self.authorized_another.get(
            FOLLOW_AUTHOR_URL,
            follow=True
        )
        self.assertTrue(models.Follow.objects.filter(
            user=self.another,
            author=self.author
        ).exists())

    def test_unfollow(self):
        """Проверяем удаляется ли подписка после отписки
        """
        models.Follow.objects.create(user=self.another, author=self.author)
        self.authorized_another.get(
            UNFOLLOW_AUTHOR_URL,
            follow=True
        )
        self.assertFalse(models.Follow.objects.filter(
            user=self.another,
            author=self.author
        ).exists())

    def test_new_post_is_not_shown_on_wrong_follow_index(self):
        """Проверяем что новые посты не показываются в ленте
        тех кто не подписан
        """
        models.Follow.objects.create(user=self.another, author=self.author)
        new_post = models.Post.objects.create(
            text='Тестовый текст',
            author=self.author,
            group=self.group,
        )
        response = self.authorized_author.get(FOLLOW_INDEX_URL)
        self.assertNotIn(new_post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = models.Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.author = models.User.objects.create_user(username='TestAuthor')
        post_list = [models.Post(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )] * (settings.POSTS_PER_PAGE + 1)

        models.Post.objects.bulk_create(post_list)
        cls.guest_client = Client()
        cls.URLS = [
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL
        ]

    def test_first_page_contains_right_number_of_records(self):
        """Проверка первой страницы пагинатора."""
        for url in self.URLS:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_PER_PAGE
                )

    def test_second_page_contains_right_number_of_records(self):
        """Проверка второй страницы пагинатора."""
        for url in self.URLS:
            with self.subTest(url=url):
                response = self.guest_client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 1)
