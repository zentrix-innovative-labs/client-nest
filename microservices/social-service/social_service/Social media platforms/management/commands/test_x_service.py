from django.core.management.base import BaseCommand
from django.conf import settings
import os
from ...x_service import XService
from ...x_config import X_CONFIG, X_ENDPOINTS

class Command(BaseCommand):
    help = 'Test X (Twitter) service functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--access-token',
            type=str,
            help='X access token for testing'
        )
        parser.add_argument(
            '--access-token-secret',
            type=str,
            help='X access token secret for testing'
        )
        parser.add_argument(
            '--post-content',
            type=str,
            default='Test tweet from X Service! 🚀 #testing',
            help='Content to post for testing'
        )
        parser.add_argument(
            '--skip-posting',
            action='store_true',
            help='Skip content posting test'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Testing X Service...'))
        
        # Check configuration
        self.stdout.write('1. Checking configuration...')
        if not X_CONFIG['API_KEY']:
            self.stdout.write(self.style.ERROR('❌ X_API_KEY not found'))
            return
        if not X_CONFIG['API_SECRET']:
            self.stdout.write(self.style.ERROR('❌ X_API_SECRET not found'))
            return
        self.stdout.write(self.style.SUCCESS('✅ Configuration OK'))
        
        # Get credentials
        access_token = options['access_token'] or os.getenv('X_TEST_ACCESS_TOKEN')
        access_token_secret = options['access_token_secret'] or os.getenv('X_TEST_ACCESS_TOKEN_SECRET')
        
        if not access_token or not access_token_secret:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Test credentials not found. '
                    'Set X_TEST_ACCESS_TOKEN and X_TEST_ACCESS_TOKEN_SECRET '
                    'or use --access-token and --access-token-secret arguments'
                )
            )
            return
        
        # Test service initialization
        self.stdout.write('2. Testing service initialization...')
        try:
            x_service = XService(access_token, access_token_secret)
            self.stdout.write(self.style.SUCCESS('✅ Service initialized'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Service initialization failed: {e}'))
            return
        
        # Test account info
        self.stdout.write('3. Testing account info...')
        try:
            account_info = x_service.get_account_info()
            self.stdout.write(self.style.SUCCESS('✅ Account info retrieved'))
            user_data = account_info.get('data', {})
            self.stdout.write(
                f'   User: @{user_data.get("username", "N/A")} '
                f'({user_data.get("name", "N/A")})'
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Account info failed: {e}'))
            return
        
        # Test timeline retrieval
        self.stdout.write('4. Testing timeline retrieval...')
        try:
            timeline = x_service.get_timeline(max_results=3)
            tweets = timeline.get('data', [])
            self.stdout.write(self.style.SUCCESS(f'✅ Timeline retrieved ({len(tweets)} tweets)'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Timeline retrieval failed: {e}'))
        
        # Test content posting
        if not options['skip_posting']:
            self.stdout.write('5. Testing content posting...')
            test_content = options['post_content']
            try:
                result = x_service.post_content(test_content)
                if result.get('status') == 'error':
                    self.stdout.write(
                        self.style.ERROR(f'❌ Posting failed: {result.get("message")}')
                    )
                else:
                    self.stdout.write(self.style.SUCCESS('✅ Content posted successfully'))
                    self.stdout.write(f'   Tweet ID: {result.get("id")}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Posting failed: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ X Service test completed!')) 