#views
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponseRedirect
from .models import Post, Author, FollowRequest, Friend
from .serializers import AuthorSerializer, FriendSerializer
from django.views import generic, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import uuid  #  Added for UUID generation
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from .models import Post, Author, Comment, PostLike, CommentLike
from django.views import generic , View
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.urls import reverse 
from django.db.models import Q 
import json
import uuid
from django.urls import reverse
from rest_framework.renderers import JSONRenderer



from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import uuid  #  Added for UUID generation

# #  Fetch Author by Display Name (HTML)
# class AuthorDetailView(generic.DetailView):
#     model = Author
#     context_object_name = "author"
#     template_name = "authors/profile.html"

#     def get_object(self):
#         display_name = self.kwargs.get('display_name')
#         return get_object_or_404(Author, display_name=display_name)

# #  Fetch Author by ID (HTML)
# class AuthorDetailByIDView(generic.DetailView):
#     model = Author
#     context_object_name = "author"
#     template_name = "authors/profile.html"

#     def get_object(self):
#         author_id = self.kwargs.get('author_id')
#         return get_object_or_404(Author, id=author_id)

# #  Fetch Author as JSON
# class AuthorDetailJSONView(View):
#     def get(self, request, author_id):
#         author = get_object_or_404(Author, id=author_id)
#         return JsonResponse({
#             "id": str(author.id),
#             "global_id": author.global_id,
#             "display_name": author.display_name,
#             "host": author.host,
#             "github": author.github,
#             "profile_image": author.profile_image,
#         })

# @method_decorator(csrf_exempt, name='dispatch')
# class AuthorListView(View):
#     """Handles listing all authors and creating new authors."""

#     def get(self, request):
#         """Retrieve a list of all authors."""
#         authors = Author.objects.all().values("id", "global_id", "display_name", "host", "github", "profile_image")
#         return JsonResponse(list(authors), safe=False)

#     def post(self, request):
#         """Create a new author and generate a unique `global_id`."""
#         try:
#             data = json.loads(request.body)
#             author_id = uuid.uuid4()
#             global_id = f"http://127.0.0.1:8000/authors/{author_id}"  #  Ensure uniqueness

#             author = Author.objects.create(
#                 id=author_id,
#                 display_name=data["display_name"],
#                 host=data["host"],
#                 global_id=global_id,
#                 github=data.get("github", ""),
#                 profile_image=data.get("profile_image", ""),
#             )

#             return JsonResponse({
#                 "id": str(author.id),
#                 "global_id": author.global_id,
#                 "display_name": author.display_name,
#                 "host": author.host,
#                 "github": author.github,
#                 "profile_image": author.profile_image,
#             }, status=201)

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)
        

# class AuthorUpdateView(View):
#     """Allows updating an author's profile."""

#     def get(self, request, author_id):
#         """Render author update form."""
#         author = get_object_or_404(Author, id=author_id)
#         return render(request, "authors/update_author.html", {"author": author})

#     def post(self, request, author_id):
#         """Handle author update from form submission."""
#         author = get_object_or_404(Author, id=author_id)

#         # Get form data
#         author.display_name = request.POST.get("display_name", author.display_name)
#         author.github = request.POST.get("github", author.github)
#         author.profile_image = request.POST.get("profile_image", author.profile_image)
#         author.save()

#         #  Fix: Use 'authors:author_profile_id' instead of 'author_profile_id'
#         return redirect(reverse("authors:author_profile_id", kwargs={"author_id": author.id}))
  

# class AuthorCreateView(View):
#     """Handles creating a new author using an HTML form."""

#     def get(self, request):
#         """Render the form to create a new author."""
#         return render(request, "authors/create_author.html")

#     def post(self, request):
#         """Handle form submission and create an author."""
#         try:
#             display_name = request.POST.get("display_name")
#             github = request.POST.get("github", "")
#             profile_image = request.POST.get("profile_image", "")
#             author_id = uuid.uuid4()
#             global_id = f"http://127.0.0.1:8000/api/authors/{author_id}"

#             author = Author.objects.create(
#                 id=author_id,
#                 display_name=display_name,
#                 host="http://127.0.0.1:8000",
#                 global_id=global_id,
#                 github=github,
#                 profile_image=profile_image,
#             )

#             # Fix: Use 'authors:author_profile_id' instead of 'author_profile_id'
#             return redirect(reverse("authors:author_profile_id", kwargs={"author_id": author.id}))

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)
        
def create_post(request, author_id):
    """ Renders a form to create a new post """
    author = get_object_or_404(Author, id=author_id)

    if request.method == "POST":
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        content = request.POST.get("content", "")
        content_type = request.POST.get("content_type", "text/plain")
        visibility = request.POST.get("visibility", "PUBLIC")

        if not content:  # Ensure content is provided
            return render(request, "authors/create_post.html", {"error": "Content is required", "author": author})

        # Create a new post
        post = Post(
            id=uuid.uuid4(),
            author=author,
            title=title,
            description=description,
            content=content,
            content_type=content_type,
            visibility=visibility,
            created_at=now(),
            updated_at=now(),
        )
        post.save()

        return redirect(f"/api/authors/{author.id}/posts/")  # Redirect to the author's posts

    return render(request, "authors/create_post.html", {"author": author})



def view_post(request, author_id, post_id):
    """view a SINGLE post with options to update or delete it."""
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)


    # only the node admin can view deleted posts
    if post.visibility == "DELETED":
        return HttpResponseForbidden("This post is no longer available.")

    return render(request, 'authors/view_post.html', {"author": author, "post": post})


def update_post(request, author_id, post_id):
    """form with existing post data to update."""
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)

    if request.method == "POST":
        post.title = request.POST.get("title", post.title)
        post.description = request.POST.get("description", post.description)
        post.content = request.POST.get("content", post.content)
        post.content_type = request.POST.get("content_type", post.content_type)
        post.visibility = request.POST.get("visibility", post.visibility)
        post.save()
        return redirect('authors:post-detail', author_id=author.id, post_id=post.id)  #redirect to post detail

    return render(request, "authors/update_post.html", {"author": author, "post": post})



def manage_posts(request, author_id):
    """view ALL posts made by a specific author"""
    author = get_object_or_404(Author, id=author_id)
    posts = Post.objects.filter(author=author).order_by('-created_at')
    return render(request, "authors/posts.html", {"author": author, "posts": posts})

def delete_post(request, author_id, post_id):
    """ handles post deletion"""
    author = get_object_or_404(Author, id=author_id)
    post = get_object_or_404(Post, id=post_id, author=author)

    if request.method == "POST":
        post.visibility = "DELETED"
        post.save()
        return redirect('authors:author-posts', author_id=author.id)  #redirect to author's posts

    return redirect('authors:post-detail', author_id=author.id, post_id=post.id)  #redirect back to the post if not deleted





# #### TAKE A LOOK AT CSRF VERIFICATION LATER. MIGHT NEED TO REMOVE THE EXEMPTION
# @method_decorator(csrf_exempt, name='dispatch') # I'm exempting csrf verification
# class PostView(View):

#     def post(self, request, author_id):
#         """allows authors to make posts"""
#         author = get_object_or_404(Author, id=author_id)

#         ####IMPORTANT=>##authenticate the author before letting them make a post; temporarily disabling to see if it works. must authenticate. curls are anonymous
#         #if str(request.user.id) != str(author.id):
#         #    return HttpResponseForbidden("You do not have permission to create a post.")

#         try:
#             if not request.body:
#                 return JsonResponse({"error": "Empty request body"}, status=400)

#             data = json.loads(request.body.decode('utf-8'))

#             post = Post(
#                 id=uuid.uuid4(),  # Generate a new UUID for the post
#                 author=author,
#                 title=data.get("title", ""),
#                 description=data.get("description", ""),
#                 content=data["content"],  
#                 content_type=data.get("content_type", "text/plain"),
#                 visibility=data.get("visibility", "PUBLIC"),
#                 created_at=now(),
#                 updated_at=now(),
#             )
#             post.save()

#             response = {
#                 "message": "Post created successfully",
#                 "post_id": str(post.id),
#                 "global_id": post.global_id,
#             }
#             return JsonResponse(response, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)

#         except KeyError:
#             return JsonResponse({"error": "Missing required fields"}, status=400)


#     def get(self, request, author_id, post_id=None):
#         """Handles fetching all posts or a specific post."""
#         author = get_object_or_404(Author, id=author_id)

#         if post_id:
#             # Get a specific post
#             post = get_object_or_404(Post, id=post_id, author=author)

#             if post.visibility == "DELETED":
#                 return HttpResponseForbidden("This post is no longer available.")

#             response = {
#                 "id": str(post.id),
#                 "global_id": post.global_id,
#                 "title": post.title,
#                 "description": post.description,
#                 "content": post.content,
#                 "content_type": post.content_type,
#                 "visibility": post.visibility,
#                 "created_at": post.created_at.isoformat(),
#                 "updated_at": post.updated_at.isoformat()
#             }
#             return JsonResponse(response)

#         # Get all posts by the author
#         posts = Post.objects.filter(author=author).order_by('-created_at')

#         if not posts.exists():
#             return JsonResponse({"message": "No posts made by this author."}, status=200)

#         response = [
#             {
#                 "id": str(post.id),
#                 "title": post.title,
#                 "description": post.description,
#                 "content": post.content,
#                 "content_type": post.content_type,
#                 "visibility": post.visibility,
#                 "created_at": post.created_at.isoformat(),
#                 "updated_at": post.updated_at.isoformat()
#             }
#             for post in posts
#         ]
#         return JsonResponse(response, safe=False)


#     def put(self, request, author_id, post_id):
#         """update post but only if you're the author; will add functionality for node admin later"""
#         post = get_object_or_404(Post, id=post_id, author__id=author_id)

#         #####IMPORTANT=>#check if the user has permission to edit the post; again temporarily removing authentifcation; will have to add it back later
#         #if str(request.user.id) != str(post.author.id):
#         #    return HttpResponseForbidden("You do not have permission to edit this post.")


#         try:
#             data = json.loads(request.body.decode('utf-8'))
#             post.title = data.get("title", post.title)
#             post.description = data.get("description", post.description)
#             post.content = data.get("content", post.content)
#             post.content_type = data.get("content_type", post.content_type)
#             post.visibility = data.get("visibility", post.visibility)
#             post.updated_at = now()
#             post.save()

#             return JsonResponse({"message": "Post updated", "post_id": str(post.id)}, status=200)

#         #return error code if it didn't go through
#         except KeyError:
#             return JsonResponse({"error": "Invalid request"}, status=400)
    
#     def delete(self, request, author_id, post_id):
#         """to allow an author to delete a post but only if it's their own
#         ####Have to make sure that deleted posts aren't actually deleted but simply set to be invisible to anyone except the 
#         node admin who should still be able to view the deleted posts
#         """
#         post = get_object_or_404(Post, id=post_id, author__id=author_id)

#         #check if the user has permission to delete the post
#         #if str(request.user.id) != str(post.author.id):
#         #    return HttpResponseForbidden("You do not have permission to delete this post.")

#         post.visibility = "DELETED"
#         post.save()


#         return JsonResponse({"message": "Post deleted"}, status=204)
    
# class CommentView(View):
#     ''' 
#     Handles comments on posts 
#     Allows the user to see the comments on the posts and also add comments to the posts
#     '''
#     def post(self, request, author_id, post_id):
#         '''
#         Allows the user to add and create a new comment to a post
#         '''
#         #Verify that the post exists
#         post = get_object_or_404(Post, id=post_id, author_id=author_id)
#         #Verify that the author exists
#         author = get_object_or_404(Author, id=author_id)

#         try:
#             # Load the JSON data from the request body
#             data = json.loads(request.body.decode('utf-8'))
#             comment_text = data['comment']
#             content_type = data.get('content_type', 'text/plain')

#             # Create a new comment object
#             comment_obj = Comment( 
#                 author=author,
#                 post=post,
#                 comment = comment_text,
#                 content_type = content_type,
#                 published = now()
#             )
#             # Save the comment to the database
#             comment_obj.save()

#             # Return a success response
#             response_data = {
#                 "type": "comment",
#                 "author": {
#                     "type": "author",
#                     "id": str(author.id),
#                     "displayName": author.display_name,
#                     "host": author.host,
#                     "url": author.global_id
#                 },
#                 "comment": comment_obj.comment,
#                 "contentType": comment_obj.content_type,
#                 "published": comment_obj.published.isoformat(),
#                 "id": str(comment_obj.id),
#                 "post": f'{post.author.host}api/authors/{post.author.id}/posts/{post.id}',
#                 "likes" : {}
#             }
#             return JsonResponse(response_data, status=201)


#         except (json.JSONDecodeError, KeyError):
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)

# class CommentListView(View):
#     '''
#     Handles the listing of comments on a post
#     Returning all commnets ordered newest to oldest
#     '''   
#     def get(self, request, post_id):
#         # verify that the post exists
#         post = get_object_or_404(Post, id=post_id)
#         # get all the comments for the post
#         comments_qs = post.comments.order_by('-published')

#         #For pagination, we'll return the first 5 comments.
#         page_size = 5
#         page_number = int(request.GET.get('page', 1))
#         start_index = (page_number - 1) * page_size
#         end_index = start_index + page_size

#         comments = comments_qs[start_index:end_index]
#         comments_list = []
#         for comment in comments:
#             comments_list.append({
#                 "type": "comment",
#                 "author": {
#                     "type": "author",
#                     "id": str(comment.author.id),
#                     "displayName": comment.author.display_name,
#                     "host": comment.author.host,
#                     "url": comment.author.global_id
#                 },
#                 "comment": comment.comment,
#                 "contentType": comment.content_type,
#                 "published": comment.published.isoformat(),
#                 "id": comment.global_id,
#                 "post": f'{post.author.host}api/authors/{post.author.id}/posts/{post.id}',
#                 "likes" : {}
#             })

#         response_data = {
#             "type" : "comments",
#             "page" : f"{post.author.host}api/authors/{post.author.id}/posts/{post.id}/comments",
#             "id" : f"{post.author.host}api/authors/{post.author.id}/posts/{post.id}/comments",
#             "page_number" : page_number,
#             "size" : page_size,
#             "count" : post.comments.count(),
#             "src" : comments_list
#         }
#         return JsonResponse(response_data, safe=False)
    
# def comment_post_form(request, author_id, post_id):
#     '''
#     View to render the form to create a new comment under the users post
#     '''
#     # Verify that the post and author exists
#     author = get_object_or_404(Author, id=author_id)
#     post = get_object_or_404(Post, id=post_id, author=author)

#     context = {
#         "author": author,
#         "post": post,
#     }
#     return render(request, "authors/comment_post.html", context)

# class PostLikeView(View):
#     '''
#     Allow the user to like a post and create a model for it
#     '''
#     def post(self, request, author_id, post_id):
#         # verify that the post exists
#         post = get_object_or_404(Post, id=post_id)
#         # verify that the author exists
#         author = get_object_or_404(Author, id=author_id)

#         #Checks if this author has already liked this post
#         if PostLike.objects.filter(author=author, post=post).exists():
#             like_count = post.post_likes.count() #getting the number of likes on the post
#             response_data = {
#                 "message": "You have already liked this post.",
#                 "count" : like_count
#             }
#             return JsonResponse(response_data, status=200)
        
#         #Creating the like object
#         post_like = PostLike(
#             author=author,
#             post=post,
#             published=now()
#         )
#         post_like.save() #saving the like object to the database

#         like_count = post.post_likes.count() #getting the number of likes on the post
#         #returning a success response
#         response_data = {
#             "type" : "like",
#             "id" : post_like.global_id,
#             "author" : {
#                 "type" : "author",
#                 "id" : str(author.id),
#                 "page" : f"{author.host}api/authors/{author.id}",
#                 "displayName" : author.display_name,
#                 "host" : author.host,
#                 "url" : author.global_id,
#                 "github" : author.github,
#                 "profileImage" : author.profile_image
#             },
#             "published" : post_like.published.isoformat(),
#             "object" : f"{post.author.host}api/authors/{post.author.id}/posts/{post.id}",
#             "count" : like_count
#         }
#         return JsonResponse(response_data, status=201)
    
# def post_list(request, author_id):
#     '''
#     View to list all the posts
#     '''
#     # verify that the author exists
#     author = get_object_or_404(Author, id=author_id)
#     # get all the posts for the author
#     posts = Post.objects.filter(author=author).order_by('-created_at')
#     # render the posts
#     return render(request, "authors/post_list.html", {"author": author, "posts": posts})

# class CommentLikeView(View):
#     '''This will allow a user to like a comment'''
#     def post(self, request, author_id, post_id, comment_id):
#         # verify that the post exists
#         post = get_object_or_404(Post, id=post_id)
#         # verify that the author exists
#         author = get_object_or_404(Author, id=author_id)
#         # verify that the comment exists
#         comment = get_object_or_404(Comment, id=comment_id, post=post)

#         #Checks if this author has already liked this comment
#         if comment.comment_likes.filter(author=author).exists():
#             like_count = comment.comment_likes.count() #getting the number of likes on the comment
#             response_data = {
#                 "message": "You have already liked this comment.",
#                 "count" : like_count
#             }
#             return JsonResponse(response_data, status=200)
        
#         #Creating the like object for the comment
#         comment_like = CommentLike(author=author, comment=comment, published = now())
#         comment_like.save()

#         #getting the updated like count
#         like_count = comment.comment_likes.count()
#         response_data = {
#             "type" : "like",
#             "id" : comment_like.global_id,
#             "author" : {
#                 "type" : "author",
#                 "id" : str(author.id),
#                 "page" : f"{author.host}api/authors/{author.id}",
#                 "displayName" : author.display_name,
#                 "host" : author.host,
#                 "url" : author.global_id,
#                 "github" : author.github,
#                 "profileImage" : author.profile_image
#             },
#             "published" : comment_like.published.isoformat(),
#             "object" : f"{post.author.host}api/authors/{post.author.id}/posts/{post.id}/comments/{comment.id}",
#             "count" : like_count
#         }
#         return JsonResponse(response_data, status=201)

