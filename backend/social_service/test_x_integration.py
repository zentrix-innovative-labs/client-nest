import os
import sys
import django
from dotenv import load_dotenv

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from social_service.x_service import XService
from social_service.models import SocialAccount

def test_x_integration():
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
    
    # Check if we have the required credentials
    if not all([os.getenv('X_API_KEY'), os.getenv('X_API_SECRET'), os.getenv('X_BEARER_TOKEN')]):
        print("Error: Missing required X (Twitter) API credentials in .env file.")
        print("Please make sure you have set X_API_KEY, X_API_SECRET, and X_BEARER_TOKEN.")
        return
    
    # Get access tokens from the database (you'll need to have gone through OAuth flow first)
    try:
        social_account = SocialAccount.objects.filter(platform='x').first()
        if not social_account:
            print("No X account found in the database. Please authenticate first.")
            return
            
        access_token = social_account.access_token
        access_token_secret = social_account.access_token_secret
        
        # Initialize the X service
        x_service = XService(access_token=access_token, access_token_secret=access_token_secret)
        
        # Test 1: Post a test tweet
        print("\n=== Testing Post Creation ===")
        test_post = x_service.post_content("This is a test tweet from ClientNest integration! 🚀")
        
        if test_post.get('status') == 'error':
            print(f"❌ Error posting tweet: {test_post.get('message')}")
        else:
            print(f"✅ Successfully posted tweet!")
            print(f"Tweet ID: {test_post.get('id')}")
            print(f"Text: {test_post.get('text')}")
            
            # Test 2: Reply to the test tweet
            print("\n=== Testing Comment/Reply ===")
            reply = x_service.post_comment(
                tweet_id=test_post.get('id'),
                text="This is a test reply from ClientNest! 👋"
            )
            
            if reply.get('status') == 'error':
                print(f"❌ Error posting reply: {reply.get('message')}")
            else:
                print(f"✅ Successfully posted reply!")
                print(f"Reply ID: {reply.get('id')}")
                print(f"In reply to tweet ID: {reply.get('in_reply_to_tweet_id')}")
                print(f"Text: {reply.get('text')}")
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_x_integration()
