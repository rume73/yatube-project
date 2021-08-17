from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.db.models import Q

from .models import Post, Group, User, Follow, Profile, Likes
from .forms import PostForm, CommentForm, ProfileForm, GroupForm


def search(request):
    query = request.GET.get("q")
    object_list = Post.objects.filter(
        Q(text__icontains=query) or Q(author__username__icontains=query)
        or Q(group__title__icontains=query))
    return render(request, "search_results.html",
                  {"object_list": object_list, "query": query})


def index(request):
    post_list = Post.objects.select_related("group").all()
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
    is_image = False
    if Profile.objects.filter(image=None):
        is_image = True
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
        "post_view": False,
        "profile_is_not_image": is_image,}
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
    likes = post.likes.all()
    is_liked = False
    if post.likes.filter(user=request.user.id).exists():
        is_liked = True
    context = {
        "form": form,
        "post": post,
        "author": post.author,
        "comments": comments,
        "followers_count": followers_count,
        "followings_count": followings_count,
        "following": following,
        "show_form": False,
        "post_view": True,
        "likes": likes,
        "post_is_liked": is_liked,}
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
            status=404)


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
    return render(request, "post.html", {
        "form": form,
        "post": post,
        "author": post.author,
        "comments": comments,
        "followers_count": followers_count,
        "followings_count": followings_count,
        "following": following,
        "show_form": True,
        "post_view": True, })


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


@login_required
def new_group(request):
    form = GroupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        group = form.save(commit=False)
        group.creator = request.user
        group.save()
        return redirect("posts:all_groups")
    return render(request, "new_group.html", {"form": form})


@login_required
def group_edit(request, username, slug):
    creator = get_object_or_404(User, username=username)
    group = get_object_or_404(Group, creator=creator, slug=slug)
    if request.user != creator:
        return redirect("posts:all_groups")
    form = GroupForm(request.POST or None, files=request.FILES or None,
                     instance=group)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("posts:all_groups")
    return render(request, "new_group.html",
                  {"form": form, "creator": creator, "group": group})


@login_required
def group_delete(request, username, slug):
    creator = get_object_or_404(User, username=username)
    group = get_object_or_404(Group, creator=creator, slug=slug)
    if request.user != creator:
        return redirect("posts:all_groups")
    else:
        group.delete()
        return redirect("posts:all_groups")


def all_groups(request):
    group_list = Group.objects.all()
    paginator = Paginator(group_list, settings.DEFAULT_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "all_groups.html", {
        "page": page,
        "paginator": paginator,
        "groups": group_list})


@login_required
def profile_settings(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    form = ProfileForm(request.POST or None, files=request.FILES or None,
                       instance=profile)
    if not form.is_valid():
        return render(request, "profile_settings.html", {"form": form})
    form.save()
    return redirect("posts:profile", username=request.user.username)


@login_required
def user_delete(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect("posts:profile", username=request.user.username,)
    else:
        user.delete()
        return redirect("posts:index")


@login_required
def likes(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    is_liked = False
    if post.likes.filter(user=request.user.id).exists():
        is_liked = True
        Likes.objects.get(user=request.user, post=post).delete()
    else:
        Likes.objects.get_or_create(user=request.user, post=post)
    if user:
        prewious_url = request.META.get("HTTP_REFERER")
        return redirect(prewious_url, {"post_is_liked": is_liked})
    else:
        return redirect("post_view.html", username=request.user.username,
                        id=post_id)
    

def all_authors(request):
    author_list = User.objects.all().order_by('-date_joined')
    paginator = Paginator(author_list, 20)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "all_authors.html", {
        "page": page,
        "paginator": paginator,
        "author_list": author_list,})


def author_groups(request, username):
    creator = get_object_or_404(User, username=username)
    groups = Group.objects.filter(creator__username=username)
    paginator = Paginator(groups, settings.DEFAULT_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "author_groups.html",
                  {"creator": creator, "groups": groups,
                   "page": page, "paginator": paginator})


def following(request, username):
    author = get_object_or_404(User, username=username)
    following = author.follower.all()
    paginator = Paginator(following, 20)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "following.html", {
        "author": author,
        "page": page,
        "paginator": paginator,
    })


def followers(request, username):
    author = get_object_or_404(User, username=username)
    followers = author.following.all()
    paginator = Paginator(followers, 20)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "followers.html", {
        "author": author,
        "page": page, 
        "paginator": paginator,
    })
