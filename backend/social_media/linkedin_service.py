import requests
from .linkedin_config import LINKEDIN_API_BASE_URL

class LinkedInService:
    def __init__(self, social_account):
        self.access_token = social_account.access_token
        self.account_id = social_account.account_id

    def get_account_info(self):
        url = f"{LINKEDIN_API_BASE_URL}me"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to fetch LinkedIn account info')

    def post_content(self, content):
        url = f"{LINKEDIN_API_BASE_URL}ugcPosts"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        payload = {
            "author": f"urn:li:person:{self.account_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception('Failed to post content to LinkedIn')

    def get_userinfo(self):
        url = 'https://api.linkedin.com/v2/userinfo'
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to fetch LinkedIn user info')

    def register_image_upload(self):
        url = f"{LINKEDIN_API_BASE_URL}assets?action=registerUpload"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        payload = {
            "registerUploadRequest": {
                "owner": f"urn:li:person:{self.account_id}",
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [
                    {
                        "identifier": "urn:li:userGeneratedContent",
                        "relationshipType": "OWNER"
                    }
                ]
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception('Failed to register image upload')

    def upload_image(self, upload_url, image_data):
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/octet-stream'
        }
        response = requests.put(upload_url, headers=headers, data=image_data)
        if response.status_code in [200, 201]:
            return True
        else:
            raise Exception('Failed to upload image to LinkedIn')

    def post_content_with_image(self, content, asset_urn):
        url = f"{LINKEDIN_API_BASE_URL}ugcPosts"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        payload = {
            "author": f"urn:li:person:{self.account_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": content},
                            "media": asset_urn,
                            "title": {"text": "Image"}
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception('Failed to post content with image to LinkedIn') 