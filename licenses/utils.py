# utils.py
import uuid
import hashlib

def generate_license_key(username):
    # Generate an 8-character random component.
    random_part = uuid.uuid4().hex.upper()[:8]
    
    # Create a hidden message using the username.
    message = f"{username}"
    
    # Compute a SHA-256 hash of the message and take the first 8 characters.
    hash_part = hashlib.sha256(message.encode('utf-8')).hexdigest().upper()[:8]
    
    # Combine the two parts to form a 16-character license key.
    return random_part + hash_part
