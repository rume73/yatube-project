from django import forms
from django.forms import Textarea

from .models import Post, Comment, Group, Profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text", "image")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
        self.fields["text"].widget = Textarea(attrs={"rows": 3, })


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("title", "slug", "description")
        labels = {"title": "Название группы", "slug": "Адрес группы",
                  "description": "Описание", }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("image", "bio")
        labels = {"image": "Загрузите аватар", "bio": "Напишите о себе", }
