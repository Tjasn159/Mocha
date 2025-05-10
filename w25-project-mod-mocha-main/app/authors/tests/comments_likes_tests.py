from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Author, Post, Comment, CommentLike, PostLike
import uuid
import json

# Run: python manage.py test authors.tests.comments_likes_tests
# Reference: https://medium.com/@akshatgadodia/testing-django-and-django-rest-framework-drf-ensuring-reliability-236f0fcbeee6
# References: ChatGpt, GeeksForGeeks, StackOverflow, Django Documentation
# References: https://www.django-rest-framework.org/api-guide/testing/

class TestCommentLikeAPIs(TestCase):
    def setUp(self):
        '''Creating 2 authors and a post'''
        self.author1 = Author.objects.create(
            id = uuid.uuid4(),
            display_name = "TestAuthor1",
            bio = "Test Author1 bio",
            global_id = "http://127.0.0.1:8000/authors/testauthor1",
            host = "http://127.0.0.1:8000/",
            github = "http://github.com/testauthor1"
        )
        self.author2 = Author.objects.create(
            id = uuid.uuid4(),
            display_name = "TestAuthor2",
            bio = "Test Author2 bio",
            global_id = "http://127.0.0.1:8000/authors/testauthor2",
            host = "http://127.0.0.1:8000/",
            github = "http://github.com/testauthor2"
        )
        # create a post for author2
        self.post = Post.objects.create(
            id = uuid.uuid4(),
            author = self.author2,
            title = "Test Post",
            description = "This is a test post",
            content = "Hello, world!",
            content_type = "text/plain",
            visibility = "PUBLIC",
            created_at = timezone.now()
        )
        self.client = APIClient() # Initialize API client

    def test_create_comment(self):
        '''Testing that an author can create a comment on a post'''
        url = reverse('authors:create-comment', kwargs={
            'author_id': self.author2.id,
            'post_id': self.post.id
        })
        data = {
            'comment': 'This is a test comment',
            "content_type": "text/plain",
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201) # Checking that the response is 201
        data = response.json()
        self.assertEqual(data.get("type"), "comment") # Checking that the type is comment
        self.assertEqual(data.get("comment"), "This is a test comment") # Checking that the comment is correct
        #Checking that the post reference is correct
        self.assertIn(str(self.post.id), data.get("post"))

    def test_list_comment(self):
        '''Testing listing the comments on a post'''
        # create 2 comments
        comment1 = Comment.objects.create(
            id = uuid.uuid4(),
            author = self.author1,
            post = self.post,
            comment = "This is a test comment 1",
            content_type = "text/plain",
            published = timezone.now()
        )
        comment2 = Comment.objects.create(
            id = uuid.uuid4(),
            author = self.author2,
            post = self.post,
            comment = "This is a test comment 2",
            content_type = "text/plain",
            published = timezone.now()
        )
        url = reverse('authors:all-comments', kwargs={
            'post_id': self.post.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()  
        self.assertEqual(data.get("type"), "comments") # Checking that the type is comments
        self.assertEqual(data.get("page_number"), 1) # Checking that the page number is 1
        self.assertEqual(data.get("count"), 2)        # Checking that the count is 2
        self.assertEqual(len(data.get("src")), 2) # Checking that there are 2 comments
        # Checking that the comments are correct
        self.assertEqual(data.get("src")[0].get("comment"), "This is a test comment 2")
        self.assertEqual(data.get("src")[1].get("comment"), "This is a test comment 1")

    def test_like_post(self):
        '''Testing that an author can like a post'''
        url = reverse('authors:like-post', kwargs={
            'author_id': self.author1.id,
            'post_id': self.post.id
        })
        #This will like the post for the fist time
        response1 = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response1.status_code, 201) # Checking that the response is 201
        data1 = response1.json()
        self.assertEqual(data1.get("type"), "like") # Checking that the type is like
        first_count = data1.get("count")
        self.assertIsNotNone(first_count) # Checking that the count is not None

        #This will like the post for the second time
        response2 = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response2.status_code, 200) # Checking that the response is 201
        data2 = response2.json()
        self.assertEqual(data2.get("message"), "You have already liked this post.") # Checking that the message is correct
        self.assertEqual(data2.get("count"), first_count) # Checking that the count is the same as the first time

    def test_like_comment(self):
        '''Testing that an author can like a comment'''
        # create a comment
        comment = Comment.objects.create(
            id = uuid.uuid4(),
            author = self.author2,
            post = self.post,
            comment = "This is a test comment for liking",
            content_type = "text/plain",
            published = timezone.now()
        )
        url = reverse('authors:like-comment', kwargs={
            'author_id': self.author1.id,
            'post_id': self.post.id,
            'comment_id': comment.id
        })

        #This is the first like attempt on the comment
        response1 = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response1.status_code, 201)
        data1 = response1.json()
        self.assertEqual(data1.get("type"), "like")
        first_count = data1.get("count")
        self.assertIsNotNone(first_count)   

        #This is the second like attempt on the comment
        response2 = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data2.get("message"), "You have already liked this comment.")
        self.assertEqual(data2.get("count"), first_count)
    
    def test_comment_deletion_removes_likes(self):
        'Testing that upon deletion of a comment, its associated likes are also deleted.'
        # Create a comment
        comment = Comment.objects.create(
            id = uuid.uuid4(),
            author = self.author2,
            post = self.post,
            comment = "This is a test comment for deletion",
            content_type = "text/plain",
            published = timezone.now()
        )
        url = reverse('authors:like-comment', kwargs={
            'author_id': self.author1.id,
            'post_id': self.post.id,
            'comment_id': comment.id
        })

        #Liking the comment
        response1 = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response1.status_code, 201)
        data1 = response1.json()
        self.assertEqual(data1.get("type"), "like")
        first_count = data1.get("count")
        self.assertIsNotNone(first_count)

        # Deleting the comment
        comment.delete()

        # Assuring likes on the comment are also deleted
        self.assertEqual(CommentLike.objects.filter(comment=comment).count(), 0)

    def test_delete_post_removes_comments_and_likes(self):
        '''Testing that deleting a post also removes its comments and likes'''
        # Step 1: Create a comment
        Comment.objects.create(
            id=uuid.uuid4(),
            author=self.author1,
            post=self.post,
            comment="Comment for deleted post",
            content_type="text/plain",
            published=timezone.now()
        )

        # Step 2: Like the post
        like_url = reverse('authors:like-post', kwargs={
            'author_id': self.author1.id,
            'post_id': self.post.id
        })
        self.client.post(like_url, json.dumps({}), content_type='application/json')

        # Step 3: Confirm comment and like exist
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)
        self.assertEqual(PostLike.objects.filter(post=self.post).count(), 1)

        # Step 4: Delete the post
        self.post.delete()

        # Step 5: Confirm cascade deletion
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 0)
        self.assertEqual(PostLike.objects.filter(post=self.post).count(), 0)

