from django.test import TestCase

from .. import models


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = models.User.objects.create_user(username='auth')
        cls.group = models.Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = models.Post.objects.create(
            author=cls.user,
            text='Тестовая-тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        str_outputs = {
            self.post: f'Автор: {self.post.author.get_full_name}, '
            f'Текст: {self.post.text[:20]}',
            self.group: self.group.title,
        }
        for object, expected_value in str_outputs.items():
            with self.subTest(object=object):
                self.assertEqual(
                    str(object), expected_value)

    def test_post_verbose_names(self):
        """Проверяем, что у модели поста корректные
        человекочитаемые названия полей
        """
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    models.Post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_text(self):
        """Проверяем, что у модели поста корректные
        вспомогательные тексты
        """
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    models.Post._meta.get_field(field).help_text,
                    expected_value
                )
