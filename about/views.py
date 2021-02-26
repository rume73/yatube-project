from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = "about/about.html"

    def get_context_data(self, **kwargs):
        about_info = (
            "Автор социальной сети NextLevel",
            "Инженер головного исптательного центра Роскосмос",
            "Магистрант в МАИ",
            "Студент Яндекс.Практикум",
        )
        author_info = "Владимир Логинов"
        context = super().get_context_data(**kwargs)
        context["about_info"] = about_info
        context["author_info"] = author_info
        return context


class AboutTechView(TemplateView):
    template_name = "about/about.html"

    def get_context_data(self, **kwargs):
        tech_info = (
            "django 2.2 - фреймворк",
            "bootstrap - стили и оформление",
            "VS Code - среда разработки",
            "git - система контроля версий",
        )
        context = super().get_context_data(**kwargs)
        context["tech_info"] = tech_info
        return context
