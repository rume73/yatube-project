from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_url_exists_at_desired_location(self):
        """Проверка доступности адреса /author/."""
        response = self.guest_client.get(reverse("about:author"))
        self.assertEqual(response.status_code, 200)

    def test_tech_url_exists_at_desired_location(self):
        """Проверка доступности адреса /tech/."""
        response = self.guest_client.get(reverse("about:tech"))
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "about/about.html": reverse("about:author"),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
