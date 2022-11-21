from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Follow, Post, Group, User, Comment


class ViewTests(TestCase):
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
        cls.page_count = []
        for i in range(1, 14):
            cls.page_count.append(
                Post(
                    text=f'Тестовый пост {i}',
                    group=cls.group,
                    author=cls.user,
                )
            )
        Post.objects.bulk_create(cls.page_count)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.QUANTITY_POSTS = 10
        self.CHECK_QUANTITY_POSTS = Post.objects.count() - self.QUANTITY_POSTS

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            'posts/post_create.html': reverse('posts:post_create'),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.user}
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_indext_context(self):
        """index C правильным контекстом"""
        response = self.guest_client.get(reverse('posts:index'))
        page = list(Post.objects.all()[:10])
        self.assertEqual(list(response.context['page_obj']), page)

    def test_group_list_context(self):
        """group_list c правильным контекстом"""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={"slug": self.group.slug})
        )
        page = list(
            Post.objects.filter(group_id=self.group.id)[:self.QUANTITY_POSTS]
        )
        self.assertEqual(list(response.context["page_obj"]), page)

    def test_profile_context_autorizet(self):
        """profile c правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={"username": self.user.username})
        )
        page = list(
            Post.objects.filter(author_id=self.group.id)[:self.QUANTITY_POSTS]
        )
        self.assertEqual(list(response.context["page_obj"]), page)

    def test_post_detail_context_guest(self):
        """ profile с правельным контекстом."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={'username': self.post.author})
        )
        expected = list(
            Post.objects.filter(author_id=self.user.id)[:self.QUANTITY_POSTS]
        )
        self.assertEqual(list(response.context["page_obj"]), expected)

    def test_form_post_detail_context(self):
        """post_detail с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        post = response.context.get("post")
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_create_show_context(self):
        """create форма с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        """Проверка, на главной странице 10 постов"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), self.QUANTITY_POSTS
        )

    def test_second_page_contains_three_records(self):
        """ Проверка на второй странице должно быть 4е поста"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), self.CHECK_QUANTITY_POSTS
        )

    def test_comment_autorise_clients(self):
        """Комментировать посты может только авторизованный пользователь."""
        form_data = {"text": "Тестовый коммент"}
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            )
        )
        self.assertTrue(
            Comment.objects.filter(text=form_data["text"]).exists()
        )

    def test_appears_new_comment_page(self):
        """после успешной отправки комментарий появляется на странице поста."""
        comments_count = Comment.objects.count()
        form_data = {"text": "Тестовый коммент"}
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            )
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(text=form_data["text"]).exists()
        )

    def test_cashe_index(self):
        """Проверка кеша на главной странице"""
        cache.clear()
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.user)
        content_add = self.authorized_client.get(
            reverse('posts:index')
        ).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_add, content_cache_clear)


class FollowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user_1")
        self.user_following = User.objects.create_user(username="test_user_2")
        self.guest_client = Client()
        self.client_autorized = Client()
        self.client_autorized.force_login(self.user)
        self.text = "test_text"
        self.post = Post.objects.create(
            text=self.text, author=self.user_following
        )

    def test_follow(self):
        """Авторизованный может подписаться"""
        self.client_autorized.get(
            reverse(
                "posts:profile_follow",
                kwargs={'username': self.user_following}
            )
        )
        self.assertIsNotNone(Follow.objects.first())

    def test_unfollow(self):
        """Авторизованный может отписаться"""
        self.client_autorized.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={'username': self.user_following}
            )
        )
        self.assertIsNone(Follow.objects.first())

    def test_post_follow_index(self):
        """Пост у авторизованного пользователя"""
        self.client_autorized.get(
            reverse(
                "posts:profile_follow",
                kwargs={'username': self.user_following}
            )
        )
        resp = self.client_autorized.get(reverse("posts:follow_index"))
        self.assertContains(resp, self.text)

    def test_post_not_follow_index(self):
        """Пост у не авторизованного пользователя"""
        response = self.client_autorized.get(reverse("posts:follow_index"))
        self.assertNotContains(response, self.text)
