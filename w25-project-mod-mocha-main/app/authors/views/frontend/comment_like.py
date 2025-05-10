import json
import uuid
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from authors.models import Author, Post, Comment, ForeignPost, ForeignComment, ForeignAuthor
from authors.views.api.comment_like import send_comment_to_nodes  # ✅ federation function


# 📝 Render comment form for local posts
def comment_post_form(request, author_id, post_id):
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)

    context = {
        "author": author,
        "post": post,
    }
    return render(request, "authors/comment_post.html", context)


# 📄 List posts + their foreign comments
def post_list(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    posts = Post.objects.filter(author=author).exclude(visibility='DELETED').order_by('-created_at')

    for post in posts:
        post.foreign_comments_list = ForeignComment.objects.filter(post=post).order_by('-published')

    return render(request, "authors/post_list.html", {
        "author": author,
        "posts": posts
    })


# 🌐 Create comment on a foreign post + federate
@login_required
@require_http_methods(["GET", "POST"])
def foreign_post_comment_form(request, post_id):
    post = get_object_or_404(ForeignPost, id=post_id)

    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            local_author = request.user.author

            # Convert local author to ForeignAuthor if needed
            foreign_author, _ = ForeignAuthor.objects.get_or_create(
                global_id=str(local_author.global_id),
                defaults={
                    "id": local_author.id,
                    "display_name": local_author.display_name,
                    "host": local_author.host,
                }
            )

            comment = ForeignComment.objects.create(
                global_id=f"{local_author.global_id}/posts/{post.id}/comments/{uuid.uuid4()}",
                foreign_author=foreign_author,
                post=post,
                comment=comment_text,
                content_type="text/plain",
                published=timezone.now()
            )

            # ✅ Federation call
            send_comment_to_nodes(comment)

            return redirect("authors:home")  # or another view like "stream"

    return render(request, "authors/comment_foreign_post.html", {"post": post})
