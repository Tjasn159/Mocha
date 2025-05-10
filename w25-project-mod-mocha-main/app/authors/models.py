from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
#This is so fucking stupi

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # change this back once old users gone (no null and blank)
    # Unique, persistent ID for the author
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    
    # Basic Author Information
    display_name = models.CharField(max_length=255, unique=True)  # Author's chosen display name
    bio = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    # Distributed Identity Management
    type = models.CharField(max_length=100, default="author")  # Consistent entity type
    global_id = models.URLField(blank=True)  # Keep as a manually set field
    host = models.URLField()  # Node managing this author
    github = models.URLField(blank=True, null=True)
    profile_image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.display_name

class ForeignAuthor(models.Model):
    id = models.UUIDField(primary_key=True)  # extracted from their URL
    display_name = models.CharField(max_length=255)
    host = models.URLField()  # the node's host
    global_id = models.URLField(unique=True)  # full URL of the remote author

    def __str__(self):
        return f"{self.display_name} @ {self.host}"

class Post(models.Model):
    #I've based the model off of the description provided under 'Main Concepts' for posts
    #uniqe ID for each post; it'll be the primary key within this model
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    global_id = models.URLField(unique=True, blank=True)

    #the foreign key which is used to attatch the post to it's author
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="posts")

    #The post content
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)  

    #content types as 
    CONTENT_TYPES = [
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
        ("image/png;base64", "PNG Image"),
        ("image/jpeg;base64", "JPEG Image"),
    ]

    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES, default="text/plain") #default is plain text

    #post visibility
    VISIBILITY_CHOICES = [
        ("PUBLIC", "Public"),
        ("UNLISTED", "Unlisted"),
        ("PRIVATE", "Private"),
        ("DELETED", "Deleted"),
    ]
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="PUBLIC") # default is public

    #timestamps of when the post was created or updated
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """ Ensure global_id is always set based on the node """
        if not self.global_id:
            self.global_id = f"{self.author.host}api/authors/{self.author.id}/posts/{self.id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.author.display_name}: {self.title[:30] if self.title else 'Untitled Post'}"


class ForeignPost(models.Model):
    id = models.UUIDField(primary_key=True)  # Remote UUID
    global_id = models.URLField(unique=True)
    
    # These are not FK relationships, just stored data from remote nodes
    foreign_author = models.ForeignKey(ForeignAuthor, on_delete=models.CASCADE, related_name="foreign_posts")
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField()
    content_type = models.CharField(max_length=50, default="text/plain")
    visibility = models.CharField(max_length=10, default="PUBLIC")
    published = models.DateTimeField()
    
    # Store remote image in base64
    image_base64 = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"ForeignPost by {self.foreign_author.display_name}"



# Creating the comment model for the posts 
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) #unique ID for each comment
    global_id = models.URLField(unique=True, blank=True) #global ID for the comment

    #foreign key to attatch the comment to the post and link it to the author
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    #the comment content
    comment = models.TextField()
    content_type = models.CharField(max_length=50, default="text/plain") #default is plain text
    published = models.DateTimeField(default=timezone.now) #timestamp for when the comment was published

    def save(self, *args, **kwargs):
        """ Ensure global_id is always set based on the node """
        if not self.global_id:
            #Constructing the URL based on the node's host and the author's ID and the post's ID
            self.global_id = f"{self.author.host}api/authors/{self.author.id}/posts/{self.post.id}/comments/{self.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commented by: {self.author.display_name}: {self.comment[:30] if self.comment else 'Untitled Comment'}"

#This model will keep track of the likes on a post  
class PostLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) #unique ID for each like

    #foreign key to attatch the like to the post and link it to the author
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="post_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    published = models.DateTimeField(default=timezone.now) #timestamp for when the like was published

    global_id = models.URLField(unique=True, blank=True) #global ID for the like

    #Saving the global ID based on the node's host and the author's ID and the post's ID
    def save(self, *args, **kwargs):
        if not self.global_id:
            self.global_id = f"{self.author.host}api/authors/{self.author.id}/posts/{self.post.id}/likes/{self.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Like by: {self.author.display_name} on post: {self.post.title[:30] if self.post.title else 'Untitled Post'}"
    
#This model will keep track of the likes on a comment
class CommentLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) #unique ID for each like

    #foreign key to attatch the like to the comment and link it to the author
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="comment_likes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_likes")
    published = models.DateTimeField(default=timezone.now) #timestamp for when the like was published

    global_id = models.URLField(unique=True, blank=True) #global ID for the like

    #Saving the global ID based on the node's host and the author's ID and the comment's ID
    def save(self, *args, **kwargs):
        if not self.global_id:
            self.global_id = f"{self.author.host}api/authors/{self.author.id}/posts/{self.comment.post.id}/comments/{self.comment.id}/likes/{self.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Like by: {self.author.display_name} on comment: {self.comment.comment[:30] if self.comment.comment else 'Untitled Comment'}"

class FollowRequest(models.Model):
    """
    Handles the follow requests 
    The follower author (author that follows) and the followee author (author being followed)
    """

    follower = models.ForeignKey(Author, related_name="follower", on_delete=models.CASCADE)
    followee = models.ForeignKey(Author, related_name="followee", on_delete=models.CASCADE)

    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')

    def __str__(self):
        return f"{self.follower} wants to follow {self.followee}"
    
class ForeignFollowRequest(models.Model):
    """
    Handles foreign relationships , local authors uuid, foreigns FQID
    """
    follower = models.URLField()
    display_name = models.CharField(max_length=255,  default='unknown')
    followee = models.UUIDField()

    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')

    def __str__(self):
        return f"{self.follower} wants to follow {self.followee}"

class Friend(models.Model):
    """
    Defines the unique friendships , both authors follow each other 
    """
    author_1 = models.ForeignKey(Author, related_name="friends", on_delete=models.CASCADE)
    author_2 = models.ForeignKey(Author, related_name="friends_with", on_delete=models.CASCADE)

    """ A friendship only appears once in the table """
    class Meta:
        unique_together = ('author_1', 'author_2')

    def __str__(self):
        return f"{self.author_1.display_name} and {self.author_2.display_name} are friends"
    
class ForeignFriend(models.Model):  
    """
    Handles foreign friendships, stores both authors global ids 
    """
    author_1 = models.URLField()  # FQID of the first author
    author_2 = models.URLField()  # FQID of the second author
    # This is not a ForeignKey relationship, just stored data from remote nodes

    """ A friendship only appears once in the table """
    class Meta:
        unique_together = ('author_1', 'author_2')

    def __str__(self):
        return f"{self.author_1} and {self.author_2} are friends"

class Node(models.Model):
    host = models.URLField(unique=True)  # Full base URL of the node (e.g. http://example-node.com/)
    username = models.CharField(max_length=255, default='unknown')  # For authentication, take out default later
    password = models.CharField(max_length=255, default=1234)  # For authentication, take out default later
    display_name = models.CharField(max_length=255, default='unknown')  # Display name of the node
    is_active = models.BooleanField(default=True)  # You can use this to enable/disable a node
    inbox_url = models.URLField(blank=True, null=True)  # Optional: custom inbox route
    # You said no authentication is required, so no need for username/password

    def __str__(self):
        return self.display_name

class ForeignComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    global_id = models.URLField(unique=True)
    foreign_author = models.ForeignKey(ForeignAuthor, on_delete=models.CASCADE, related_name="foreign_comments")
    post = models.ForeignKey(ForeignPost, on_delete=models.CASCADE, related_name="foreign_comments")
    comment = models.TextField()
    content_type = models.CharField(max_length=50, default="text/plain")
    published = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.foreign_author.display_name}: {self.comment[:30]}"

    

