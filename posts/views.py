from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse

from .models import Comment, Post, Group, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, settings.DEFAULT_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
        "post_view": False,
    }
    return render(request, "index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.all()
    paginator = Paginator(group_list, settings.DEFAULT_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "group": group,
        "paginator": paginator,
        "post_view": False,
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect("posts:index")
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    latest = author.posts.all()
    paginator = Paginator(latest, settings.DEFAULT_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    followers_count = Follow.objects.filter(author=author).count()
    followings_count = Follow.objects.filter(user=author).count()
    following = Follow.objects.filter(user__username=request.user,
                                      author=author)
    context = {
        "page": page,
        "paginator": paginator,
        "author": author,
        "followers_count": followers_count,
        "followings_count": followings_count,
        "following": following,
        "post_view": False,}
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post.objects.filter(author__username=username, id=post_id))
    comments = post.comments.all()
    form = CommentForm(request.POST or None)

    followers_count = Follow.objects.filter(author=post.author).count()
    followings_count = Follow.objects.filter(user=post.author).count()
    following = Follow.objects.filter(user__username=request.user,
                                      author=post.author)
    context = {
        "form": form,
        "post": post,
        "author": post.author,
        "comments": comments,
        "followers_count": followers_count,
        "followings_count": followings_count,
        "following": following,
        "show_form": False,
        "post_view": True,}
    return render(request, "post.html", context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        raise Http404("У Вас нет прав на редактирование поста")
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.method == "POST" and form.is_valid():
        post.save()
        return redirect("posts:post", post.author, post_id)
    return render(request, "new_post.html", {"form": form, "post": post,
                                             "is_edit": True})


@login_required
def post_delete(request, username, post_id):
    try:
        post = get_object_or_404(Post, id=post_id, author__username=username)
        post.delete()
        return redirect("posts:index")
    except Post.DoesNotExist:
        return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(id=post_id, author__username=username)
    author = post.author
    form = CommentForm(request.POST or None)
    comments = post.comments.all()

    followers_count = Follow.objects.filter(author=post.author).count()
    followings_count = Follow.objects.filter(user=post.author).count()
    following = Follow.objects.filter(user__username=request.user,
                                      author=post.author)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(reverse("posts:post", kwargs={
            "username": author.username, "post_id": post.id}))
    return render(request, 'post.html', {
        "form": form,
        "post": post,
        "author": post.author,
        "comments": comments,
        "followers_count": followers_count,
        "followings_count": followings_count,
        "following": following,
        "show_form": True,
        "post_view": True,
        })


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.DEFAULT_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator}
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    follower.delete()
    return redirect("posts:profile", username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
