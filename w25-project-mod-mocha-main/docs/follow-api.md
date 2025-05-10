# Follower Management API Documentation


## Endpoints Overview

### **1. Get All Followers**

- **Method**: `GET`
- **Endpoint**: `://service/api/authors/{author_id}/followers/`
- **Description**: Retrieves all followers for the user with the specified ID.

- **Response**:
  - Ex. if given author has followers
  - Status Code : `200` 

```json
{
  "type": "followers",
  "followers": [
    {
      "type": "author",
      "id": "http://nodebbbb/api/authors/222",
      "host": "http://nodebbbb/api/",
      "displayName": "Lara Croft",
      "page": "http://nodebbbb/authors/222",
      "github": "http://github.com/laracroft",
      "profileImage": "http://nodebbbb/api/authors/222/posts/217/image"
    },
    {
      // Second follower author object
    },
    {
      // Third follower author object
    }
  ]
}
```
  - Ex. if given author has no followers
  - Status Code : `200` 
```json
{        "message": "This author has no followers."      }
```

### **2. Get A Follower**
- **Method**: `GET`
- **Endpoint**: `://service/api/authors/{author_id}/followers/{follower_id}`
- **Description**: Retrives a specific follower of a given author ID
- **Response**:
  - ex. if laura follows greg
  - Status Code : `200` 
```json
{
        "type":"author",
        "id":"http://nodebbbb/api/authors/222",
        "host":"http://nodebbbb/api/",
        "displayName":"Lara Croft",
        "page":"http://nodebbbb/authors/222",
        "github": "http://github.com/laracroft",
        "profileImage": "http://nodebbbb/api/authors/222/posts/217/image"
}
```
  - ex. if laura does NOT follow greg
  - Status Code : `404` 
```json
{        "message": "Lara Croft does not follow Greg."      }
```
