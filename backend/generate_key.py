from cryptography.fernet import Fernet

# Generate a new key
key = Fernet.generate_key()
print("Generated key:", key.decode()) 