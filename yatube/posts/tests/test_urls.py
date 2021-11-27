from django.test import TestCase, Client
from django.urls import reverse

from .. import models

SLUG = 'test-slug'
AUTHOR_USERNAME = 'TestAuthor'
USER_USERNAME = 'TestUser'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
GROUP_LIST_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
UNEXISTING_PAGE_URL = '/unexisting_page/'


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = models.Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.author = models.User.objects.create_user(username=AUTHOR_USERNAME)
        cls.user = models.User.objects.create_user(username=USER_USERNAME)
        cls.post = models.Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id]
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            args=[cls.post.id]
        )
        cls.POST_COMMENT_URL = reverse(
            'posts:add_comment',
            args=[cls.post.id]
        )

    def setUp(self):
        self.guest = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.another = Client()
        self.another.force_login(self.user)

    def test_status_codes(self):
        """Страницы проекта доступны по своим адресам."""
        cases = [
            [INDEX_URL, self.guest, 200],
            [GROUP_LIST_URL, self.guest, 200],
            [PROFILE_URL, self.guest, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            [self.POST_EDIT_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.another, 302],
            [self.POST_EDIT_URL, self.author_client, 200],
            [CREATE_URL, self.guest, 302],
            [CREATE_URL, self.another, 200],
            [UNEXISTING_PAGE_URL, self.guest, 404],
        ]
        for url, client, code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, code)

    def test_create_url_redirect_anonymous_on_auth_login(self):
        """Страницы требующие авторизации перенаправят анонимного
        пользователя на страницу логина.
        """
        cases = [
            [
                self.POST_EDIT_URL,
                self.guest,
                f'{LOGIN_URL}?next={self.POST_EDIT_URL}'
            ],
            [
                self.POST_EDIT_URL,
                self.another,
                self.POST_DETAIL_URL
            ],
            [CREATE_URL, self.guest, f'{LOGIN_URL}?next={CREATE_URL}'],
            [
                self.POST_COMMENT_URL,
                self.guest,
                f'{LOGIN_URL}?next={self.POST_COMMENT_URL}'
            ],
        ]
        for url, client, redirect_url in cases:
            with self.subTest(url=url, client=client):
                self.assertRedirects(
                    client.get(url, follow=True),
                    redirect_url
                )

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_LIST_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            CREATE_URL: 'posts/create_post.html',
        }

        for url, template in templates_pages_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.author_client.get(url),
                    template
                )
