from django.shortcuts import render, get_object_or_404
from authors.models import Author, FollowRequest, Friend, ForeignFollowRequest, ForeignFriend
from authors.serializers import FriendSerializer
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from django.urls import reverse
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from urllib.parse import unquote, quote
from rest_framework import status
import requests


@login_required(login_url='authors:login_view')
def view_followers(request, author_id):
    """
    Get the list of followers for a specific author and render the HTML page.
    """
    author = get_object_or_404(Author, id=author_id)
    approved_requests = FollowRequest.objects.filter(followee=author, status='approved')

    foreign_requests = ForeignFollowRequest.objects.filter(followee=author_id, status='approved')

    if not approved_requests.exists() and not foreign_requests.exists():
        return render(request, 'authors/followers_list.html', {'author': author, 'message': "This author has no followers."})
    
    return render(request, 'authors/followers_list.html', {'author': author, 'approved_requests': approved_requests, 'foreign_requests': foreign_requests})

@login_required(login_url='authors:login_view')
def view_followees(request, author_id):
    """
    Get the list of authors a specific author is following and render the HTML page.
    """
    author = get_object_or_404(Author, id=author_id)
    approved_requests = FollowRequest.objects.filter(follower=author, status='approved')

    if not approved_requests.exists():
        return render(request, 'authors/following_list.html', {'author': author, 'message': "This author is not following anyone."})
    
    return render(request, 'authors/following_list.html', {'author': author, 'approved_requests': approved_requests})

@login_required(login_url='authors:login_view')
def view_follow_requests(request, author_id):
    """
    Get the list of follow requests for a specific author and render the HTML page.
    """
    author = get_object_or_404(Author, id=author_id)
    pending_requests = FollowRequest.objects.filter(followee=author, status='pending')

    ## adding foreign requests 
    foreign_requests = ForeignFollowRequest.objects.filter(followee=author_id, status='pending')

    if not pending_requests.exists() and not foreign_requests.exists():
        return render(request, 'authors/follow_requests.html', {'author': author, 'message': "This author has no follow requests."})
    
    return render(request, 'authors/follow_requests.html', {'author': author, 'pending_requests': pending_requests, 'foreign_requests': foreign_requests})

@login_required(login_url='authors:login_view')
def create_follow_request(request, author_id):
    """
    Create a follow request for a specific author.
    """
    follower = get_object_or_404(Author, id=request.user.author.id)
    followee = get_object_or_404(Author, id=author_id)

    # Check if the follow request already exists
    follow_request = FollowRequest.objects.filter(follower=follower, followee=followee).first()
    # Get the referer URL and fall back to a default if not found
    referer_url = request.META.get('HTTP_REFERER', None)

    if follow_request:
        return HttpResponseRedirect(referer_url)

    follow_request = FollowRequest(follower=follower, followee=followee, status='pending')
    follow_request.save()

    return HttpResponseRedirect(referer_url)

# Edit follow request view 
@login_required(login_url='authors:login_view')
def edit_follow_request(request, author_id, follow_request_id, status):
    follow_request = get_object_or_404(FollowRequest, id=follow_request_id)
    
    # Change the status of the follow request : options; pending, approved, denied 
    follow_request.status = status 
    follow_request.save()

    # Check if the other follow request exists and is approved
    # Check if both follow requests are approved
    if status == 'approved':
        other_follow_request = FollowRequest.objects.filter(
            follower=follow_request.followee, followee=follow_request.follower
        ).first()  # `.first()` will return None if no match is found

        if other_follow_request and other_follow_request.status == 'approved':
            # Both users approved each other's follow request, create friendship
            createFriendsip(follow_request.follower.id, follow_request.followee.id)

    if status == 'denied':
        try:
            # Try to get a friendship where either author_1 or author_2 matches the author_id
            friendship = Friend.objects.filter(
                (Q(author_1=author_id) | Q(author_2=author_id))
            ).first()  # Get the first match (if any)
        except Friend.DoesNotExist:
            friendship = None
        if friendship:
            friendship.delete()
    
    # Get the referer URL and fall back to a default if not found
    referer_url = request.META.get('HTTP_REFERER', None)
    if not referer_url:
        # Fall back to a default URL if referer is None
        referer_url = reverse("view_follow_requests", args=[author_id])

    return HttpResponseRedirect(referer_url)

def createFriendsip(author1_id, author2_id):
    serializer = FriendSerializer(data={"author_1":author1_id, "author_2":author2_id})
    if serializer.is_valid():
        print("is valid")
        serializer.save()
    else:
        return Response({"error": serializer.errors}, status=400)
    return 

@login_required(login_url='authors:login_view')
def view_friends(request, author_id):
    """
    Get the list of friends for a specific author and render the HTML page.
    """
    author = get_object_or_404(Author, id=author_id)
    friends = Friend.objects.filter(Q(author_1=author) | Q(author_2=author))

    if not friends.exists():
        return render(request, 'authors/friends_list.html', {'author': author, 'message': "This author has no friends."})
    
    friend_list = []
    for friendship in friends:
        friend = friendship.author_1 if friendship.author_2 == author else friendship.author_2
        friend_list.append(friend)

    return render(request, 'authors/friends_list.html', {'author': author, 'friends': friend_list})

def edit_foreign_follow_request(request, author_id, follow_request_id, status):
    current_author = request.user.author
    follow_request = get_object_or_404(ForeignFollowRequest, id=follow_request_id)

    # Change the status of the follow request : options; pending, approved, denied 
    follow_request.status = status
    follow_request.save()

    # if status is approved, create friendship, denied then remove 
    if status == 'approved':
        ForeignFriend.objects.get_or_create(
            author_1=current_author.global_id, author_2=follow_request.follower
        )
    if status == 'denied':
        try:
            # Try to get a friendship where either author_1 or author_2 matches the author_id
            friendship = ForeignFriend.objects.filter(
                (Q(author_1=current_author.global_id) | Q(author_2=follow_request.follower))
            ).first()  # Get the first match (if any)
        except ForeignFriend.DoesNotExist:
            friendship = None
        if friendship:
            friendship.delete()
            
    # Get the referer URL and fall back to a default if not found
    referer_url = request.META.get('HTTP_REFERER', None)
    if not referer_url:
        # Fall back to a default URL if referer is None
        referer_url = reverse("view_follow_requests", args=[author_id])

    return HttpResponseRedirect(referer_url)


def createForeignFriend(author_1, author_2):
    # create a foreign friend object
    ForeignFriend.objects.create(author_1=author_1, author_2=author_2)