from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, User, Group, Follow
# import paginator
from .utils import get_paginated_objects


def index(request):
    """main page"""
    context = get_paginated_objects(Post.objects.all(), request)
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    """users posts group"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        "group": group,
    }
    context.update(get_paginated_objects(posts, request))
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    """user page"""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    user_is_author = request.user == author
    context = {
        'author': author,
        'posts': posts,
        'user_is_author': user_is_author,
        'following': following,
    }
    context.update(get_paginated_objects(posts, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """page of one post"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """check and save post"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect(
                reverse(
                    'posts:profile',
                    kwargs={'username': request.user.username}
                )
            )
    return render(
        request, 'posts/post_create.html', {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    page_obj = Post.objects.filter(author__following__user=request.user)
    page_count = len(page_obj)
    context = {
        'page_obj': page_obj,
        'page_count': page_count,
        'follow': True
    }
    context.update(get_paginated_objects(page_obj, request))
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
