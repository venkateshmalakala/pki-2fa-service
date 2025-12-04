from crypto_utils import decrypt_seed, generate_totp_code

# Read the encrypted seed from the file you got in Phase 2
with open("encrypted_seed.txt", "r") as f:
    enc_seed = f.read().strip()

print("Attempting to decrypt...")
try:
    # Try to decrypt
    hex_seed = decrypt_seed(enc_seed)
    print(f"✅ Decrypted Seed: {hex_seed}")

    # Try to generate a code
    result = generate_totp_code(hex_seed)
    print(f"✅ Generated Code: {result['code']} (Valid for {result['valid_for']}s)")

except Exception as e:
    print(f"❌ FAILED: {e}")