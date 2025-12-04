from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair
    """
    print(f"Generating {key_size}-bit RSA key pair... this may take a moment.")
    
    # 1. Generate Private Key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # 2. Generate Public Key
    public_key = private_key.public_key()

    # 3. Serialize Private Key to PEM format
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 4. Serialize Public Key to PEM format
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # 5. Save to files
    with open("student_private.pem", "wb") as f:
        f.write(pem_private)
    
    with open("student_public.pem", "wb") as f:
        f.write(pem_public)

    print("✅ Keys generated successfully!")
    print("- student_private.pem")
    print("- student_public.pem")

if __name__ == "__main__":
    generate_rsa_keypair()