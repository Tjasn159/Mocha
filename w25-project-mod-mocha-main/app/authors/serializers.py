from rest_framework import serializers
from .models import Author, Friend

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'display_name', 'github', 'profile_image', 'host'] 

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['author_1', 'author_2']
from authors.models import Node

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'
from rest_framework import serializers
from authors.models import Post

# class PostSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Post
#         fields = '__all__'

from rest_framework import serializers
from .models import Post

import base64

class PostSerializer(serializers.ModelSerializer):
    #image_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    # def get_image_base64(self, post):
    #     if post.image:
    #         with post.image.open("rb") as image_file:
    #             encoded = base64.b64encode(image_file.read()).decode("utf-8")
    #             if post.content_type == "image/png;base64":
    #                 return f"data:image/png;base64,{encoded}"
    #             elif post.content_type == "image/jpeg;base64":
    #                 return f"data:image/jpeg;base64,{encoded}"
    #     return None

from rest_framework import serializers
from authors.models import FollowRequest

class FollowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowRequest
        fields = '__all__'


from rest_framework import serializers
from authors.models import Comment, Author, ForeignComment, ForeignAuthor

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment  # Base it on Comment, but it will work for both
        fields = ['id', 'comment', 'content_type', 'published', 'author', 'post']  # ❌ Don't include 'type'

    def get_author(self, obj):
        # Handles both local and foreign comments
        if hasattr(obj, "author") and isinstance(obj.author, Author):
            author = obj.author
        elif hasattr(obj, "foreign_author") and isinstance(obj.foreign_author, ForeignAuthor):
            author = obj.foreign_author
        else:
            return None

        return {
            "id": str(author.global_id),
            "host": author.host,
            "displayName": author.display_name,
        }



