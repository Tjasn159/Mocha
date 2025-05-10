from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from authors.models import Post, Author
from django.utils.timezone import now
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.core.serializers.json import DjangoJSONEncoder
import json

import uuid  #  Ensure uuid is imported
##This is so dumb why sint it pushing


import base64
import os

import base64
import os

import os
import base64
import json
from authors.models import Node
from authors.serializers import PostSerializer
import requests
from django.core.serializers.json import DjangoJSONEncoder

def send_post_to_nodes(post):
    from authors.models import Node
    from authors.serializers import PostSerializer
    import requests
    import os
    import base64
    import json
    from django.core.serializers.json import DjangoJSONEncoder

    nodes = Node.objects.filter(is_active=True)

    for node in nodes:
        try:
            inbox_url = node.inbox_url or f"{node.host}api/authors/{post.author.id}/inbox/"
            serialized_post = json.loads(json.dumps(PostSerializer(post).data, cls=DjangoJSONEncoder))
            serialized_post["type"] = "post"

            if post.image:
                print("🖼 Found image field:", post.image.name)
                print("🛣 Full path:", post.image.path)

                if os.path.exists(post.image.path):
                    with open(post.image.path, "rb") as img_file:
                        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
                        print("✅ Encoded image size:", len(encoded_image))

                    serialized_post["image_base64"] = encoded_image
                    ext = os.path.splitext(post.image.name)[-1].replace('.', '')
                    serialized_post["contentType"] = f"image/{ext};base64"
                else:
                    print("❌ File path does not exist:", post.image.path)
                    serialized_post["image_base64"] = None
            else:
                print("📭 No image attached to post.")
                serialized_post["image_base64"] = None

            if "image" in serialized_post:
                del serialized_post["image"]

            response = requests.post(
                inbox_url,
                json=serialized_post,
                headers={"Content-Type": "application/json"}
            )
            print(f"📤 Sent post {post.id} to {node.host}, status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending post {post.id} to {node.host}: {e}")




@method_decorator(csrf_exempt, name='dispatch')
class PostView(View):

    def post(self, request, author_id):
        """Allows authors to create posts with optional image uploads."""
        author = get_object_or_404(Author, id=author_id)

        if request.method == "POST":
            title = request.POST.get("title", "")
            description = request.POST.get("description", "")
            content = request.POST.get("content", "")
            content_type = request.POST.get("content_type", "text/plain")
            visibility = request.POST.get("visibility", "PUBLIC")

            image = request.FILES.get("image", None)  #  Extract image file

            if not content and not image:
                return JsonResponse({"error": "Either content or an image is required."}, status=400)

            post = Post(
                id=uuid.uuid4(),
                author=author,
                title=title,
                description=description,
                content=content,
                content_type=content_type,
                visibility=visibility,
                image=image,  #  Save image if provided
                created_at=now(),
                updated_at=now(),
            )
            post.save()
            send_post_to_nodes(post)

            return JsonResponse({
                "message": "Post created successfully",
                "post_id": str(post.id),
                "image_url": post.image.url if post.image else None,  #  Return image URL
            }, status=201)

    def get(self, request, author_id, post_id=None):
        """Handles fetching all posts or a specific post."""
        author = get_object_or_404(Author, id=author_id)

        if post_id:
            # Get a specific post
            post = get_object_or_404(Post, id=post_id, author=author)

            if post.visibility == "DELETED":
                return HttpResponseForbidden("This post is no longer available.")

            response = {
                "id": str(post.id),
                "global_id": post.global_id,
                "title": post.title,
                "description": post.description,
                "content": post.content,
                "content_type": post.content_type,
                "visibility": post.visibility,
                "image_url": post.image.url if post.image else None,  #  Include image in response
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat()
            }
            return JsonResponse(response)

        # Get all posts by the author
        posts = Post.objects.filter(author=author).order_by('-created_at')

        if not posts.exists():
            return JsonResponse({"message": "No posts made by this author."}, status=200)

        response = [
            {
                "id": str(post.id),
                "title": post.title,
                "description": post.description,
                "content": post.content,
                "content_type": post.content_type,
                "visibility": post.visibility,
                "image_url": post.image.url if post.image else None,  #  Include image in response
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat()
            }
            for post in posts
        ]
        return JsonResponse(response, safe=False)

    def put(self, request, author_id, post_id):
        """Update post but only if you're the author; will add functionality for node admin later."""
        post = get_object_or_404(Post, id=post_id, author__id=author_id)

        try:
            data = json.loads(request.body.decode('utf-8'))
            post.title = data.get("title", post.title)
            post.description = data.get("description", post.description)
            post.content = data.get("content", post.content)
            post.content_type = data.get("content_type", post.content_type)
            post.visibility = data.get("visibility", post.visibility)
            post.updated_at = now()
            post.save()

            return JsonResponse({"message": "Post updated", "post_id": str(post.id)}, status=200)

        except KeyError:
            return JsonResponse({"error": "Invalid request"}, status=400)

    def delete(self, request, author_id, post_id):
        """To allow an author to delete a post but only if it's their own.
        #### Have to make sure that deleted posts aren't actually deleted but simply set to be invisible to anyone except the 
        node admin who should still be able to view the deleted posts.
        """
        post = get_object_or_404(Post, id=post_id, author__id=author_id)

        post.visibility = "DELETED"
        post.save()

        return JsonResponse({"message": "Post deleted"}, status=204)
