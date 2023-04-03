from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, очень много символов больше 15!',
        )

    def test_models__str__(self):
        """Проверяем, что у модели group корректно работает __str__."""
        post = self.post
        group = self.group
        dict_egual = {
            post: post.text[:15],
            group: group.title
        }
        for model, expected_value in dict_egual.items():
            with self.subTest(model=model):
                self.assertEqual(expected_value, str(model))

    def test_verbose_name(self):
        """Проверяем, verbose_name."""
        field_verbose_name = {
            'text': 'Текст',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст автора',
            'pub_date': 'Дата проставится сама',
            'author': 'еле нашёл(',
            'group': 'Группа, к которой будет относится пост'
        }

        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value
                )
