# Author Management API Documentation

## Endpoints Overview

This API allows for the creation, retrieval, and updating of author profiles.

---

## 1. Get All Authors
- **Method:** `GET`
- **Endpoint:** `://service/api/authors/`
- **Description:** Retrieves a list of all authors.

### Response:
**If authors exist**
- **Status Code:** `200`
```json
{
  "type": "authors",
  "authors": [
    {
      "type": "author",
      "id": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000",
      "host": "http://service/api/",
      "displayName": "Alice",
      "page": "http://service/authors/123e4567-e89b-12d3-a456-426614174000",
      "github": "http://github.com/alice",
      "profileImage": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000/image"
    }
  ]
}
```
**If no authors exist**
- **Status Code:** `200`
```json
{
  "message": "No authors found."
}
```

---

## 2. Get a Specific Author by UUID
- **Method:** `GET`
- **Endpoint:** `://service/api/authors/{author_id}/`
- **Description:** Retrieves an author’s details using their unique UUID.

### Response:
**If author exists**
- **Status Code:** `200`
```json
{
  "type": "author",
  "id": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000",
  "host": "http://service/api/",
  "displayName": "Alice",
  "page": "http://service/authors/123e4567-e89b-12d3-a456-426614174000",
  "github": "http://github.com/alice",
  "profileImage": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000/image"
}
```
**If author does not exist**
- **Status Code:** `404`
```json
{
  "message": "Author not found."
}
```

---

## 3. Get a Specific Author by Display Name
- **Method:** `GET`
- **Endpoint:** `://service/api/authors/name/{display_name}/profile/`
- **Description:** Retrieves an author’s details using their display name.

### Response:
**If author exists**
- **Status Code:** `200`
```json
{
  "type": "author",
  "id": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000",
  "host": "http://service/api/",
  "displayName": "Alice",
  "page": "http://service/authors/123e4567-e89b-12d3-a456-426614174000",
  "github": "http://github.com/alice",
  "profileImage": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000/image"
}
```
**If author does not exist**
- **Status Code:** `404`
```json
{
  "message": "No author found with display name Alice."
}
```

---

## 4. Create a New Author
- **Method:** `POST`
- **Endpoint:** `://service/api/authors/create/`
- **Description:** Creates a new author.

### Request Body (JSON):
```json
{
  "display_name": "NewAuthor",
  "host": "http://service/api/",
  "github": "http://github.com/newauthor",
  "profileImage": "http://service/api/authors/456e1234-e89b-12d3-a456-426614174222/image"
}
```
### Response:
**If author is created successfully**
- **Status Code:** `201`
```json
{
  "id": "http://service/api/authors/456e1234-e89b-12d3-a456-426614174222",
  "global_id": "http://service/api/authors/456e1234-e89b-12d3-a456-426614174222",
  "displayName": "NewAuthor",
  "host": "http://service/api/",
  "github": "http://github.com/newauthor",
  "profileImage": "http://service/api/authors/456e1234-e89b-12d3-a456-426614174222/image"
}
```
**If required fields are missing**
- **Status Code:** `400`
```json
{
  "error": "Missing required field: display_name"
}
```

---

## 5. Update an Existing Author
- **Method:** `PUT`
- **Endpoint:** `://service/api/authors/{author_id}/update/`
- **Description:** Updates an author's details.

### Request Body (JSON):
```json
{
  "display_name": "UpdatedAuthor",
  "github": "http://github.com/updatedauthor",
  "profileImage": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000/image"
}
```
### Response:
**If update is successful**
- **Status Code:** `200`
```json
{
  "message": "Author updated successfully",
  "id": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000",
  "displayName": "UpdatedAuthor",
  "github": "http://github.com/updatedauthor",
  "profileImage": "http://service/api/authors/123e4567-e89b-12d3-a456-426614174000/image"
}
```
**If author is not found**
- **Status Code:** `404`
```json
{
  "message": "Author not found."
}
```

