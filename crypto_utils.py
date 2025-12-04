import base64
import time
import pyotp
import hashlib  # <--- NEW IMPORT
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_seed(encrypted_seed_b64: str, private_key_path: str = "student_private.pem") -> str:
    """
    Step 5: Decrypt the base64 encrypted seed using the Private Key.
    Algorithm: RSA/OAEP with SHA-256 and MGF1
    """
    try:
        # 1. Load the Private Key
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )

        # 2. Decode the Base64 string into bytes
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)

        # 3. Decrypt using RSA-OAEP-SHA256
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 4. Convert bytes to string (UTF-8)
        decrypted_hex_seed = decrypted_bytes.decode('utf-8')

        # 5. Validation (Must be 64 chars hex)
        if len(decrypted_hex_seed) != 64:
            raise ValueError("Decrypted seed length is not 64 characters")
        
        # Check if valid hex
        int(decrypted_hex_seed, 16) 

        return decrypted_hex_seed

    except Exception as e:
        print(f"Decryption failed: {str(e)}")
        raise e

def get_totp_object(hex_seed: str):
    """
    Helper to create the TOTP object with correct settings.
    """
    # Convert HEX seed to Base32 (Required by TOTP standard)
    # 1. Hex -> Bytes
    seed_bytes = bytes.fromhex(hex_seed)
    # 2. Bytes -> Base32
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    
    # 3. Create TOTP object (SHA1, 6 digits, 30s interval)
    # FIX: Use hashlib.sha1 (Standard Lib) instead of hashes.SHA1 (Cryptography Lib)
    return pyotp.TOTP(base32_seed, digits=6, interval=30, digest=hashlib.sha1)

def generate_totp_code(hex_seed: str):
    """
    Step 6: Generate current 2FA code
    """
    totp = get_totp_object(hex_seed)
    
    # Calculate remaining seconds
    time_remaining = int(totp.interval - (time.time() % totp.interval))
    
    return {
        "code": totp.now(),
        "valid_for": time_remaining
    }

def verify_totp_code(hex_seed: str, code: str) -> bool:
    """
    Step 6b: Verify code with tolerance
    """
    totp = get_totp_object(hex_seed)
    # valid_window=1 means accept code from current 30s block OR previous/next 30s block
    return totp.verify(code, valid_window=1)