

from .common import *

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ["*"]
# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
