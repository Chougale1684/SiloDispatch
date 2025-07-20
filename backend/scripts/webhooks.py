# ~/silo_fortune/config/webhooks.py
import os
import hmac
import hashlib

class WebhookVerifier:
    def __init__(self):
        self.secret = (os.getenv("silofortune") or "default_secret").encode()
    
    def verify(self, payload: bytes, signature: str) -> bool:
        expected = hmac.new(
            self.secret,
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

webhook_verifier = WebhookVerifier()