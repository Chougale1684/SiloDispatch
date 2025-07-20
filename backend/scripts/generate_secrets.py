# ~/silo_fortune/scripts/generate_secrets.py
import os
import secrets
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
webhook_secret = secrets.token_hex(32)

with open(env_path, 'a') as f:
    f.write(f"\nWEBHOOK_SECRET={webhook_secret}")

print(f"Generated new WEBHOOK_SECRET in .env file")