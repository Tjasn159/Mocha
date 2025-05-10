from django.shortcuts import get_object_or_404
from authors.models import Author, FollowRequest, Friend, ForeignFollowRequest
from django.db.models import Q
from authors.serializers import AuthorSerializer, FriendSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import unquote
import requests

@api_view(['GET'])
def get_followers(request, author_id):
    """
    Get the list of followers for a specfic author
    """
    author = get_object_or_404(Author, id=author_id)
    follow_requests = FollowRequest.objects.filter(followee=author, status='approved')
    # Check if no followers
    if not follow_requests.exists():
        return Response({"message": "This author has no followers."}, status=200)
    
    followers = []
    for follow_request in follow_requests:
        follower = follow_request.follower
        # Serialize the follower data 
        follower_data = AuthorSerializer(follower).data
        # Add extra field
        follower_data['type'] = 'author'
        followers.append(follower_data)

    # Return the formatted response
    return Response({
        "type": "followers",
        "followers": followers
    })

@api_view(['GET', 'PUT', 'DELETE'])
def get_follower(request, author_id, follower_id):
    """
    Get a specific follower for a specfic author, 404 if not a follower 
    """
    if request.method == 'GET':
        # check if foriegn follower 
        if follower_id.startswith("http"):
            # Decode the url 
            decoded_url = unquote(follower_id)
            print(f"Decoded follower_id: {decoded_url}") 
            # Get the object 
            follow_requests = ForeignFollowRequest.objects.filter(followee=author_id, follower=decoded_url, status='approved')

            if not follow_requests.exists():
                return Response({"message": f"{decoded_url} does not follow {author_id}."}, status=404)
            
            if follow_requests:
                try:
                    # Make the external GET request to get the follower data
                    #external_response = requests.get(decoded_url)
                    #external_response.raise_for_status()  # Will raise an error for non-2xx status codes
                    return Response(status=status.HTTP_200_OK)
                except requests.exceptions.RequestException as e:
                    return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
            
            # Get the author and return that data 
            return requests.get(decoded_url + "/")

        author = get_object_or_404(Author, id=author_id)
        follower = get_object_or_404(Author, id=follower_id)

        follow_requests = FollowRequest.objects.filter(followee=author,follower=follower, status='approved')
        # Check if no followers
        if not follow_requests.exists():
            return Response({"message": f"{follower.display_name} does not follow {author.display_name}."}, status=404)
        # Serialize the follower data 
        follower_data = AuthorSerializer(follower).data
        
        # Return the formatted response
        return Response(follower_data)
    if request.method == 'PUT':
        return add_follower(author, follower)
    if request.method == 'DELETE':
        return remove_follower(author, follower)

def add_follower(author, follower):
    """
    Add a follower to a specific author
    """
    # Check if the request object already exists
    follow_requests = FollowRequest.objects.filter(followee=author,follower=follower)
    if not follow_requests.exists():
        follow_request = FollowRequest.objects.create(follower=follower, followee=author, status='approved')
    else:
        follow_request = follow_requests.first() # get the first in the query set 
        follow_request.status = 'approved'
    follow_request.save()
    # Check if the other follow request exists and is approved
    other_follow_request = FollowRequest.objects.filter(
        follower=follow_request.followee, followee=follow_request.follower
    ).first()  # `.first()` will return None if no match is found

    if other_follow_request and other_follow_request.status == 'approved':
        # Both users approved each other's follow request, create friendship
        createFriendsip(follow_request.follower.id, follow_request.followee.id)
    
    return Response({"message": f"{follower.display_name} now follows {author.display_name}."}, status=200)


def remove_follower(author, follower):
    """
    Remove a follower from a specific author
    """
    # Check if the request object already exists
    follow_requests = FollowRequest.objects.filter(followee=author,follower=follower)
    if not follow_requests.exists():
        return Response({"message": f"{follower.display_name} does not follow {author.display_name}."}, status=404)
    follow_request = follow_requests.first() # get the first in the query set 
    follow_request.status = 'denied'
    follow_request.save()
    # Check if they were friends and if so remove the friendship
    try:
        # Try to get a friendship where either author_1 or author_2 matches the author_id
        friendship = Friend.objects.filter(
            (Q(author_1=author.id) | Q(author_2=author.id))
        ).first()  # Get the first match (if any)
    except Friend.DoesNotExist:
        friendship = None
    if friendship:
        friendship.delete()

    return Response({"message": f"{follower.display_name} no longer follows {author.display_name}."}, status=200)

def createFriendsip(author1_id, author2_id):
    serializer = FriendSerializer(data={"author_1":author1_id, "author_2":author2_id})
    if serializer.is_valid():
        print("is valid")
        serializer.save()
    else:
        return Response({"error": serializer.errors}, status=400)
    return 

@api_view(['POST'])
def follow_user(request, author_id):
    '''
    Allow the user to follow another author
    '''
    if not request.user.is_authenticated: # Check if the user is authenticated
        return Response({"error": "User not authenticated"}, status=401)
    
    follower = request.user.author
    followee = get_object_or_404(Author, id=author_id)

    if follower == followee: # Check if the user is trying to follow themselves
        return Response({"error": "You cannot follow yourself."}, status=400)
    
    # Check if the follow request already exists
    follow_request, created = FollowRequest.objects.get_or_create(
        follower=follower,
        followee=followee,
        defaults={'status': 'pending'}
    )

    if not created:
        return Response({"error": "You have already sent a follow request to this author."}, status=200)
    
    return Response({"message": "Follow request sent successfully."}, status=201)

