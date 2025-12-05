import sys
import subprocess
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def generate_proof():
    print("--- Generating Submission Proof ---")

    # 1. Get latest Git Commit Hash
    try:
        # Run git command to get the hash
        commit_hash = subprocess.check_output(['git', 'log', '-1', '--format=%H']).decode('utf-8').strip()
        print(f"✅ Commit Hash: {commit_hash}")
    except Exception as e:
        print("❌ Error: Could not get git hash. Are you in a git repo?")
        print(e)
        return

    # 2. Load Student Private Key
    try:
        with open("student_private.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        print("❌ Error: student_private.pem not found.")
        return

    # 3. Sign the Hash (RSA-PSS)
    signature = private_key.sign(
        commit_hash.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # 4. Load Instructor Public Key
    try:
        with open("instructor_public.pem", "rb") as f:
            inst_public_key = serialization.load_pem_public_key(f.read())
    except FileNotFoundError:
        print("❌ Error: instructor_public.pem not found.")
        return

    # 5. Encrypt the Signature (RSA-OAEP)
    encrypted_signature = inst_public_key.encrypt(
        signature,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 6. Encode to Base64
    final_proof = base64.b64encode(encrypted_signature).decode('utf-8')
    
    print("\n⬇️ COPY THIS FOR SUBMISSION ⬇️")
    print(final_proof)
    print("⬆️ ------------------------- ⬆️")

if __name__ == "__main__":
    generate_proof()