from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group, User
from yatube.settings import POSTS_ON_PAGE


def page_obj(queryset, request):
    return Paginator(queryset, POSTS_ON_PAGE).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': page_obj(Post.objects.all(), request),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'page_obj': page_obj(group.posts.all(), request),
        'group': group,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    return render(request, 'posts/profile.html', {
        'page_obj': page_obj(author.posts.all(), request),
        'author': author,
    })


def post_detail(request, post_id):
    return render(request, 'posts/post_detail.html', {
        'post': get_object_or_404(Post, pk=post_id),
    })


@login_required
def post_create(request):
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'post': post,
    })
