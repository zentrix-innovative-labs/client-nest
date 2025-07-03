import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')

# For OAuth2 callback
YOUTUBE_REDIRECT_URI = os.getenv('YOUTUBE_REDIRECT_URI', 'http://localhost:8000/api/social/youtube/callback/')

print("[DEBUG] YOUTUBE_API_KEY loaded:", "Yes" if os.getenv('YOUTUBE_API_KEY') else "No") 