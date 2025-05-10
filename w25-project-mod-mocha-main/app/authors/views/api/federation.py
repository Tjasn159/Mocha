from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from authors.models import Author, Post, FollowRequest
from authors.serializers import AuthorSerializer, PostSerializer, FollowRequestSerializer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

#  Get all authors (local and federated)
@api_view(['GET'])
def get_authors(request):
    authors = Author.objects.all()
    serialized_authors = AuthorSerializer(authors, many=True)
    return Response(serialized_authors.data)

#  Get a specific author
@api_view(['GET'])
def get_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    serialized_author = AuthorSerializer(author)
    return Response(serialized_author.data)

#  Get an author's posts
@api_view(['GET'])
def get_posts(request, author_id):
    posts = Post.objects.filter(author__id=author_id)
    serialized_posts = PostSerializer(posts, many=True)
    return Response(serialized_posts.data)

#  Follow an author on another node
@api_view(['POST'])
def follow_author(request, author_id):
    """ Send a follow request to another node """
    data = request.data
    target_author = get_object_or_404(Author, id=author_id)

    follow_request = FollowRequest.objects.create(
        requester=request.user.author,  # Assuming authentication is set up
        recipient=target_author,
        status="PENDING"
    )
    follow_request.save()

    serialized_follow_request = FollowRequestSerializer(follow_request)
    return Response(serialized_follow_request.data, status=status.HTTP_201_CREATED)

#  Fetch public posts from another node
@api_view(['GET'])
def fetch_remote_posts(request, remote_url):
    """ Fetch public posts from another node """
    try:
        response = requests.get(
            remote_url,
            auth=HTTPBasicAuth(settings.REMOTE_NODE_USERNAME, settings.REMOTE_NODE_PASSWORD)  # Authentication
        )
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to fetch posts"}, status=response.status_code)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
from authors.models import Node
from authors.serializers import NodeSerializer
from rest_framework.decorators import api_view

@api_view(['POST'])
def register_node(request):
    """ Add a new federated node """
    serializer = NodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from authors.models import Node
from authors.federation.utils import fetch_remote_author

@api_view(['GET'])
def get_all_authors(request):
    local_authors = Author.objects.all()
    serialized_local = AuthorSerializer(local_authors, many=True).data

    remote_authors = []
    for node in Node.objects.all():
        remote_authors += fetch_remote_authors(node)

    return Response(serialized_local + remote_authors)


