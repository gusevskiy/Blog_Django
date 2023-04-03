from django.urls import reverse
from django.test import TestCase, Client
from ..models import Group, Post, User
from http import HTTPStatus


class URLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='R2_D2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        """ Создаем три клиента"""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_template(self):
        """Проверяем страницы для Неавторизованного пользователя"""
        urls_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
        }
        for address, template in urls_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_guest_client_page(self):
        """Проверяем страницы для Авторизованного пользователя"""
        urls_name = {
            'posts/post_create.html': reverse('posts:post_create')
        }
        for address, page in urls_name.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_page(self):
        """Не существующая страница"""
        address = '/unexpected_page/'
        response = self.client.get(address)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_page(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_404(self):
        """страница 404 отдаёт кастомный шаблон."""
        address = '/unexpected_page/'
        response = self.client.get(address)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.guest_client.get(address)
        self.assertTemplateUsed(response, 'core/404.html')
