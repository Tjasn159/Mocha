from django.urls import path
from authors.views.frontend.follow import view_followers, view_followees, view_follow_requests, edit_follow_request, create_follow_request, view_friends, edit_foreign_follow_request
from authors.views.frontend.comment_like import comment_post_form, post_list    
from authors.views.frontend.authors import AuthorDetailByIDView, AuthorUpdateView, AuthorDetailView, AuthorCreateView, get_authors, get_foreign_authors, send_follow_request
from authors.views.frontend.posts import create_post, view_post, update_post, delete_post, stream_view
from django.shortcuts import render
from authors.views.frontend.posts import manage_posts
from authors.views.frontend.authentication import register_view, login_view, logout_view
from authors.views.frontend.comment_like import foreign_post_comment_form
from authors.views.frontend.comment_like import foreign_post_comment_form

app_name = "authors"
urlpatterns = [
    # Home page now shows all relevant posts
    path("stream/", stream_view, name="home"), 
    path("foreign-posts/<uuid:post_id>/comment/", foreign_post_comment_form, name="foreign-post-comment-form"),
 

    # Authentication
    path("register/", register_view, name='register_view'),
    path("login/", login_view, name='login_view'),
    path("logout/", logout_view, name='logout_view'),
    #followers/friends frontend
    path("<uuid:author_id>/followers/", view_followers, name='view_followers'),
    path("<uuid:author_id>/followees/", view_followees, name='view_followees'),
    path("<uuid:author_id>/friends/", view_friends, name='view_friends'),
    path("<uuid:author_id>/followers/requests/", view_follow_requests, name='view_follow_requests'),
    path("<uuid:author_id>/followers/requests/create", create_follow_request, name='create_follow_request'),
    path("<uuid:author_id>/followers/requests/edit/<int:follow_request_id>/<str:status>/", edit_follow_request, name='edit_follow_request'),
    path("<uuid:author_id>/followers/requests/editf/<int:follow_request_id>/<str:status>/", edit_foreign_follow_request, name='edit_foreign_follow_request'),

    #comments/likes front end urls
    path('<uuid:author_id>/posts/<uuid:post_id>/comments/new/', comment_post_form, name='create-comment-form'), # Show form in browser for comment creation
    path('<uuid:author_id>/posts/list/', post_list, name='post-list'),  # View all posts by an author

    # Authors frontend urls
    path("", get_authors, name="authors"),  # Authors list 
    path("foreign/", get_foreign_authors, name="get_foreign_authors"),  # Foreign Authors list 
    path("foreign/request", send_follow_request, name="send_follow_request"),  # Send foreign request
    path("<uuid:author_id>/profile/", AuthorDetailByIDView.as_view(), name="author_profile_id"), 
    path("<uuid:author_id>/update/", AuthorUpdateView.as_view(), name="author_update"), # HTML Profile by ID
    path("name/<str:display_name>/profile/", AuthorDetailView.as_view(), name="author_profile_name"),
    path("create/", AuthorCreateView.as_view(), name="author_create"),
    # path("authors/<uuid:author_id>/profile/", AuthorDetailByIDView.as_view(), name="author_profile_id"),  # HTML Profile
    path("authors/create/", lambda request: render(request, "authors/create_author.html"), name="create_author"),  # HTML Form to Create
    path("authors/<uuid:author_id>/edit/", lambda request, author_id: render(request, "authors/update_author.html", {"author_id": author_id}), name="edit_author"),  # HTML Form to Edit

    #Posts frontend urls
    # path("<uuid:author_id>/posts/", PostView.as_view(), name="author-posts"),  #  View all posts by an author
    path("<uuid:author_id>/posts/new/", create_post, name="create-post-form"),  # Show form in browser for post creation
    path("<uuid:author_id>/posts/<uuid:post_id>/", view_post, name="post-detail"),  #  View a single post by an author
    path("<uuid:author_id>/posts/<uuid:post_id>/edit/", update_post, name="update-post"),  #  Update post made by author
    path("<uuid:author_id>/posts/<uuid:post_id>/delete/", delete_post, name="delete-post"),  #  Delete post made by author

    path("posts/", manage_posts, name="all-posts"),  #  View all posts (admin)

]
