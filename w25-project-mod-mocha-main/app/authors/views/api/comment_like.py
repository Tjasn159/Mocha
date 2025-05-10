from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from authors.models import Post, Comment, Author, PostLike, CommentLike
from django.utils.timezone import now
import json

#  Import the federation function to send comments to other nodes
from authors.views.frontend.posts import send_comment_to_nodes


class CommentView(View):
    ''' 
    Handles comments on posts 
    Allows the user to see the comments on the posts and also add comments to the posts
    '''
    def post(self, request, author_id, post_id):
        '''
        Allows the user to add and create a new comment to a post
        '''
        # Verify that the post exists
        post = get_object_or_404(Post, id=post_id, author_id=author_id)

        # Verify that the author is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        commentor = request.user.author

        try:
            # Load the JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))
            comment_text = data['comment']
            content_type = data.get('content_type', 'text/plain')

            # Create a new comment object
            comment_obj = Comment(
                author=commentor,
                post=post,
                comment=comment_text,
                content_type=content_type,
                published=now()
            )

            # Save the comment to the database
            comment_obj.save()

            #  Send the comment to other federated nodes (new feature)
            send_comment_to_nodes(comment_obj)

            # Return a success response
            response_data = {
                "type": "comment",
                "author": {
                    "type": "author",
                    "id": str(commentor.id),
                    "displayName": commentor.display_name,
                    "host": commentor.host,
                    "url": commentor.global_id
                },
                "comment": comment_obj.comment,
                "contentType": comment_obj.content_type,
                "published": comment_obj.published.isoformat(),
                "id": str(comment_obj.id),
                "post": f'{post.author.host}api/authors/{post.author.id}/posts/{post.id}',
                "likes": {}
            }
            return JsonResponse(response_data, status=201)

        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"error": "Invalid JSON format"}, status=400)


class CommentListView(View):
    '''
    Handles the listing of comments on a post
    Returning all comments ordered newest to oldest
    '''   
    def get(self, request, post_id):
        # Verify that the post exists
        post = get_object_or_404(Post, id=post_id)

        # Get all the comments for the post
        comments_qs = post.comments.order_by('-published')

        # Pagination: return the first 5 comments
        page_size = 5
        page_number = int(request.GET.get('page', 1))
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size

        comments = comments_qs[start_index:end_index]
        comments_list = []
        for comment in comments:
            comments_list.append({
                "type": "comment",
                "author": {
                    "type": "author",
                    "id": str(comment.author.id),
                    "displayName": comment.author.display_name,
                    "host": comment.author.host,
                    "url": comment.author.global_id
                },
                "comment": comment.comment,
                "contentType": comment.content_type,
                "published": comment.published.isoformat(),
                "id": comment.global_id,
                "post": f'{post.author.host}api/authors/{post.author.id}/posts/{post.id}',
                "likes": {}
            })

        response_data = {
            "type": "comments",
            "page": f"{post.author.host}api/authors/{post.author.id}/posts/{post.id}/comments",
            "id": f"{post.author.host}api/authors/{post.author.id}/posts/{post.id}/comments",
            "page_number": page_number,
            "size": page_size,
            "count": post.comments.count(),
            "src": comments_list
        }
        return JsonResponse(response_data, safe=False)


class PostLikeView(View):
    '''
    Allow the user to like a post and create a model for it
    '''
    def post(self, request, author_id, post_id):
        post = get_object_or_404(Post, id=post_id)

        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        liker = request.user.author

        existing_like = PostLike.objects.filter(author=liker, post=post)
        if existing_like.exists():
            like_count = post.post_likes.count()
            return JsonResponse({
                "message": "You have already liked this post.",
                "count": like_count
            }, status=200)
        
        post_like = PostLike(
            author=liker,
            post=post,
            published=now()
        )
        post_like.save()

        like_count = post.post_likes.count()
        response_data = {
            "type": "like",
            "id": post_like.global_id,
            "author": {
                "type": "author",
                "id": str(liker.id),
                "page": f"{liker.host}api/authors/{liker.id}",
                "displayName": liker.display_name,
                "host": liker.host,
                "url": liker.global_id,
                "github": liker.github,
                "profileImage": liker.profile_image
            },
            "published": post_like.published.isoformat(),
            "object": f"{post.author.host}api/authors/{post.author.id}/posts/{post.id}",
            "count": like_count
        }
        return JsonResponse(response_data, status=201)


class CommentLikeView(View):
    '''This will allow a user to like a comment'''
    def post(self, request, author_id, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        author = get_object_or_404(Author, id=author_id)
        comment = get_object_or_404(Comment, id=comment_id, post=post)

        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        liker = request.user.author

        existing_like = CommentLike.objects.filter(author=liker, comment=comment)
        if existing_like.exists():
            like_count = comment.comment_likes.count()
            return JsonResponse({
                "message": "You have already liked this comment.",
                "count": like_count
            }, status=200)
        
        comment_like = CommentLike(author=liker, comment=comment, published=now())
        comment_like.save()

        like_count = comment.comment_likes.count()
        response_data = {
            "type": "like",
            "id": comment_like.global_id,
            "author": {
                "type": "author",
                "id": str(liker.id),
                "page": f"{liker.host}api/authors/{liker.id}",
                "displayName": liker.display_name,
                "host": liker.host,
                "url": liker.global_id,
                "github": liker.github,
                "profileImage": liker.profile_image
            },
            "published": comment_like.published.isoformat(),
            "object": f"{post.author.host}api/authors/{post.author.id}/posts/{post.id}/comments/{comment.id}",
            "count": like_count
        }
        return JsonResponse(response_data, status=201)
