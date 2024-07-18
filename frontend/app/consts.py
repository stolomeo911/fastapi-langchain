import uuid
import os

URL = os.environ.get('URL', 'http://localhost:9000')

PERSIST_DIR = os.environ.get('PERSIST_DIR', 'frontend/app/persist_directory/')

SESSION_ID = str(uuid.uuid4())
