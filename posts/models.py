from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
    text = models.TextField("Текст", help_text="Введите текст публикации")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts", verbose_name="Автор")
    group = models.ForeignKey("Group", on_delete=models.SET_NULL, null=True,
                              blank=True, related_name="posts",
                              verbose_name="Группа",
                              help_text="Выберите группу")
    image = models.ImageField(upload_to="posts/", blank=True, null=True,
                              verbose_name="Картинка",
                              help_text="Загрузите картинку")

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]
        verbose_name_plural = "Публикации"


class Group(models.Model):
    title = models.CharField("Название группы", max_length=200,
                             help_text="Введите название группы")
    slug = models.SlugField("Уникальный идентификатор", unique=True,
                            help_text="Укажите адрес для страницы группы. "
                            "Используйте только латиницу, цифры, дефисы "
                            "и знаки подчёркивания")
    description = models.TextField("Описание", null=True, blank=True,
                                   help_text="Введите описание группы")
    creator = models.ForeignKey(User, verbose_name='Создатель группы',
                                on_delete=models.SET_NULL, blank=True,
                                null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Группы"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments", null=True, blank=True,
                             verbose_name="Ссылка на пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments", verbose_name="Автор")
    text = models.TextField("Комментарий",
                            help_text="Напишите комментарий")
    created = models.DateTimeField("Дата публикации", auto_now_add=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["created"]
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower", verbose_name="Подписчик")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following",
                               verbose_name="Подписка")

    class Meta:
        db_table = "Follow"
        constraints = [models.UniqueConstraint(fields=["user", "author"],
                                               name="unique follow")]
        verbose_name_plural = "Подписки"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True,
                           verbose_name="Описание профиля")
    image = models.ImageField(upload_to="users/", blank=True,
                              null=True, verbose_name="Аватар")
    

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="user_likes")
    post = models.ForeignKey(Post, blank=False, null=False,
                             on_delete=models.CASCADE,
                             related_name="likes")
