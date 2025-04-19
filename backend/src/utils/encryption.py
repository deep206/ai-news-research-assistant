from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

class EncryptionManager:
    def __init__(self):
        # Get encryption key from environment or generate a new one
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            print("WARNING: New encryption key generated. Please add ENCRYPTION_KEY to your .env file")
        self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string"""
        if not data:
            return ""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt an encrypted string"""
        if not encrypted_data:
            return ""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

# Create a singleton instance
encryption_manager = EncryptionManager() 