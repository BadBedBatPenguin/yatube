import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .. import models
from ..forms import PostForm

SLUG = 'test-slug'
SLUG_2 = 'test-slug-2'
TEXT_1 = 'Тестовый текст'
TEXT_2 = 'Тестовый текст 2'
TEXT_3 = 'Тестовый текст 3'
COMMENT = 'Тестовый комментарий'
AUTHOR_USERNAME = 'TestAuthor'
NONAUTHOR_USERNAME = 'TestNonauthor'
CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
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
COMMENT_FORM_DATA = {
    'text': COMMENT,
}


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = models.Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.group_2 = models.Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG_2,
            description='Тестовое описание'
        )
        cls.author = models.User.objects.create_user(username=AUTHOR_USERNAME)
        cls.nonauthor = models.User.objects.create_user(
            username=NONAUTHOR_USERNAME
        )
        cls.form = PostForm()
        cls.post = models.Post.objects.create(
            text=TEXT_1,
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
        cls.ADD_COMENT_URL = reverse(
            'posts:add_comment',
            args=[cls.post.id]
        )
        cls.FORM_DATA1 = {
            'text': TEXT_2,
            'group': cls.group.id,
            'image': UPLOADED,
        }
        cls.FORM_DATA2 = {
            'text': TEXT_3,
            'group': cls.group_2.id,
            'image': UPLOADED,
        }
        cls.guest = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = Client()
        cls.user.force_login(cls.nonauthor)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = models.Post.objects.count()
        posts_ids = set(models.Post.objects.all().values_list("id", flat=True))
        UPLOADED.seek(0)
        response = self.author_client.post(
            CREATE_URL,
            self.FORM_DATA1,
            follow=True
        )
        new_posts = models.Post.objects.exclude(id__in=posts_ids)
        self.assertEqual(len(new_posts), 1)
        new_post = new_posts[0]
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(models.Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.text, self.FORM_DATA1['text'])
        self.assertEqual(new_post.group.id, self.FORM_DATA1['group'])
        self.assertEqual(new_post.author, self.author)
        self.assertEqual(
            new_post.image.seek(0),
            self.FORM_DATA1['image'].seek(0)
        )

    def test_anonymous_cant_create_post(self):
        """Анонимный пользователь не может создать пост."""
        posts_count = models.Post.objects.count()
        posts_ids = set(models.Post.objects.all().values_list("id", flat=True))
        anonymous_response = self.guest.post(
            CREATE_URL,
            self.FORM_DATA1,
            follow=True
        )
        new_posts = models.Post.objects.exclude(id__in=posts_ids)
        self.assertEqual(len(new_posts), 0)
        self.assertRedirects(
            anonymous_response,
            f'{LOGIN_URL}?next={CREATE_URL}'
        )
        self.assertEqual(models.Post.objects.count(), posts_count)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = models.Post.objects.count()
        UPLOADED.seek(0)
        response = self.author_client.post(
            self.POST_EDIT_URL,
            data=self.FORM_DATA2,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        edited_post = response.context['post']
        self.assertEqual(models.Post.objects.count(), posts_count)
        self.assertEqual(edited_post.text, self.FORM_DATA2['text'])
        self.assertEqual(edited_post.group.id, self.FORM_DATA2['group'])
        self.assertEqual(edited_post.author, self.post.author)
        self.assertEqual(edited_post.image.seek(0), UPLOADED.seek(0))

    def test_anonymous_and_nonauthor_cant_edit_post(self):
        """Анонимный пользователь и не автор не могут редактировать пост."""
        posts_count = models.Post.objects.count()
        UPLOADED.seek(0)
        cases = [
            [self.user, self.POST_DETAIL_URL],
            [self.guest, f'{LOGIN_URL}?next={self.POST_EDIT_URL}'],
        ]
        for user, redirect_url in cases:
            with self.subTest(user=user):
                response = user.post(
                    self.POST_EDIT_URL,
                    data=self.FORM_DATA2,
                    follow=True
                )
                edited_post = self.post
                self.assertRedirects(response, redirect_url)
                self.assertNotEqual(edited_post.text, self.FORM_DATA2['text'])
                self.assertNotEqual(
                    edited_post.group.id,
                    self.FORM_DATA2['group']
                )
                self.assertNotEqual(
                    edited_post.image,
                    UPLOADED
                )
                self.assertEqual(models.Post.objects.count(), posts_count)

    def test_post_edit_create_show_correct_context(self):
        """Шаблоны post_edit и post_create сформированы
        с правильным контекстом.
        """
        urls = [
            self.POST_EDIT_URL,
            CREATE_URL,
        ]
        for url in urls:
            response = self.author_client.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_add_comment_form_creates_new_comment(self):
        """Форма add_comment создает комментарий и он показывается
        на странице поста.
        """
        response = self.author_client.post(
            self.ADD_COMENT_URL,
            COMMENT_FORM_DATA,
            follow=True
        )
        self.assertEqual(
            response.context['post'].comments.all()[0].text,
            COMMENT_FORM_DATA['text']
        )
        self.assertEqual(
            response.context['post'],
            self.post
        )
        self.assertEqual(
            response.context['post'].comments.all()[0].author,
            self.post.author
        )

    def test_anonymous_cant_comment(self):
        comments_count = self.post.comments.all().count()
        response = self.guest.post(
            self.ADD_COMENT_URL,
            COMMENT_FORM_DATA,
            follow=True
        )
        self.assertRedirects(
            response,
            f'{LOGIN_URL}?next={self.ADD_COMENT_URL}'
        )
        comments_count_after_post = self.post.comments.all().count()
        self.assertEqual(comments_count, comments_count_after_post)
