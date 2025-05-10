# Post Management API Documentation

## Endpoints Overview

### 1. Get All Posts by an Author

- **Method:** `GET`
- **Endpoint:** `://service/authors/{author_id}/posts/`
- **Description:** Retrieves all posts created by the specified author.
- **Response:**

  - **Ex. if given author has posts:**
  - **Status Code:** `200`
  
  ```json
  {
    "type": "posts",
    "posts": [
      {
        "id": "http://127.0.0.1:8000/authors/123/posts/456",
        "title": "My First Post",
        "description": "A short description",
        "content": "This is my first post!",
        "contentType": "text/plain",
        "visibility": "PUBLIC",
        "created_at": "2025-02-20T00:48:15.028406+00:00",
        "updated_at": "2025-02-20T00:48:15.028406+00:00"
      }
    ]
  }
  ```

  - **Ex. if given author has no posts:**
  - **Status Code:** `200`
  
  ```json
  {
    "message": "No posts made by this author."
  }
  ```

### 2. Get a Specific Post

- **Method:** `GET`
- **Endpoint:** `://service/authors/{author_id}/posts/{post_id}/`
- **Description:** Retrieves a single post by the given author.
- **Response:**

  - **Ex. if the post exists:**
  - **Status Code:** `200`
  
  ```json
  {
    "id": "http://127.0.0.1:8000/authors/123/posts/456",
    "title": "My First Post",
    "description": "A short description",
    "content": "This is my first post!",
    "contentType": "text/plain",
    "visibility": "PUBLIC",
    "created_at": "2025-02-20T00:48:15.028406+00:00",
    "updated_at": "2025-02-20T00:48:15.028406+00:00"
  }
  ```

  - **Ex. if the post does not exist:**
  - **Status Code:** `404`
  
  ```json
  {
    "message": "Post not found."
  }
  ```

### 3. Create a New Post

- **Method:** `POST`
- **Endpoint:** `://service/authors/{author_id}/posts/new/`
- **Description:** Allows an author to create a new post.
- **Request Body:**
  
  ```json
  {
    "title": "My New Post",
    "description": "Brief description",
    "content": "This is the content of my new post.",
    "contentType": "text/plain",
    "visibility": "PUBLIC"
  }
  ```
- **Response:**
  - **Status Code:** `201`
  
  ```json
  {
    "message": "Post created successfully",
    "post_id": "http://127.0.0.1:8000/authors/123/posts/789"
  }
  ```

### 4. Update a Post

- **Method:** `PUT`
- **Endpoint:** `://service/authors/{author_id}/posts/{post_id}/edit/`
- **Description:** Allows an author to update an existing post.
- **Request Body:**
  
  ```json
  {
    "title": "Updated Post Title",
    "description": "Updated description",
    "content": "Updated post content.",
    "contentType": "text/plain",
    "visibility": "PUBLIC"
  }
  ```
- **Response:**
  - **Status Code:** `200`
  
  ```json
  {
    "message": "Post updated successfully",
    "post_id": "http://127.0.0.1:8000/authors/123/posts/456"
  }
  ```

### 5. Delete a Post

- **Method:** `DELETE`
- **Endpoint:** `://service/authors/{author_id}/posts/{post_id}/`
- **Description:** Allows an author to delete a post. Instead of deleting it from the database, the visibility is set to `DELETED`.
- **Response:**
  - **Status Code:** `204`
  
  ```json
  {
    "message": "Post deleted"
  }
  ```

