# posts/tests/tests_views.py
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

import tempfile
import shutil

from yatube.settings import MEDIA_ROOT
from posts.models import Post, Group, User, Comment, Follow


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(prefix="pages",
                                               dir=settings.BASE_DIR)

        cls.group1 = Group.objects.create(
            title="Тестовый заголовок 2",
            slug="test-slug",
            description="Описание тестовой группы 2",
        )
        cls.group2 = Group.objects.create(
            title="Тестовый заголовок 3 ",
            slug="test-slug-1",
            description="Описание тестовой группы 3",
        )
        cls.user1 = User.objects.create(username="Ivan_Log11")
        cls.user2 = User.objects.create(username="Ivan_Log")
        cls.user3 = User.objects.create(username="Ivan_Log1")
        cls.group3 = Group.objects.create(
            title="Тестовый заголовок 4",
            slug="test-slug-2",
            description="Описание тестовой группы 4",
        )
        cls.group4 = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug-10",
            description="Описание тестовой группы",
        )
        cls.count = 5
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
        cls.post = Post.objects.create(
            author=cls.user3,
            text="Тестовый текст",
            group=cls.group4,
            image=cls.uploaded
        )
        posts = [Post(author=cls.user2, group=cls.group3,
                      text="Тестовый текст") for i in range(cls.count)]
        Post.objects.bulk_create(posts)
        cls.comment = Comment.objects.create(
            post=cls.post,
            text="Отлично",
            author=cls.user2
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user1,
        )
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username="IvanLog")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:index"))

        first_post = response.context["page"][5]
        post_author_0 = first_post.author
        post_text_0 = first_post.text
        post_group_0 = first_post.group
        post_image = first_post.image

        self.assertEqual(post_author_0.username, self.user3.username,
                         post_text_0)
        self.assertEqual(post_text_0, "Тестовый текст", post_text_0)
        self.assertEqual(post_group_0.title, self.group4.title,
                         post_text_0)
        self.assertEqual(post_image, self.post.image)

    def test_group_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:group",
                                         kwargs={"slug": self.group4.slug}))
        response_group = response.context["group"]
        page = response.context["page"]

        self.assertEqual(response_group.title, "Тестовая группа")
        self.assertEqual(response_group.description,
                         "Описание тестовой группы")
        self.assertEqual(response_group.slug, self.group4.slug)
        self.assertEqual(page.object_list[0].image, self.post.image)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:new_post"))

        form_fields = {
            "group": forms.models.ModelChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
        edit_flag = response.context.get("is_edit")
        self.assertFalse(edit_flag)

    def test_new_post_group_and_index_show_correct_context(self):
        """new_post сформирован в шаблонах index и group"""
        expected = self.post.text
        response = self.authorized_client.get(reverse("posts:index"))
        first_post = response.context["page"][0]
        self.assertEqual(first_post.text, expected)

        response = self.authorized_client.get(
            reverse("posts:group", kwargs={"slug": self.group3.slug}))
        page = response.context["page"]
        self.assertEqual(page.object_list[0].text, expected)

        response = self.authorized_client.get(
            reverse("posts:group", kwargs={"slug": self.group2.slug}))
        self.assertFalse(len(response.context.get("page").object_list))

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:profile",
                                         kwargs={"username": self.user3}))

        page = response.context["page"]
        post_author = response.context.get("author").username
        post_author_count = len(page.object_list)
        post_text_0 = page.object_list[0].text
        post_image = page.object_list[0].image

        self.assertEqual(post_author, self.user3.username)
        self.assertEqual(post_author_count, 1)
        self.assertEqual(post_text_0, "Тестовый текст")
        self.assertEqual(post_image, self.post.image)

    def test_post_view_pages_show_correct_context(self):
        test_post = Post.objects.create(text="Тестовый текст 1",
                                        author=self.user,
                                        image=self.post.image)
        comment = Comment.objects.create(post=test_post, text="Отлично",
                                         author=self.user)
        response = self.authorized_client.get(reverse("posts:post",
                                              kwargs={
                                                  "username": test_post.author,
                                                  "post_id": test_post.id}))

        post_author = response.context.get("post").author.username
        post_text_0 = response.context.get("post")
        post_image = response.context.get("post").image
        comment = response.context.get("comments")[0].text

        self.assertEqual(post_author, self.user.username)
        self.assertEqual(post_text_0, test_post)
        self.assertEqual(post_image, self.post.image)
        self.assertEqual(comment, self.comment.text)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        test_post = Post.objects.create(text="Тестовый текст 1",
                                        author=self.user,)
        response = self.authorized_client.get(reverse("posts:post_edit",
                                              kwargs={
                                                  "username": test_post.author,
                                                  "post_id": test_post.id}))
        form_fields = {
            "group": forms.models.ModelChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
        edit_flag = response.context.get("is_edit")
        self.assertTrue(edit_flag)

    def test_cache_correct_index_page(self):
        """Проверка работы кэширования на главной странице"""
        response_0 = self.authorized_client.get(reverse("posts:index"))

        post = Post.objects.create(text="Test", author=self.user,
                                   group=self.group1)
        response_1 = self.authorized_client.get(reverse("posts:index"))
        Post.objects.filter(id=post.id).delete()

        response_2 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response_1.content, response_2.content)

        cache.clear()
        response_3 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response_0.content, response_3.content)

    def test_new_post_follow_index_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом."""
        self.authorized_client.get(reverse("posts:profile_follow",
                                           kwargs={"username": self.user2}))
        follow_exist = Follow.objects.filter(user=self.user,
                                             author=self.user2).exists()
        self.assertEqual(True, follow_exist)

        test_post = Post.objects.create(text="Тестовый текст",
                                        author=self.user)
        expected = test_post.text
        response = self.authorized_client.get(reverse("posts:follow_index"))
        first_post = response.context["page"].object_list[0]
        self.assertEqual(first_post.text, expected)

        self.authorized_client.get(reverse("posts:profile_unfollow",
                                           kwargs={"username": self.user2}))
        follow_exist = Follow.objects.filter(user=self.user,
                                             author=self.user2).exists()
        self.assertEqual(False, follow_exist)

        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertFalse(len(response.context.get("page").object_list))

    def test_follow_another_user(self):
        """Follow на другого пользователя работает корректно"""
        self.authorized_client.get(reverse("posts:profile_follow",
                                           kwargs={"username": self.user2}))
        follow_exist = Follow.objects.filter(user=self.user,
                                             author=self.user2).exists()
        self.assertEqual(True, follow_exist)

    def test_unfollow_another_user(self):
        """Unfollow от другого пользователя работает корректно"""
        self.authorized_client.get(reverse("posts:profile_follow",
                                           kwargs={"username": self.user2}))
        self.authorized_client.get(reverse("posts:profile_unfollow",
                                           kwargs={"username": self.user2}))
        follow_exist = Follow.objects.filter(user=self.user,
                                             author=self.user2).exists()
        self.assertEqual(False, follow_exist)
