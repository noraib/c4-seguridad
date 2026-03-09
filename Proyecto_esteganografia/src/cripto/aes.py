from cryptography.fernet import Fernet


def generate_key() -> bytes:
    return Fernet.generate_key()


def encrypt_message(message: str, key: bytes) -> bytes:
    f = Fernet(key)
    encrypted = f.encrypt(message.encode())
    return encrypted


def decrypt_message(ciphertext: bytes, key: bytes) -> str:
    f = Fernet(key)
    decrypted = f.decrypt(ciphertext)
    return decrypted.decode()