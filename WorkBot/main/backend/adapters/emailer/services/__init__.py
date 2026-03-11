from ..registry import EmailProviderRegistry
from ..services.gmail_service import GmailService
from ..services.outlook_service import OutlookService

EmailProviderRegistry.register('gmail', lambda: GmailService('token.json'))
EmailProviderRegistry.register('outlook', OutlookService)