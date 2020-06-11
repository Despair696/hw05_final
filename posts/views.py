from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from posts.forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow


User = get_user_model()


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {
            "group": group,
            "page": page,
            "paginator": paginator
            }
    )


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            new_post_form = form.save(commit=False)
            new_post_form.author = request.user
            new_post_form.save()
            success_url = "index"
            return redirect(success_url)

        return render(request, "new_post.html", {"form": form})

    form = PostForm()
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.order_by('-pub_date').all()
    follow = None
    if request.user.is_authenticated:
        follow = Follow.objects.filter(user=request.user, author=author).exists()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "profile.html",
        {
            "author": author,
            "page": page,
            "paginator": paginator,
            "follow": follow
        }
    )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    posts = author.posts.order_by('-pub_date').all()
    posts_sum = posts.count()
    post = get_object_or_404(Post, author=author, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request,
        "post_view.html",
        {
            "author": author,
            "post": post,
            "posts_sum": posts_sum,
            "comments": comments,
            "form": form
            }
        )


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    user = request.user
    if user != author:
        return redirect("post", username=post.author, post_id=post.id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username=post.author, post_id=post.id)

    return render(
        request,
        "new_post.html",
        {
            "form": form,
            "edit": True,
            "post": post,
            "author": author
            }
        )


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            return redirect("post", username=post.author, post_id=post.id)

    else:
        form = CommentForm()
    return render(
        request,
        "post_view.html",
        {
            "post": post,
            "author": author,
            "form": form,
        }
    )


@login_required
def follow_index(request):
    following = Follow.objects.all().values("author")
    post_list = Post.objects.filter(author__in=following).order_by("author")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {"page": page, "paginator": paginator, "following": following},
    )


@login_required
def profile_follow(request, username):
    followed_author = get_object_or_404(User, username=username)
    if request.user != followed_author:
        Follow.objects.get_or_create(user=request.user, author=followed_author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
