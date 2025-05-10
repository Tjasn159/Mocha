from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Author, Post

# Run: python manage.py test authors.tests.post_test.py
# Reference: https://medium.com/@akshatgadodia/testing-django-and-django-rest-framework-drf-ensuring-reliability-236f0fcbeee6

class TestPostAPIs(TestCase):
    def setUp(self):
        """Set up test authors and posts"""
        self.author = Author.objects.create(
            display_name="TestAuthor",
            bio="Test Author's bio",
            global_id="http://127.0.0.1:8000/authors/test-author",
            host="http://127.0.0.1:8000/",
            github="http://github.com/testauthor"
        )

        self.post = Post.objects.create(
            author=self.author,
            title="Test Post",
            description="This is a test post",
            content="Hello, world!",
            content_type="text/plain",
            visibility="PUBLIC"
        )

        # Initialize API client
        self.client = APIClient()

    def test_create_post(self):
        """Test creating a new post for an author"""
        post_data = {
            "title": "New Post",
            "description": "A new test post",
            "content": "This is a new test post!",
            "content_type": "text/plain",
            "visibility": "PUBLIC"
        }
        response = self.client.post(f'/authors/{self.author.id}/posts/new/', post_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], "Post created successfully")

    def test_get_post(self):
        """Test retrieving a specific post"""
        response = self.client.get(f'/authors/{self.author.id}/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], "Test Post")

    def test_update_post(self):
        """Test updating a post"""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "content": "Updated content",
            "content_type": "text/plain",
            "visibility": "PRIVATE"
        }
        response = self.client.put(f'/authors/{self.author.id}/posts/{self.post.id}/edit/', update_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "Post updated")

        # Check if the post was actually updated
        response = self.client.get(f'/authors/{self.author.id}/posts/{self.post.id}/')
        self.assertEqual(response.data['title'], "Updated Title")
        self.assertEqual(response.data['visibility'], "PRIVATE")

    def test_delete_post(self):
        """Test deleting a post (soft delete by setting visibility to DELETED)"""
        response = self.client.delete(f'/authors/{self.author.id}/posts/{self.post.id}/')

        self.assertEqual(response.status_code, 204)

        # Verify post visibility is now "DELETED"
        response = self.client.get(f'/authors/{self.author.id}/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 403)  # Forbidden since it's deleted
    
    def test_get_all_posts_by_author(self):
        """Test return all posts by an author"""
        response = self.client.get(f'/authors/{self.author.id}/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data, list))
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_post_missing_fields(self):
        """Test to create a post with missing fields"""
        post_data = {
            "title": "Missing Content"
        }
        response = self.client.post(f'/authors/{self.author.id}/posts/new/', post_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
    
    def test_update_post_invalid_id(self):
        """Test updating a post that does not exist (invalid ID)"""
        update_data = {
            "title": "New Title"
        }
        response = self.client.put(f'/authors/{self.author.id}/posts/invalid-id/edit/', update_data, format='json')
        self.assertEqual(response.status_code, 404)



