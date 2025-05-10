# Comment and likes documentation

## Endpoints Overview

## 1. Creating a new comment on a post

- **Method:** `POST`
- **Endpoint:** `://service/authors/{author_id}/posts/comments/`
- **Description:** Allows the author to add a new comment on the given post.

### Response:
- ### Request Body (JSON):
```json
{
    "comment": "This is my comment text.",
    "content_type": "text/plain" 
}
```
**Commented succecfully**
- **Status Code:** `201`
```json
{
  "type": "comment",
  "author": {
    "type": "author",
    "id": "http://service/api/authors/111",
    "displayName": "Greg Johnson",
    "host": "http://service/api/",
    "url": "http://service/api/authors/111"
  },
  "comment": "This is my comment text.",
  "contentType": "text/plain",
  "published": "2025-02-22T15:30:00+00:00",
  "id": "d57a7c0e-3b0c-4f7a-9c11-8f9f8f9c8a7b",
  "post": "http://service/api/authors/222/posts/333",
  "likes": {}
}
```
**If the required fields are missing**
- **Status Code:** `400`
```json
{
  "error": "Invalid JSON format"
}
```
**If the specified post does not exist**
- **Status Code:** `404`
```json
{
  "message": "Post not found."
}
```
**If the specified author does not exist**
- **Status Code:** `404`
```json
{
  "message": "Author not found."
}
```

---

## 2. List Comments for a Post
- **Method:** `GET`
- **Endpoint:** `/authors/{author_id}/posts/{post_id}/comments/`
- **Description:** Retrieves a list of comments on a specified post

### Response:
**When the comments exist**
- **Status Code:** `200`
```json
{
  "type": "comments",
  "page": "http://service/api/authors/222/posts/333/comments",
  "id": "http://service/api/authors/222/posts/333/comments",
  "page_number": 1,
  "size": 5,
  "count": 12,
  "src": [
    {
      "type": "comment",
      "author": {
        "type": "author",
        "id": "http://service/api/authors/111",
        "displayName": "Greg Johnson",
        "host": "http://service/api/",
        "url": "http://service/api/authors/111"
      },
      "comment": "This is my comment text.",
      "contentType": "text/plain",
      "published": "2025-02-22T15:30:00+00:00",
      "id": "http://service/api/authors/111/posts/333/comments/d57a7c0e-3b0c-4f7a-9c11-8f9f8f9c8a7b",
      "post": "http://service/api/authors/222/posts/333",
      "likes": {}
    }
  ]
}
```
**If the post does not exist**
- **Status Code:** `404`
```json
{
    "message": "Post not found."
}
```

---

## 3. Liking a Post
- **Method:** `POST`
- **Endpoint:** `/authors/{author_id}/posts/{post_id}/like/`
- **Description:** Allowing the author to like a specified post.

### Request Body:
```json
{} //Typically empty
```

### Response:
**When a new like is created and added to the post**
- **Status Code:** `201`
```json
{
  "type": "like",
  "id": "http://service/api/authors/111/posts/333/likes/789",
  "author": {
    "type": "author",
    "id": "http://service/api/authors/111",
    "page": "http://service/api/authors/111",
    "displayName": "Greg Johnson",
    "host": "http://service/api/",
    "url": "http://service/api/authors/111"
  },
  "published": "2025-02-22T15:35:00+00:00",
  "object": "http://service/api/authors/222/posts/333",
  "count": 10
}
```
**If the user has already liked a post**
- **Status Code:** `200`
```json
{
  "message": "You have already liked this post.",
  "count": 10
}
```
**If the specified post does not exist**
- **Status Code:** `404`
```json
{
  "message": "Post not found."
}
```
**If the specified author does not exist**
- **Status Code:** `404`
```json
{
  "message": "Author not found."
}
```

---

## 4. Liking a comment
- **Method:** `POST`
- **Endpoint:** `/authors/{author_id}/posts/{post_id}/comments/{comment_id}/like/`
- **Descrption:** Allows the author to like a specific comment on a post

### Request Body
```json
{} //Typically empty
```

### Response:
**When a new like is created and added to the comment**
- **Status Code:** `201`
```json
{
  "type": "like",
  "id": "http://service/api/authors/111/posts/333/comments/abc/likes/def",
  "author": {
    "type": "author",
    "id": "http://service/api/authors/111",
    "page": "http://service/api/authors/111",
    "displayName": "Greg Johnson",
    "host": "http://service/api/",
    "url": "http://service/api/authors/111"
  },
  "published": "2025-02-22T15:40:00+00:00",
  "object": "http://service/api/authors/222/posts/333/comments/abc",
  "count": 3
}
```
**If the user has already liked the comment**
- **Status Code:** `200`
```json
{
  "message": "You have already liked this comment.",
  "count": 3
}
```
**When the comment does not exist**
- **Status Code:** `404`
```json
{
  "message": "Comment not found."
}
```


