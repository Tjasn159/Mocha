from django.urls import path
from authors.views.api.follow import get_follower, get_followers
from authors.views.api.comment_like import CommentView, CommentListView, PostLikeView, CommentLikeView
from authors.views.api.authors import AuthorListView, AuthorDetailJSONView
from authors.views.api.posts import PostView
from authors.views.api.follow import follow_user
from authors.views.api.federation import register_node
from authors.views.api.inbox import inbox
from authors import views  





urlpatterns = [
    #inbox 
    path("<uuid:author_id>/inbox", inbox, name='inbox'),  



    #followers/friends api 
    path("<uuid:author_id>/followers/", get_followers, name='get_followers'),
    path("<uuid:author_id>/followers/<path:follower_id>/", get_follower, name='get_follower'),
    path("<uuid:author_id>/follow/", follow_user, name='follow_user'),
    #comments/likes api urls
    path('<uuid:author_id>/posts/<uuid:post_id>/comments/', CommentView.as_view(), name='create-comment'), # Create a new comment
    path('<uuid:post_id>/comments/', CommentListView.as_view(), name='all-comments'), # View all comments on a post
    path('<uuid:author_id>/posts/<uuid:post_id>/like/', PostLikeView.as_view(), name='like-post'), # Like a post
    path('<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/like/', CommentLikeView.as_view(), name='like-comment'), # Like a comment

    #Authors api urls
    path("", AuthorListView.as_view(), name="authors_list"),  # List/Create (No more "authors/")
    path("<uuid:author_id>/", AuthorDetailJSONView.as_view(), name="author_detail_json"),  # JSON API

    #Posts api urls
    path("<uuid:author_id>/posts/", PostView.as_view(), name="author-posts"),  #  View all posts by an author


    path("nodes/register/", register_node, name="register_node"),


]



