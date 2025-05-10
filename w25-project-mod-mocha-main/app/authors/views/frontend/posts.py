from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.contrib.auth.decorators import login_required  
from django.urls import reverse
from authors.models import Post, FollowRequest, Friend, Author,ForeignPost, ForeignAuthor
import markdown
import json
import requests
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
import uuid
from authors.models import Node
from authors.serializers import PostSerializer  # or create a minimal serializer if needed
import base64 
from base64 import b64encode

def get_auth_headers(node):
    user_pass = f"{node.username}:{node.password}"
    token = b64encode(user_pass.encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }


def send_post_to_nodes(post):
    if post.visibility != "PUBLIC":
        return  # Only send public posts

    nodes = Node.objects.filter(is_active=True)

    for node in nodes:
        inbox_url = node.inbox_url or f"{node.host}api/authors/{post.author.id}/inbox"
        
        try:
            # Serialize and encode safely
            serialized_post = PostSerializer(post).data
            serialized_post["type"] = "post"
            serialized_post["id"] = serialized_post.get("global_id", serialized_post["id"])
            serialized_post["contentType"] = serialized_post["content_type"]
            serialized_post["published"] = serialized_post["created_at"]
            serialized_post["author"] = {
                "type": "author",
                "id": post.author.global_id,
                "host": post.author.host,
                "displayName": post.author.display_name,
                "page": f"{post.author.host}authors/{post.author.id}",
                "github": post.author.github,
                "profileImage": post.author.profile_image,
            }
            if serialized_post["image"]:
                try:
                    # Open the image file and encode it as Base64
                    with post.image.open("rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                    
                    # Update contentType to image/jpeg (or the appropriate type)
                    serialized_post["contentType"] = "image/jpeg"  # Change to "image/png" if needed
                    
                    # Send the Base64-encoded image as the content
                    serialized_post["content"] = f"data:{serialized_post['contentType']};base64,{encoded_image}"

                except Exception as e:
                    print(f"Error encoding image: {e}")
                    serialized_post["content"] = None  # Fallback to None if image encoding fails

            safe_json_payload = json.loads(json.dumps(serialized_post, cls=DjangoJSONEncoder))
            headers = get_auth_headers(node)

            response = requests.post(
                inbox_url,
                json=safe_json_payload,
                headers=headers
            )
            #print(safe_json_payload)

            print(f"[✓] Sent to {inbox_url}, status={response.status_code}")
        except Exception as e:
            print(f"[x] Error sending post to {node.host}: {e}")



def send_delete_to_nodes(post):
    # Build a delete-type payload
    payload = {
        "type": "delete",
        "id": str(post.id),
        "author": {
            "id": str(post.author.id),
            "host": post.author.host if hasattr(post.author, "host") else "",  # optional
        }
    }

    for node in Node.objects.filter(is_active=True):
        inbox_url = node.inbox_url or f"{node.host}api/authors/{post.author.id}/inbox"
        try:
            headers = get_auth_headers(node)
            response = requests.post(
                inbox_url,
                data=json.dumps(payload, cls=DjangoJSONEncoder),
                headers=headers
            )
            print(f"[✓] Sent delete to {node.host}: {response.status_code}")
        except Exception as e:
            print(f"[x] Failed to send delete to {node.host}: {e}")



def create_post(request, author_id):
    """ Renders a form to create a new post with an optional image """
    author = get_object_or_404(Author, id=author_id)

    if request.method == "POST":
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        content = request.POST.get("content", "")
        content_type = request.POST.get("content_type", "text/plain")
        visibility = request.POST.get("visibility", "PUBLIC")
        image = request.FILES.get("image", None)  #  Handle image upload

        if not content and not image:
            return render(request, "authors/create_post.html", {"error": "Content or image is required.", "author": author})

        post = Post(
            id=uuid.uuid4(),
            author=author,
            title=title,
            description=description,
            content=content,
            content_type=content_type,
            visibility=visibility,
            image=image,  #  Save the image
            created_at=now(),
            updated_at=now(),
        )
        post.save()
        send_post_to_nodes(post)


        return redirect(reverse('authors:post-detail', kwargs={'author_id': author.id, 'post_id': post.id}))

    return render(request, "authors/create_post.html", {"author": author})


@login_required(login_url='authors:login_view')
def view_post(request, author_id, post_id):
    """ View a SINGLE post with options to update or delete it. """
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)

    if post.visibility == "FRIENDS":
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You do not have permission to view this post.")

        user_author = Author.objects.filter(user=request.user).first()
        friends = get_friends(author)

        if user_author not in friends and user_author != author:
            return HttpResponseForbidden("This post is only visible to friends.")

    comments = post.comments.filter(Q(author=author) | Q(author__id__in=friends)).order_by('-published') if post.visibility == "FRIENDS" else post.comments.all().order_by('-published')

    if post.visibility == "DELETED":
        return HttpResponseForbidden("This post is no longer available.")
    
    post_content = mark_safe(markdown.markdown(post.content)) if post.content_type == "text/markdown" else post.content

    #  Ensure image URL is passed to template
    image_url = post.image.url if post.image else None

    return render(request, 'authors/view_post.html', {
        "author": author,
        "post": post,
        "comments": comments,
        "image_url": image_url,  #  Now available in the template
        "post_content": post_content,
    })


def update_post(request, author_id, post_id):
    """ Form with existing post data to update. """
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)

    if request.method == "POST":
        post.title = request.POST.get("title", post.title)
        post.description = request.POST.get("description", post.description)
        post.content = request.POST.get("content", post.content)
        post.content_type = request.POST.get("content_type", post.content_type)
        post.visibility = request.POST.get("visibility", post.visibility)

        new_image = request.FILES.get("image", None)
        if new_image:
            post.image = new_image  #  Update image if a new one is uploaded

        post.save()
        send_post_to_nodes(post)
        return redirect(reverse('authors:post-detail', kwargs={'author_id': author.id, 'post_id': post.id}))

    return render(request, "authors/update_post.html", {"author": author, "post": post})

def manage_posts(request, author_id):
    """ View ALL posts made by a specific author """
    author = get_object_or_404(Author, id=author_id)
    posts = Post.objects.filter(author=author).order_by('-created_at')
    return render(request, "authors/posts.html", {"author": author, "posts": posts})

def delete_post(request, author_id, post_id):
    """ Handles post deletion """
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)

    if request.method == "POST":
        post.visibility = "DELETED"
        post.save()
        send_delete_to_nodes(post) 
        return redirect(reverse('authors:author_profile_id', kwargs={'author_id': author.id}))


    return redirect(reverse('authors:post-detail', kwargs={'author_id': author.id, 'post_id': post.id}))


def process_post_content(posts):
    '''Convert markdown content for all posts'''
    for post in posts:
        if post.content_type == "text/markdown":
            post.content = mark_safe(markdown.markdown(post.content))
    return posts

def stream_view(request):
    user = request.user
    author = Author.objects.filter(user=user).first() if user.is_authenticated else None
    filter_type = request.GET.get("filter", "all")

    friend_ids = get_friends(author) if author else []
    followed_authors = get_followed_authors(author) if author else []

    # LOCAL posts logic
    if not author:
        Post.objects.filter(visibility="PUBLIC").exclude(visibility="DELETED")

    elif filter_type == "friends-only":
        local_posts = Post.objects.filter(author__id__in=friend_ids).exclude(visibility="DELETED")
    else:
        local_posts = Post.objects.filter(
            Q(visibility="PUBLIC") |
            Q(visibility="PRIVATE", author__id__in=friend_ids) |
            Q(visibility="UNLISTED", author__id__in=followed_authors + friend_ids)
        ).exclude(Q(visibility="DELETED") | Q(author=author))

    # FOREIGN posts logic (only public ones)
    foreign_posts = ForeignPost.objects.filter(
        visibility="PUBLIC"
    ).exclude(
        visibility="DELETED"
    ).order_by("-published")

    

    # Merge and sort
    all_posts = list(local_posts) + list(foreign_posts)
    all_posts.sort(key=lambda x: x.updated_at if hasattr(x, "updated_at") else x.published, reverse=True)

    all_posts = process_post_content(all_posts)

    # Tag post type for the template
    for post in all_posts:
        post.is_foreign = post.__class__.__name__ == "ForeignPost"

    return render(request, "authors/stream.html", {"posts": all_posts, "filter_type": filter_type})


def get_friends(author):
    """ Returns a list of friend author IDs (both authors must have approved each other). """
    if not author:
        return []

    friend_ids = set()
    friendships = Friend.objects.filter(Q(author_1=author) | Q(author_2=author))
    
    for f in friendships:
        friend_ids.add(f.author_1.id if f.author_2 == author else f.author_2.id)

    return list(friend_ids)


def get_followed_authors(author):
    """ Get a list of followed authors excluding friends """
    if not author:
        return []

    friend_ids = get_friends(author)

    followed_authors = list(FollowRequest.objects.filter(
        follower=author, status="approved"
    ).exclude(
        followee__id__in=friend_ids  # Remove friends from followers
    ).values_list("followee__id", flat=True))

    return followed_authors

def send_comment_to_nodes(comment):
    from authors.serializers import CommentSerializer
    from authors.models import Node
    import json
    import requests
    from django.core.serializers.json import DjangoJSONEncoder

    nodes = Node.objects.filter(is_active=True)

    for node in nodes:
        try:
            # ✅ Determine the post and author fields based on model type
            post = comment.post
            if hasattr(comment, "foreign_author"):
                author = comment.foreign_author
                post_author_id = post.foreign_author.id
            else:
                author = comment.author
                post_author_id = post.author.id

            inbox_url = node.inbox_url or f"{node.host}api/authors/{post_author_id}/inbox"
            print(f"📨 Sending comment to inbox URL: {inbox_url}")

            # ✅ Serialize the comment (you may still want different serializers if needed)
            serialized_comment = CommentSerializer(comment).data
            serialized_comment["type"] = "comment"
            serialized_comment["id"] = str(comment.global_id)

            # Replace nested author object with minimal info
            serialized_comment["author"] = {
                "id": str(author.global_id),
                "host": author.host,
                "displayName": author.display_name,
            }

            # Include post ID as URL
            serialized_comment["post"] = str(post.global_id)

            payload = json.loads(json.dumps(serialized_comment, cls=DjangoJSONEncoder))
            print("📦 Final JSON payload:", json.dumps(payload, indent=2))

            headers = get_auth_headers(node)

            response = requests.post(
                inbox_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            print(f"📝 Sent comment {comment.id} to {node.host}, status: {response.status_code}")
            if response.status_code not in [200, 201]:
                print("⚠️ Response content:", response.text)

        except Exception as e:
            print(f"❌ Failed to send comment {comment.id} to {node.host}: {e}")


