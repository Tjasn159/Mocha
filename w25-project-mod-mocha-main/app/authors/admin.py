from django.contrib import admin
from .models import Author, FollowRequest, Friend, ForeignFollowRequest, Node
from authors.models import Post
from authors.serializers import PostSerializer
import requests
import json
from django.core.serializers.json import DjangoJSONEncoder
from base64 import b64encode
import threading

# Build headers for basic auth
def get_auth_headers(node):
    user_pass = f"{node.username}:{node.password}"
    token = b64encode(user_pass.encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

# Send public posts to new node
def send_all_public_posts_to_node(node):
    from authors.models import Post
    from authors.serializers import PostSerializer
    import os
    import base64
    import json
    import requests
    from django.core.serializers.json import DjangoJSONEncoder

    posts = Post.objects.filter(visibility="PUBLIC")
    for post in posts:
        try:
            inbox_url = node.inbox_url or f"{node.host}api/authors/{post.author.id}/inbox"
            serialized_post = PostSerializer(post).data
            serialized_post["type"] = "post"


            headers = get_auth_headers(node)
            if post.image:
                if os.path.exists(post.image.path):
                    with open(post.image.path, "rb") as img_file:
                        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
                    serialized_post["image_base64"] = encoded_image
                    ext = os.path.splitext(post.image.name)[-1].replace('.', '')
                    serialized_post["contentType"] = f"image/{ext};base64"
                else:
                    serialized_post["image_base64"] = None
            else:
                serialized_post["image_base64"] = None

            if "image" in serialized_post:
                del serialized_post["image"]

            response = requests.post(
                inbox_url,
                json=json.loads(json.dumps(serialized_post, cls=DjangoJSONEncoder)),
                headers=headers
            )
            print(f"✓ Sent post {post.id} to {node.host}, status: {response.status_code}")
            if response.status_code == 401:
                print(" Unauthorized. Double-check the receiving node's expected credentials.")
        except Exception as e:
            print(f"✗ Failed to send post {post.id} to {node.host}: {e}")


# Create a custom admin class for Node
class CustomNodeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        is_new = not obj.pk  # It's new if it has no primary key yet
        super().save_model(request, obj, form, change)
        if is_new:
            threading.Thread(target=send_all_public_posts_to_node, args=(obj,)).start()

# Register your models
admin.site.register(Author)
admin.site.register(FollowRequest)
admin.site.register(Friend)
admin.site.register(ForeignFollowRequest)
admin.site.register(Node, CustomNodeAdmin)