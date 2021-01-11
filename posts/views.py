from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from yatube.settings import PAGE_NUMBER

user = get_user_model()


def index(request):
    content = Post.objects.select_related('group')
    paginator = Paginator(content, PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'index.html', context)


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    content = group.group_post.all()
    paginator = Paginator(content, PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'group': group,
        'paginator': paginator,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(
            request,
            'posts/new_post.html',
            {'form': form}
        )
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:index')
    return render(request, 'posts/new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(user, username=username)
    author_content = Post.objects.filter(author=author)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    paginator = Paginator(author_content, PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'author': author,
        'count': paginator.count,
        'page': page,
        'paginator': paginator,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    current_post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username)
    count = current_post.author.posts.count()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author__username=username).exists()
    form = CommentForm(request.POST or None)
    comments = current_post.comments.all()
    context = {
        'author': current_post.author,
        'count': count,
        'post': current_post,
        'comments': comments,
        'form': form,
        'following': following,
    }
    return render(request, 'posts/post.html', context)


def post_edit(request, username, post_id):
    current_user = request.user
    current_post = get_object_or_404(Post, id=post_id)
    if current_user != current_post.author:
        return redirect('posts:profile', username=current_post.author)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=current_post
    )
    if form.is_valid():
        current_post = form.save(commit=False)
        current_post.save()
        return redirect('posts:post', post_id=post_id, username=username)
    return render(
        request,
        'posts/new_post.html',
        {'form': form, 'post': current_post, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id, username):
    current_post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username
    )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.post = current_post
        new_comment.author = request.user
        new_comment.save()
    return redirect('posts:post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    current_user = request.user
    content = Post.objects.filter(author__following__user=current_user)
    paginator = Paginator(content, PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    following_to = get_object_or_404(user, username=username)
    if request.user == following_to:
        return profile(request, username)
    is_followed, created = Follow.objects.get_or_create(
        user=request.user,
        author=following_to,
    )
    return profile(request, username)


@login_required
def profile_unfollow(request, username):
    following_to = get_object_or_404(user, username=username)
    is_followed = Follow.objects.filter(user=request.user, author=following_to)
    is_followed.delete()
    return profile(request, username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
