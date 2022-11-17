from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    # index.html
    path("", views.index, name="index"),
    # group_list.html
    path("group/<slug:slug>/", views.group_posts, name="group_list"),
    # post_create.html
    path('create/', views.post_create, name='post_create'),
    # post_detail.html
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # post_detail.html или post_create.html авторизованный
    path('posts/<post_id>/edit/', views.post_edit, name='post_edit'),
    # profile.html авторизованный
    path('profile/<str:username>/', views.profile, name='profile'),
    path(
        'posts/<int:post_id>/comment/', views.add_comment, name='add_comment'
    ),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
