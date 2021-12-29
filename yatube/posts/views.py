from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post
from .utils import get_page_obj

User = get_user_model()


def index(request):
    post_list = Post.objects.order_by('-pub_date')
    context = {
        'page_obj': get_page_obj(post_list, settings.POST_PER_PAGE, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    context = {
        'group': group,
        'page_obj': get_page_obj(post_list, settings.POST_PER_PAGE, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    context = {
        'author': author,
        'page_obj': get_page_obj(post_list, settings.POST_PER_PAGE, request),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    user = request.user
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author_id = user.id
        new_post.save()
        return redirect('posts:profile', username=user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    if user != post.author:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(request, 'posts/create_post.html', {'form': form,
                                                      'is_edit': True,
                                                      'post_id': post.pk,
                                                      })
