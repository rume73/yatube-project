# posts/tests/tests_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user1 = User.objects.create(username="Ivan_Log")
        user2 = User.objects.create(username="Ivan_Log1")
        group1 = Group.objects.create(
            title="Тестовая група",
            slug="test-slug",
            description="Описание группы")
        post1 = Post.objects.create(
            author=user1,
            text="Привет " * 15)
        comment1 = Comment.objects.create(
            post=post1,
            text="Отлично",
            author=user1,
        )
        cls.follow = Follow.objects.create(
            user=user2,
            author=user1,
        )
        cls.post = post1
        cls.comment = comment1
        cls.group = group1

    def test_post_verbose_name(self):
        """verbose_name поля модели Post совпадают с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
            "image": "Картинка",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_comment_verbose_name(self):
        """verbose_name поля модели Comment совпадают с ожидаемым."""
        comment = PostModelTest.comment
        field_verboses = {
            "post": "Ссылка на пост",
            "text": "Комментарий",
            "created": "Дата публикации",
            "author": "Автор",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_group_verbose_name(self):
        """verbose_name поля модели Group совпадают с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            "title": "Название группы",
            "slug": "Уникальный идентификатор",
            "description": "Описание",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_follow_verbose_name(self):
        """verbose_name поля модели Follow совпадают с ожидаемым."""
        follow = PostModelTest.follow
        field_verboses = {
            "user": "Подписчик",
            "author": "Подписка",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)

    def test_post_text_help_text(self):
        """help_text поля модели Post совпадают с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            "group": "Выберите группу",
            "text": "Введите текст публикации",
            "image": "Загрузите картинку",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_group_text_help_text(self):
        """help_text поля модели Group совпадают с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            "title": "Введите название группы",
            "slug": "Укажите адрес для страницы группы. "
                    "Используйте только латиницу, цифры, дефисы "
                    "и знаки подчёркивания",
            "description": "Введите описание группы",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_title_help_text(self):
        """help_text поля comment.text совпадает с ожидаемым."""
        comment = PostModelTest.comment
        help_text = comment._meta.get_field("text").help_text
        self.assertEquals(help_text, "Напишите комментарий")

    def test_post_text_field(self):
        """В поле __str__ объекта post записано значение поля post.text."""
        post = PostModelTest.post
        expected_text = post.text[:15]
        self.assertEqual(expected_text, str(post))

    def test_title_field(self):
        """В поле __str__ объекта group записано значение поля group.title."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_comment_text_field(self):
        """В поле __str__ объекта comment записано значение comment.text."""
        comment = PostModelTest.comment
        expected_text = comment.text[:15]
        self.assertEqual(expected_text, str(comment))
