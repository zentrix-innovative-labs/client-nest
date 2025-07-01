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

---

**Note:**
- These endpoints are to be consumed by the frontend for Facebook Page management and analytics.
- Do not include sensitive information (like access tokens) in frontend code or documentation.

- These endpoints are to be consumed by the frontend for LinkedIn management and posting.
- Do not include sensitive information (like access tokens) in frontend code or documentation. 