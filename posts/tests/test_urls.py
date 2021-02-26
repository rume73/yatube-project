# posts/tests/tests_urls.py
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User, Comment, Follow


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(username="Ivan_Log")
        cls.user2 = User.objects.create(username="Ivan_Log1")
        cls.user3 = User.objects.create(username="IvanLog")
        cls.group1 = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Описание тестовой группы",
        )
        cls.group2 = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug-1",
            description="Описание тестовой группы",
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text="Тестовый текст",
            group=cls.group1,
        )
        cls.post2 = Post.objects.create(
            author=cls.user3,
            text="Тестовый текст",
            group=cls.group2,
        )
        cls.comment = Comment.objects.create(
            post=cls.post1,
            text="Отлично",
            author=cls.user1,
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = self.post1.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(response.status_code, 200)

    def test_post_group_url_exists_at_desired_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get(reverse("posts:group", kwargs={
            "slug": self.group1.slug}))
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /<str:username>/ доступна любому пользователю."""
        response = self.guest_client.get(reverse("posts:profile", kwargs={
            "username": self.user}))
        self.assertEqual(response.status_code, 200)

    def test_post_id_url_exists_at_desired_location(self):
        """Страница <str:username>/<int:post_id>/ доступна
        любому пользователю.
        """
        response = self.guest_client.get(reverse("posts:post", kwargs={
            "username": self.user1,
            "post_id": self.post1.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_new_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get("/new/")
        self.assertEqual(response.status_code, 200)

    def test_follow_index_url_exists_at_desired_location(self):
        """Страница /follow/ доступна авторизованному пользователю."""
        response = self.authorized_client.get("/follow/")
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница <str:username>/<int:post_id>/edit/ доступна
        авторизованному пользователю.
        """
        response = self.authorized_client.get(reverse("posts:post_edit",
                                              kwargs={
                                                  "username": self.user1,
                                                  "post_id": self.post1.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_new_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get("/new/", follow=True)
        self.assertRedirects(
            response, "/auth/login/?next=/new/")

    def test_profile_follow_url_redirect_anonymous_on_admin_login(self):
        """Страница /follow/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(reverse("posts:profile_follow",
                                         kwargs={"username": self.user3}),
                                         follow=True)
        self.assertRedirects(response, "/auth/login/?next=/IvanLog/follow/")

    def test_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница /<str:username>/<int:post_id>/edit/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse("posts:post_edit",
                                         kwargs={"username": self.user3,
                                                 "post_id": self.post1.id}),
                                         follow=True)
        self.assertRedirects(response, "/auth/login/?next=/IvanLog/1/edit/")

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "index.html": reverse("posts:index"),
            "new_post.html": reverse("posts:new_post"),
            "group.html": reverse("posts:group",
                                  kwargs={"slug": self.group1.slug}),
            "follow.html": reverse("posts:follow_index"),
            "profile.html": reverse("posts:profile", kwargs={
                "username": self.user3
            }),
            "post.html": reverse("posts:post", kwargs={
                "username": self.user1,
                "post_id": self.post1.id
            }),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_wrong_url_returns_404(self):
        """Страница /fail/ возвращает код 404 пользователю."""
        response = self.guest_client.get("/fail/")
        self.assertEqual(response.status_code, 404)
