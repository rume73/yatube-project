# posts/tests/tests_paginator.py
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Ivan_Log")
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test-slug",
            description="Описание тестовой группы",
        )
        cls.count = 13
        posts = [Post(author=cls.user, group=cls.group,
                      text=str(i)) for i in range(cls.count)]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()

    def test_index_first_page_containse_ten_records(self):
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_index_second_page_containse_three_records(self):
        response = self.guest_client.get(reverse("posts:index") + '?page=2')
        self.assertEqual(len(response.context.get("page").object_list), 3)

    def test_profile_first_page_containse_ten_records(self):
        response = self.guest_client.get(reverse("posts:profile", kwargs={
            "username": self.user}))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_profile_second_page_containse_three_records(self):
        response = self.guest_client.get(reverse("posts:profile", kwargs={
            "username": self.user}) + '?page=2')
        self.assertEqual(len(response.context.get("page").object_list), 3)

    def test_group_first_page_containse_ten_records(self):
        response = self.guest_client.get(reverse("posts:group", kwargs={
            "slug": self.group.slug}))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_group_second_page_containse_three_records(self):
        response = self.guest_client.get(reverse("posts:group", kwargs={
            "slug": self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context.get("page").object_list), 3)
