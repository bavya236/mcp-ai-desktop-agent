"""
Web Authentication Service (No Sorting Algorithms here)
"""
from datetime import datetime, timedelta
import hashlib

class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.users_db = {}
        
    def hash_password(self, password: str) -> str:
        return hashlib.sha256((password + self.secret_key).encode()).hexdigest()
        
    def register_user(self, username: str, password: str) -> bool:
        if username in self.users_db:
            return False
        self.users_db[username] = self.hash_password(password)
        return True
        
    def authenticate(self, username: str, password: str) -> bool:
        stored = self.users_db.get(username)
        return stored == self.hash_password(password)
