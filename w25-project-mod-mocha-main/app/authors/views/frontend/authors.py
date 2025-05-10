from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from authors.models import Author, Post, FollowRequest, Friend, Node
from django.urls import reverse
import uuid
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import markdown
from django.utils.safestring import mark_safe     
import requests 
from django.http import HttpResponseRedirect
from django.contrib import messages

#  Fetch Author by Display Name (HTML)
class AuthorDetailView(generic.DetailView):
    model = Author
    context_object_name = "author"
    template_name = "authors/profile.html"

    def get_object(self):
        display_name = self.kwargs.get('display_name')
        return get_object_or_404(Author, display_name=display_name)
    
def get_friends(author):
        """Returns a list of friend author IDs (both authors must have approved each other)."""
        if not author:
            return []

        friend_ids = set()
        friendships = Friend.objects.filter(Q(author_1=author) | Q(author_2=author))
        
        for f in friendships:
            friend_ids.add(f.author_1.id if f.author_2 == author else f.author_2.id)

        return list(friend_ids)
    
class AuthorDetailByIDView(generic.DetailView):
    model = Author
    context_object_name = "author"
    template_name = "authors/profile.html"

    def get_object(self):
        author_id = self.kwargs.get('author_id')
        return get_object_or_404(Author, id=author_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_object()
        context["followers"] = FollowRequest.objects.filter(followee=author, status="approved").count()

        # Check if the logged-in user is following the author
        if self.request.user.is_authenticated:
            context["is_following"] = FollowRequest.objects.filter(follower=self.request.user.author, followee=author, status="approved").exists()
        else:
            context["is_following"] = False

        # Get friends of the author
        friends = get_friends(self.request.user.author)
        context["is_friend"] = author.id in friends

        # Check if the logged-in user is viewing their own profile
        is_own_profile = self.request.user.author == author

        context["followees"] = FollowRequest.objects.filter(follower=author, status="approved").count()
        context["post_count"] = author.posts.exclude(visibility='DELETED').count()

        # Filter posts based on visibility and relationship status
        if self.request.user.is_authenticated:
            if is_own_profile:
                # Always show all posts for the user's own profile
                posts = author.posts.exclude(visibility='DELETED')
            elif context["is_friend"]:
                # Friends can see both private and public posts
                posts = author.posts.exclude(visibility='DELETED')
            else:
                # Only show public posts if not friends
                posts = author.posts.filter(visibility='PUBLIC').exclude(visibility='DELETED')
        else:
            # For unauthenticated users, only show public posts
            posts = author.posts.filter(visibility='PUBLIC').exclude(visibility='DELETED')

        for post in posts:
            if post.content_type == "text/markdown":
                post.content = mark_safe(markdown.markdown(post.content))

        context["posts"] = posts.order_by("-created_at")

        return context
    
class AuthorUpdateView(View):
    """Allows updating an author's profile."""

    def get(self, request, author_id):
        """Render author update form."""
        author = get_object_or_404(Author, id=author_id)
        return render(request, "authors/update_author.html", {"author": author})

    def post(self, request, author_id):
        """Handle author update from form submission."""
        author = get_object_or_404(Author, id=author_id)

        # Get form data
        author.display_name = request.POST.get("display_name", author.display_name)
        author.github = request.POST.get("github", author.github)
        author.bio = request.POST.get("bio", author.bio)
        author.profile_image = request.POST.get("profile_image", author.profile_image)
        author.save()

        #  Fix: Use 'authors:author_profile_id' instead of 'author_profile_id'
        return redirect(reverse("authors:author_profile_id", kwargs={"author_id": author.id}))

class AuthorCreateView(View):
    """Handles creating a new author using an HTML form."""

    def get(self, request):
        """Render the form to create a new author."""
        return render(request, "authors/create_author.html")

    def post(self, request):
        """Handle form submission and create an author."""
        try:
            display_name = request.POST.get("display_name")
            github = request.POST.get("github", "")
            profile_image = request.POST.get("profile_image", "")
            author_id = uuid.uuid4()
            global_id = f"http://127.0.0.1:8000/api/authors/{author_id}"

            author = Author.objects.create(
                id=author_id,
                display_name=display_name,
                host="http://127.0.0.1:8000",
                global_id=global_id,
                github=github,
                profile_image=profile_image,
            )

            # Fix: Use 'authors:author_profile_id' instead of 'author_profile_id'
            return redirect(reverse("authors:author_profile_id", kwargs={"author_id": author.id}))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# Get a list of all authors 
@login_required(login_url='authors:login_view')
def get_authors(request):
    # exclude the current author from the list
    current_author = request.user.author
    authors = Author.objects.exclude(id=current_author.id)
    # return a dictionary of authors with relationship status with current author
    authors_list = [] # [{author: author, relationship: status, follow_request: follow_request}]

    for author in authors:
        follow_request = FollowRequest.objects.filter(followee=author, follower=current_author).first()
        if follow_request:
            authors_list.append({"author": author, "relationship": follow_request.status, "follow_request": follow_request})
        else:
            authors_list.append({"author": author, "relationship": "none", "follow_request": follow_request})
    return render(request, "authors/authors_list.html", {"authors_list": authors_list})

# Get a list of all foreign authors 
@login_required(login_url='authors:login_view')
def get_foreign_authors(request):
    """
    Fetch all foreign authors and render the HTML page.
    """
    authors = []
    # fetch authors from the all the registered foreign servers
    nodes = Node.objects.all()
    for node in nodes:
        try:
            # host + api/authors/
            auth = (node.username, node.password)  
            headers = {"Content-Type": "application/json", "X-original-host": "http://[2605:fd00:4:1001:f816:3eff:fec9:f508]:8000/api/"}
            response = requests.get(f"{node.host}/api/authors/", headers=headers, auth=auth)
            response_data = response.json()
            if response.status_code == 200:
                authors.extend(response_data["authors"])  # Assuming the response is a JSON list of authors
        except Exception as e:
            print(f"Error fetching authors from {node.host}: {e}")

    return render(request, "authors/foreign_authors.html", {"authors": authors})

@login_required(login_url='authors:login_view')
def send_follow_request(request):
    """
    Send a follow request to a foreign author.
    """
    current_author = request.user.author
    if request.method == "POST":
        try:
            # Get the foreign author information 
            fa_id = request.POST.get("foreign_author_id")
            fa_dn = request.POST.get("foreign_author_display_name")
            fa_host = request.POST.get("foreign_author_host")
            print(fa_id, fa_dn, fa_host)
            # Get the Node for the foreign author
            try:
                # Normalize the host by removing any trailing path (e.g., "/api") and ensuring it ends with a "/"
                if "/api" in fa_host:
                    normalized_host = fa_host.rstrip('/').split('/api')[0] + '/'
                else:
                    normalized_host = fa_host.rstrip('/') + '/'

                node = Node.objects.get(host=normalized_host)
            except Node.DoesNotExist:
                messages.error(request, f"Node for host {fa_host} not found.")
                return HttpResponseRedirect(reverse("get_foreign_authors"))
            
            # Create the follow request, actor wants to follow the object 
            follow_request_payload = {
                "type": "follow",
                "actor": {
                    "id": current_author.global_id,
                    "displayName": current_author.display_name,
                    "host": current_author.host,
                },
                "object": {
                    "id": fa_id,
                    "displayName": fa_dn,
                    "host": fa_host,
                }
            }
            print(follow_request_payload)
            # Add authentication headers (Basic Authentication) for the external request
            print(f'The display name is: {node.display_name}')
            if (node.display_name == 'Indigo'):
                auth = ('Vasu', 'Arnv2004')
            else:
                auth = (node.username, node.password)  
            headers = {"Content-Type": "application/json", "X-original-host": "http://[2605:fd00:4:1001:f816:3eff:fec9:f508]:8000/api/"}

            # send to author.id/inbox 
            response = requests.post(f"{fa_id}/inbox", json=follow_request_payload, headers=headers, auth=auth)

            # Check if the request was successful
            if response.status_code == 200 or response.status_code == 201:
                messages.success(request, f"Follow request sent to {fa_dn} successfully!")
            else:
                messages.error(request, f"Failed to send follow request to {fa_dn}. Server responded with status code {response.status_code}.")
        except Exception as e:
            print(f"Error sending follow request: {e}")

    # Get the referer URL and fall back to a default if not found
    referer_url = request.META.get('HTTP_REFERER', None)
    if not referer_url:
        # Fall back to a default URL if referer is None
        referer_url = reverse("get_foreign_authors")
    return HttpResponseRedirect(referer_url)
