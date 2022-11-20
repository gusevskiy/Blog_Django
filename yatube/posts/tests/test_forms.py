from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User


class PostFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="Han_Solo")
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание'
        )
        self.post = Post.objects.create(
            author=self.user,
            text="Тестовый текст",
        )
        self.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        self.posts_count = Post.objects.count()

    def test_create_form_in_post_non_group(self):
        """Запись в Post. без группы"""
        form_data = {"text": "Тестовый текст"}
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse(
                "posts:profile", kwargs={"username": self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertTrue(Post.objects.filter(text=form_data["text"]).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_form_in_post(self):
        """Запись в Post. """
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse(
                "posts:profile", kwargs={"username": self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"], group=self.group.id
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_form_in_post_invalid_data(self):
        """Попытка запис в Post. пустой формы"""
        form_data = {"text": ""}
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertFalse(Post.objects.filter(text=form_data.values()).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_form_in_post(self):
        """Изменяет запись в Post."""
        form_data = {"text": "Изменяем текст", "group": self.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertTrue(Post.objects.filter(text=form_data["text"]).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_create_form_post(self):
        """Не изменит запись в Post если неавторизован."""
        form_data = {"text": "Изменяем текст", "group": self.group.id}
        response = self.guest_client.post(
            reverse("posts:post_edit", kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, f"/auth/login/?next=/posts/{self.post.id}/edit/"
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertTrue(Post.objects.filter(text=self.post.text).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
