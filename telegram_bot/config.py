import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

BOT_TOKEN: str = os.environ['TELEGRAM_BOT_TOKEN']
API_BASE_URL: str = os.environ.get('API_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
API_SECRET: str = os.environ['BOT_API_SECRET']
NOTIFY_HOST: str = os.environ.get('NOTIFY_HOST', '127.0.0.1')
NOTIFY_PORT: int = int(os.environ.get('NOTIFY_PORT', '8001'))
OVERDUE_NOTIFY_HOUR: int = int(os.environ.get('OVERDUE_NOTIFY_HOUR', '10'))
