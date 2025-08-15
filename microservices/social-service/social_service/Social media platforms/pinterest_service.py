import requests
from requests_oauthlib import OAuth2Session

class PinterestService:
    AUTH_BASE_URL = 'https://www.pinterest.com/oauth/'
    TOKEN_URL = 'https://api.pinterest.com/v5/oauth/token'
    API_BASE_URL = 'https://api.pinterest.com/v5/'

    def __init__(self, client_id, client_secret, redirect_uri, token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.session = OAuth2Session(client_id, redirect_uri=redirect_uri, token=token)

    def get_authorization_url(self, scope=['pins:read', 'pins:write', 'boards:read']):
        return self.session.authorization_url(self.AUTH_BASE_URL, scope=scope)

    def fetch_token(self, authorization_response):
        return self.session.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response,
            client_secret=self.client_secret
        )

    def create_pin(self, board_id, image_url, title, description, link=None):
        url = self.API_BASE_URL + 'pins'
        data = {
            'board_id': board_id,
            'title': title,
            'description': description,
            'media_source': {
                'source_type': 'image_url',
                'url': image_url
            },
        }
        if link:
            data['link'] = link
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json() 