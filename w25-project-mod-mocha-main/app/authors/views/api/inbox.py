from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.views.decorators.csrf import csrf_exempt    
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings

import uuid
import traceback
import os
import base64

from authors.models import (
    Author,
    ForeignFollowRequest,
    ForeignAuthor,
    ForeignPost,
    Comment
)

# ========== INBOX VIEW ==========

@authentication_classes([BasicAuthentication]) 
@permission_classes([IsAuthenticated]) 
@csrf_exempt
@api_view(['POST'])
def inbox(request, author_id):
    """
    Handle incoming requests to the inbox
    """
    print("📥 Received request to inbox.")
    try:
        if not request.data:
            return JsonResponse({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data

        if data.get('type') == 'follow':
            return handleFollowRequestObject(data, author_id)
        elif data.get('type') == 'post':
            return handlePostObject(data, author_id)
        elif data.get('type') == 'delete':
            return handleDeleteObject(data, author_id)
        elif data.get('type') == 'comment':
            return handleCommentObject(data, author_id)

        return JsonResponse({'error': 'Unsupported object type'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print("=== ERROR IN INBOX ===")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


# ========== HANDLERS ==========

def handleFollowRequestObject(data, author_id):
    actor_data = data.get('actor', {})
    object_data = data.get('object', {})

    if not actor_data or not object_data:
        return JsonResponse({'error': 'Missing "actor" or "object"'}, status=400)

    follower_id = actor_data.get('id')
    follower_name = actor_data.get('displayName')

    follow_request, created = ForeignFollowRequest.objects.get_or_create(
        followee=author_id,
        follower=follower_id,
        defaults={'display_name': follower_name}
    )

    if created:
        return JsonResponse({'message': 'Follow request sent successfully'}, status=201)
    elif follow_request.status == 'approved':
        return JsonResponse({'message': 'Follow request already approved'}, status=400)
    else:
        follow_request.status = 'pending'
        follow_request.save()
        return JsonResponse({'message': 'Follow request updated to pending'}, status=200)


def handlePostObject(data, author_id):
    print("📥 Received POST to inbox")

    author_data = data.get("author")
    print(f" Author Field: {author_data}")

    if isinstance(author_data, str):
        global_id = author_data.strip()
        author_uuid = uuid.UUID(global_id.rstrip("/").split("/")[-1])
        host = global_id.split("/authors/")[0] + "/"
        display_name = global_id.split("/authors/")[-1][:20]
    elif isinstance(author_data, dict):
        global_id = author_data.get("id")
        author_uuid = uuid.UUID(global_id.rstrip("/").split("/")[-1])
        host = author_data.get("host")
        display_name = author_data.get("displayName", str(author_uuid))
    else:
        return JsonResponse({'error': 'Invalid author field format'}, status=400)

    foreign_author, _ = ForeignAuthor.objects.get_or_create(
        global_id=global_id,
        defaults={'id': author_uuid, 'display_name': display_name, 'host': host}
    )

    post_id = uuid.uuid4()
    base64_data = data.get("content", None)
    print(f"🧬 image_base64 present: {'Yes' if base64_data else 'No'}")
    print(f"🧬 base64 length: {len(base64_data) if base64_data else 0}")

    ForeignPost.objects.update_or_create(
        id=post_id,
        defaults={
            'global_id': data.get("id"),
            'foreign_author': foreign_author,
            'title': data.get("title", ""),
            'description': data.get("description", ""),
            'content': data.get("content", ""),
            'content_type': data.get("contentType", "text/plain"),
            'visibility': data.get("visibility", "PUBLIC"),
            'published': parse_datetime(data.get("published", "")) or timezone.now(),
            'image_base64': base64_data
        }
    )

    if base64_data:
        decoded_image = base64.b64decode(base64_data)
        filename = f"{post_id}.png"
        media_dir = os.path.join(settings.MEDIA_ROOT, "post_images")
        os.makedirs(media_dir, exist_ok=True)
        full_path = os.path.join(media_dir, filename)
        with open(full_path, "wb") as f:
            f.write(decoded_image)
        print(f"📸 Decoded and created image file: {full_path}")

    return JsonResponse({'message': 'Foreign post received'}, status=201)


def handleDeleteObject(data, author_id):
    post_id = data.get("id")
    if not post_id:
        return JsonResponse({'error': 'Missing post ID'}, status=400)

    try:
        post_uuid = uuid.UUID(post_id.strip("/").split("/")[-1])
        post = ForeignPost.objects.get(id=post_uuid)
        post.visibility = "DELETED"
        post.save()
        return JsonResponse({'message': 'Post deleted'}, status=200)
    except ForeignPost.DoesNotExist:
        return JsonResponse({'message': 'Post already deleted or not found'}, status=200)


from authors.models import Author, ForeignAuthor, Post, ForeignPost, Comment
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import uuid

from authors.models import ForeignAuthor, ForeignPost, ForeignComment  # Make sure to import this
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import uuid
from django.http import JsonResponse

from authors.models import Author, ForeignAuthor, Post, ForeignPost, Comment, ForeignComment

from authors.models import Author, ForeignAuthor, Post, ForeignPost, Comment, ForeignComment
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import uuid

from authors.models import Author, ForeignAuthor, Post, ForeignPost, Comment, ForeignComment
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import uuid

from authors.models import Author, ForeignAuthor, Post, ForeignPost, Comment, ForeignComment
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import uuid

from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import uuid

from authors.models import Author, ForeignAuthor, Post, ForeignPost, Comment, ForeignComment

def handleCommentObject(data, author_id):
    print("📥 Received COMMENT in inbox")

    try:
        comment_id = uuid.uuid4()
        global_id = data.get("id", "")
        comment_text = data.get("comment", "")
        content_type = data.get("content_type", data.get("contentType", "text/plain"))
        published = parse_datetime(data.get("published", "")) or timezone.now()
        post_url = data.get("post")

        # Parse author info
        author_data = data.get("author")
        if not author_data:
            return JsonResponse({'error': 'Missing author'}, status=400)

        if isinstance(author_data, str):
            global_author_id = author_data
            author_uuid = uuid.UUID(author_data.rstrip("/").split("/")[-1])
            host = author_data.split("/authors/")[0] + "/"
            display_name = author_uuid.hex[:10]
        else:
            global_author_id = author_data.get("id")
            author_uuid = uuid.UUID(global_author_id.rstrip("/").split("/")[-1])
            host = author_data.get("host")
            display_name = author_data.get("displayName", str(author_uuid))

        # Get or create the foreign author
        foreign_author, _ = ForeignAuthor.objects.get_or_create(
            global_id=global_author_id,
            defaults={
                'id': author_uuid,
                'display_name': display_name,
                'host': host
            }
        )

        # Try to get the post from ForeignPost table
        try:
            post = ForeignPost.objects.get(global_id=post_url)
        except ForeignPost.DoesNotExist:
            try:
                local_post = Post.objects.get(global_id=post_url)

                # Shadow the local post as a ForeignPost
                post, _ = ForeignPost.objects.get_or_create(
                    global_id=local_post.global_id,
                    defaults={
                        "id": local_post.id,
                        "foreign_author": ForeignAuthor.objects.get_or_create(
                            id=local_post.author.id,
                            defaults={
                                "global_id": str(local_post.author.global_id),
                                "display_name": local_post.author.display_name,
                                "host": local_post.author.host,
                            }
                        )[0],
                        "title": local_post.title,
                        "description": local_post.description,
                        "content": local_post.content,
                        "content_type": local_post.content_type,
                        "published": local_post.created_at,

                        "visibility": local_post.visibility,
                        "image_base64": "",
                    }
                )

            except Post.DoesNotExist:
                return JsonResponse({'error': 'Post not found (local or foreign)'}, status=404)

        # Save as ForeignComment (always)
        ForeignComment.objects.update_or_create(
            global_id=global_id,
            defaults={
                "id": comment_id,
                "foreign_author": foreign_author,
                "post": post,
                "comment": comment_text,
                "content_type": content_type,
                "published": published
            }
        )

        return JsonResponse({"message": "Comment saved"}, status=201)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)



