import uuid

def generate_license_key():
    return str(uuid.uuid4()).replace('-', '').upper()[:16]  # Example: "A1B2C3D4E5F6G7H8"