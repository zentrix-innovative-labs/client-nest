# Facebook Integration API Endpoints

This document lists the backend API endpoints available for Facebook Page management and analytics.

## Endpoints

- **GET /api/facebook/posts/**
  - List all Facebook posts for the page.

- **GET /api/facebook/posts/<post_id>/**
  - Get details for a specific Facebook post.

- **POST /api/facebook/posts/**
  - Create a new post on the Facebook page.

- **GET /api/facebook/posts/<post_id>/comments/**
  - Get all comments for a specific post.

- **GET /api/facebook/posts/<post_id>/reactions/**
  - Get reaction counts for a specific post.

- **GET /api/facebook/posts/<post_id>/insights/**
  - Get analytics (impressions, engagement, etc.) for a specific post.

# LinkedIn Integration API Endpoints

This document lists the backend API endpoints available for LinkedIn account management and posting.

## Endpoints

- **GET /api/linkedin/test-connection/**
  - Test LinkedIn account connection and get account info.

- **POST /api/linkedin/post/**
  - Create a new post on the LinkedIn account.

- **GET /api/social/linkedin/userinfo/**
  - Fetch LinkedIn user profile info (requires authentication).

- **POST /api/social/linkedin/post-image/**
  - Create a new LinkedIn post with an image. Requires 'content' and 'image' in multipart/form-data.

## LinkedIn Integration (Working Endpoints)

### 1. Post to LinkedIn (Text Only)
- **POST** `/api/social/linkedin/post/`
- **Description:** Create a new LinkedIn post (text only) for the authenticated user.
- **Headers:**
  - `Authorization: Bearer <JWT token>`
- **Body:**
  - `content`: The post text (string)
- **Response (201 Created):**
```json
{
    "status": "success",
    "message": "Post published successfully",
    "post_id": "urn:li:share:123456789"
}
```

### 2. Post to LinkedIn with Image
- **POST** `/api/social/linkedin/post-image/`
- **Description:** Create a new LinkedIn post with an image for the authenticated user.
- **Headers:**
  - `Authorization: Bearer <JWT token>`
- **Body:** (multipart/form-data)
  - `content`: The post text (string)
  - `image`: The image file
- **Response (201 Created):**
```json
{
    "status": "success",
    "message": "Post with image published successfully",
    "post_id": "urn:li:share:123456789",
    "asset_urn": "urn:li:digitalmediaAsset:abc123"
}
```

---

**Note:**
- These endpoints are to be consumed by the frontend for Facebook Page management and analytics.
- Do not include sensitive information (like access tokens) in frontend code or documentation.

- These endpoints are to be consumed by the frontend for LinkedIn management and posting.
- Do not include sensitive information (like access tokens) in frontend code or documentation. 