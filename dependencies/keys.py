import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def get_public_key_from_pem_file(pem_file_path: str):
    with open(pem_file_path, "rb") as pem_file:
        pem_data = pem_file.read()
        public_key = serialization.load_pem_public_key(
            pem_data, backend=default_backend()
        )
    return public_key


clerk_public_key = get_public_key_from_pem_file(os.getenv("CLERK_PUBLIC_KEY_PATH"))


def get_clerk_public_key():
    return clerk_public_key
