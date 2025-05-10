from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Author

# Run : python manage.py test authors.tests.test_author_api
# Reference : https://medium.com/@akshatgadodia/testing-django-and-django-rest-framework-drf-ensuring-reliability-236f0fcbeee6

class TestAuthorAPIs(TestCase):
    def setUp(self):
        """Set up test data and API client"""
        self.client = APIClient()

        # Create sample authors
        self.author1 = Author.objects.create(
            display_name="author1",
            bio="Author 1's bio",
            global_id="http://node1/authors/author1",
            host="http://node1/",
            github="http://github.com/author1"
        )

        self.author2 = Author.objects.create(
            display_name="author2",
            bio="Author 2's bio",
            global_id="http://node1/authors/author2",
            host="http://node1/",
            github="http://github.com/author2"
        )

        self.create_url = "/authors/create/"
        self.list_url = "/authors/"
        self.detail_url = f"/authors/{self.author1.id}/"
        self.update_url = f"/authors/{self.author1.id}/update/"
        self.profile_url = f"/authors/name/{self.author1.display_name}/profile/"

    def test_create_author(self):
        """Test creating a new author"""
        data = {
            "display_name": "NewAuthor",
            "host": "http://node1/",
            "github": "https://github.com/newauthor",
            "profile_image": "https://example.com/new-profile.jpg"
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["display_name"], "NewAuthor")

    def test_list_authors(self):
        """Test fetching all authors"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("authors", response.data)
        self.assertEqual(len(response.data["authors"]), 2)

    def test_get_author_by_id(self):
        """Test fetching a specific author by UUID"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["display_name"], self.author1.display_name)

    def test_get_author_by_display_name(self):
        """Test fetching an author by display name"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["display_name"], self.author1.display_name)

    def test_update_author(self):
        """Test updating an author's profile"""
        data = {
            "display_name": "UpdatedAuthor",
            "github": "https://github.com/updatedauthor",
            "profile_image": "https://example.com/updated-profile.jpg"
        }
        response = self.client.put(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify changes were saved
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.display_name, "UpdatedAuthor")

    def test_get_nonexistent_author(self):
        """Test fetching a non-existing author should return 404"""
        response = self.client.get("/authors/nonexistent-id/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "Author not found.")

    def test_create_author_missing_fields(self):
        """Test creating an author with missing required fields"""
        data = {
            "github": "https://github.com/incomplete"
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
    
    def test_update_nonexistent_author(self):
        """Test updating a non-existent author"""
        data = {
            "display_name": "ShouldFail"
        }
        response = self.client.put("/authors/invalid-id/update/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "Author not found.")


