from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Author, FollowRequest

# Run : python manage.py test authors.tests.follow_test
# reference : https://medium.com/@akshatgadodia/testing-django-and-django-rest-framework-drf-ensuring-reliability-236f0fcbeee6

class TestFollowAPIs(TestCase):
    def setUp(self):
         # Create authors
        self.author1 = Author.objects.create(display_name="author1", bio="author1's bio", global_id="http://node1/api/authors/author1", host="http://node1/api/", github="http://github.com/author1")
        self.author2 = Author.objects.create(display_name="author2", bio="author2's bio", global_id="http://node1/api/authors/author2", host="http://node1/api/", github="http://github.com/author2")
        self.author3 = Author.objects.create(display_name="author3", bio="author3's bio", global_id="http://node1/api/authors/author3", host="http://node1/api/", github="http://github.com/author3")

        # Create a follow request from author2 to author1 (approved)
        self.follow_request = FollowRequest.objects.create(
            follower=self.author2,
            followee=self.author1,
            status="approved"
        )
        
        # Create a follow request from author3 to author1 (not approved)
        self.follow_request2 = FollowRequest.objects.create(
            follower=self.author3,
            followee=self.author1,
            status="pending"
        )

        # Initialize the API client
        self.client = APIClient()

    def test_get_followers(self):
        # Test for author1 (should return 1 follower)
        response = self.client.get(f'/api/authors/{self.author1.id}/followers/')
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the correct follower
        self.assertIn('followers', response.data)
        self.assertEqual(len(response.data['followers']), 1)  # Should only return author2
        self.assertEqual(response.data['followers'][0]['display_name'], "author2")# Test when author has no followers

        # Test for author3 (should return no followers)
        response = self.client.get(f'/api/authors/{self.author3.id}/followers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "This author has no followers.")



    def test_get_follower(self):
        # Test for a valid follower (author2 follows author1)
        response = self.client.get(f'/api/authors/{self.author1.id}/followers/{self.author2.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['display_name'], "author2")
        
        # Test for an invalid follower (author3 does not follow author1)
        response = self.client.get(f'/api/authors/{self.author1.id}/followers/{self.author3.id}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], "author3 does not follow author1.")

    def test_add_follower(self):
        # Test for adding a follower (author3 follows author1)
        response = self.client.put(f'/api/authors/{self.author1.id}/followers/{self.author3.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "author3 now follows author1.")

        # Check if the follow request was created
        follow_request = FollowRequest.objects.filter(follower=self.author3, followee=self.author1).first()
        self.assertEqual(follow_request.status, "approved")

    def test_remove_follower(self):
        # Test for removing a follower (author2 unfollows author1)
        response = self.client.delete(f'/api/authors/{self.author1.id}/followers/{self.author2.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "author2 no longer follows author1.")

        # Check if the follow request was deleted
        follow_request = FollowRequest.objects.filter(follower=self.author2, followee=self.author1).first()
        self.assertEqual(follow_request.status, "denied")

    def test_add_follower_already_follows(self):
        # Test for following an author that you alreayd follow
        # Author 1 follows Author 2 but author2 already has an approved follow
        response = self.client.put(f'/api/authors/{self.author1.id}/followers/{self.author2.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("already follows", response.data['message'])

    def test_remove_nonexistent_follower(self):
        # Test for trying to remove a nonesistent follower (author3 does not have an approved follow yet)
        response = self.client.delete(f'/api/authors/{self.author1.id}/followers/{self.author3.id}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], "author3 does not follow author1.")
    
    def test_add_follower_with_pending_request(self):
        # Test for trying to follow an author when a pending request already exists (author3 already has a pending request, should upgrade to approved)
        response = self.client.put(f'/api/authors/{self.author1.id}/followers/{self.author3.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "author3 now follows author1.")
        follow = FollowRequest.objects.get(follower=self.author3, followee=self.author1)
        self.assertEqual(follow.status, "approved")

    def test_get_follower_invalid_author_ids(self):
        # Test for requesting with an invalid UUID for follower or followee
        # Invalid author id
        response = self.client.get(f'/api/authors/invalid-id/followers/{self.author2.id}')
        self.assertEqual(response.status_code, 404)

        # Invalid follower id
        response = self.client.get(f'/api/authors/{self.author1.id}/followers/invalid-id')
        self.assertEqual(response.status_code, 404)