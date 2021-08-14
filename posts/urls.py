from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search_results"),
    path("allgroups/", views.all_groups, name="all_groups"),
    path("allauthors/", views.all_authors, name="all_authors"),
    path("group/<slug:slug>/", views.group_posts, name="group"),
    path('newgroup/', views.new_group, name='new_group'),
    path("new/", views.new_post, name="new_post"),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path("404/", views.page_not_found, name="404"),
    path("500/", views.server_error, name="500"),
    path("follow/", views.follow_index, name="follow_index"),
    path("<str:username>/follow/", views.profile_follow,
         name="profile_follow"),
    path("<str:username>/unfollow/", views.profile_unfollow,
         name="profile_unfollow"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    path("<str:username>/<int:post_id>/edit/", views.post_edit,
         name="post_edit"),
    path("<str:username>/<int:post_id>/comment/", views.add_comment,
         name="add_comment"),
    path("<str:username>/<slug:slug>/edit/", views.group_edit,
         name="group_edit"),
    path("<str:username>/<int:post_id>/post_delete/", views.post_delete,
         name="post_delete"),
    path("<str:username>/<slug:slug>/delete/", views.group_delete,
         name="group_delete"),
    path("<str:username>/groups/", views.author_groups, name="author_groups"),
    path("<str:username>/delete/", views.user_delete, name="user_delete"),
    path("<str:username>/<int:post_id>/like/", views.likes,
         name="likes"),
    path('following/<str:username>/', views.following, name='following'),
    path('followers/<str:username>/', views.followers, name='followers'),
]
