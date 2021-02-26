# posts/tests/tests_forms.py
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

import tempfile
import shutil

from yatube.settings import MEDIA_ROOT
from posts.forms import PostForm
from posts.models import Post, Group, User, Comment


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(prefix="pages",
                                               dir=settings.BASE_DIR)

        group1 = Group.objects.create(
            title="Тестовый заголовок",
            description="Тестовое описание группы",
            slug="test-slug"
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        cls.group = group1
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username="Ivan_Log")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новую запись."""
        posts_count = Post.objects.count()
        form_data = {
            "group": self.group.id,
            "text": "Тестовый текст",
            "image": self.uploaded,
        }
        response = self.authorized_client.post(reverse("posts:new_post"),
                                               data=form_data,
                                               follow=True)

        self.assertRedirects(response, reverse("posts:index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(group=self.group.id,
                                            text="Тестовый текст",
                                            image="posts/small.gif").exists())

    def test_edit_post(self):
        """Валидная форма редактирует запись и производит редирект."""
        test_post = Post.objects.create(
            text="Тестовый текст записи",
            author=self.user,
        )
        posts_count = Post.objects.count()
        form_data_edit = {
            "group": self.group.id,
            "text": "Исправленный тестовый текст записи",
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit",
                    kwargs={
                        "username": self.user,
                        "post_id": test_post.id}),
            data=form_data_edit)
        test_post.refresh_from_db()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, reverse("posts:post", kwargs={
            "username": self.user,
            "post_id": test_post.id}))
        self.assertTrue(Post.objects.filter(
            text="Исправленный тестовый текст записи",
            group=self.group.id).exists())

    def test_authorised_user_can_comment(self):
        """Валидная форма добавляет комментарий"""
        test_post = Post.objects.create(
            text="Тестовый текст записи",
            author=self.user,
        )
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Тестовый комментарий"
        }
        self.authorized_client.post(
            reverse("posts:add_comment",
                    kwargs={
                        "username": self.user,
                        "post_id": test_post.id}),
            data=form_data,
            follow=True
        )
        comments_count_after = Comment.objects.count()
        self.assertEqual(comments_count + 1, comments_count_after)
        self.assertTrue(Comment.objects.filter(
            text="Тестовый комментарий").exists())
