from django.shortcuts import render
from django.urls import path, include
from .views import (
    AuthorListView,
    AuthorDetailView,
    AuthorDetailByIDView,
    AuthorDetailJSONView,
    AuthorUpdateView,
    AuthorCreateView,
    PostView,
    manage_posts,
    create_post,
    update_post,
    delete_post,
    view_post,
    get_followers,get_follower, 
    view_followers, view_followees, view_follow_requests, edit_follow_request,
    CommentView, CommentListView, comment_post_form,
    PostLikeView, post_list,
    CommentLikeView

)
from .views import AuthorDetailView, PostView, manage_posts, create_post, update_post, delete_post, AuthorDetailJSONView, view_post
urlpatterns = [
    ### Backend APIs ### 
    # path("", AuthorListView.as_view(), name="authors_list"),  # List/Create (No more "authors/")
    # path("<uuid:author_id>/", AuthorDetailJSONView.as_view(), name="author_detail_json"),  # JSON API
    # path("<uuid:author_id>/profile/", AuthorDetailByIDView.as_view(), name="author_profile_id"), 
    # path("<uuid:author_id>/update/", AuthorUpdateView.as_view(), name="author_update"), # HTML Profile by ID
    # path("name/<str:display_name>/profile/", AuthorDetailView.as_view(), name="author_profile_name"),
    # path("create/", AuthorCreateView.as_view(), name="author_create"),

    #followers/friends api 
    # path("api/authors/<uuid:author_id>/followers/", get_followers, name='get_followers'),
    # path("api/authors/<uuid:author_id>/followers/<uuid:follower_id>/", get_follower, name='get_follower'),
    # #followers/friends frontend
    # path("<uuid:author_id>/followers/", view_followers, name='view_followers'),
    # path("<uuid:author_id>/followees/", view_followees, name='view_followees'),
    # path("<uuid:author_id>/followers/requests/", view_follow_requests, name='view_follow_requests'),
    # path("<uuid:author_id>/followers/requests/edit/<int:follow_request_id>/<str:status>/", edit_follow_request, name='edit_follow_request'),

    ### frontend ###
    # path("authors/<uuid:author_id>/profile/", AuthorDetailByIDView.as_view(), name="author_profile_id"),  # HTML Profile
    # path("authors/create/", lambda request: render(request, "authors/create_author.html"), name="create_author"),  # HTML Form to Create
    # path("authors/<uuid:author_id>/edit/", lambda request, author_id: render(request, "authors/update_author.html", {"author_id": author_id}), name="edit_author"),  # HTML Form to Edit

    #  Post Management (For Authors)
    path("<uuid:author_id>/posts/", PostView.as_view(), name="author-posts"),  #  View all posts by an author
    path("<uuid:author_id>/posts/new/", create_post, name="create-post-form"),  # Show form in browser for post creation
    path("<uuid:author_id>/posts/<uuid:post_id>/", view_post, name="post-detail"),  #  View a single post by an author
    path("<uuid:author_id>/posts/<uuid:post_id>/edit/", update_post, name="update-post"),  #  Update post made by author
    path("<uuid:author_id>/posts/<uuid:post_id>/delete/", delete_post, name="delete-post"),  #  Delete post made by author

    #  Global Post Management (Admin or All Users)
    path("posts/", manage_posts, name="all-posts"),  #  View all posts (admin)

    # #Comments
    # path('<uuid:author_id>/posts/<uuid:post_id>/comments/', CommentView.as_view(), name='create-comment'),  # Create a new comment (Not for browser)
    # path('posts/<uuid:post_id>/comments/', CommentListView.as_view(), name='all-comments'),  # View all comments on a post
    # path('<uuid:author_id>/posts/<uuid:post_id>/comments/new/', comment_post_form, name='create-comment-form'),  # Show form in browser for comment creation

    # #Likes
    # path('<uuid:author_id>/posts/<uuid:post_id>/like/', PostLikeView.as_view(), name='like-post'),  # Like a post (Not for browser)
    # path('<uuid:author_id>/posts/list/', post_list, name='post-list'), # List all posts (This is main one)
    # # path('<uuid:author_id>/posts/<uuid:post_id>/likes/', post_list, name='post-likes'), # List all likes on a post
    # path('<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/like/', CommentLikeView.as_view(), name='like-comment'),  # Like a comment (Not for browser)
]
