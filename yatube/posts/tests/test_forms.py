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
CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': AUTHOR_USERNAME})
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = models.Post.objects.count()
        posts_ids = set(models.Post.objects.all().values_list("id", flat=True))
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': TEXT_2,
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_author.post(
            CREATE_URL,
            form_data,
            follow=True
        )
        new_posts = models.Post.objects.exclude(id__in=posts_ids)
        self.assertEqual(len(new_posts), 1)
        new_post = new_posts[0]
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(models.Post.objects.count(), posts_count + 1)
        self.assertTrue(new_post.text, form_data['text'])
        self.assertTrue(new_post.group.id, form_data['group'])
        self.assertTrue(new_post.author, self.author)
        self.assertTrue(new_post.image, form_data['image'])

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = models.Post.objects.count()
        form_data = {
            'text': TEXT_3,
            'group': self.group_2.id,
        }
        response = self.authorized_author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        edited_post = response.context['post']
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(models.Post.objects.count(), posts_count)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.author, self.post.author)

    def test_post_edit_create_show_correct_context(self):
        """Шаблоны post_edit и post_create сформированы
        с правильным контекстом.
        """
        urls = [
            self.POST_EDIT_URL,
            CREATE_URL,
        ]
        for url in urls:
            response = self.authorized_author.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_edit_create_make_new_entry_in_database(self):
        """Формы post_edit и post_create создают запись в базе данных.
        """
        urls = [
            self.POST_EDIT_URL,
            CREATE_URL,
        ]
        for url in urls:
            response = self.authorized_author.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_comment_is_shown_on_post_page(self):
        """Форма add_comment создает комментарий и он показывается
        на странице поста.
        """
        form_data = {
            'text': COMMENT,
            'post': self.post,
        }
        response = self.authorized_author.post(
            self.ADD_COMENT_URL,
            form_data,
            follow=True
        )
        self.assertEqual(
            response.context['post'].comments.all()[0].text,
            form_data['text']
        )
