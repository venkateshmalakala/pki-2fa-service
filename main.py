import os
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from crypto_utils import decrypt_seed, generate_totp_code, verify_totp_code

app = FastAPI()

# CONFIGURATION
# If running in Docker (we set this ENV later), use /data/seed.txt
# If running locally, just use seed.txt in the current folder
SEED_FILE_PATH = os.getenv("SEED_PATH", "seed.txt")

# --- Request Models (Data Validation) ---
class EncryptedSeedRequest(BaseModel):
    encrypted_seed: str

class VerifyCodeRequest(BaseModel):
    code: str

# --- Helper Function ---
def get_stored_seed():
    """Reads the decrypted hex seed from the file."""
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet. Please call /decrypt-seed first.")
    
    with open(SEED_FILE_PATH, "r") as f:
        return f.read().strip()

# --- API Endpoints ---

@app.post("/decrypt-seed")
def api_decrypt_seed(payload: EncryptedSeedRequest):
    """
    Accepts base64 encrypted seed, decrypts it, and saves it to storage.
    """
    try:
        # 1. Decrypt the seed using our utility
        # We assume student_private.pem is in the root folder
        hex_seed = decrypt_seed(payload.encrypted_seed, "student_private.pem")
        
        # 2. Ensure the directory exists (for Docker later)
        directory = os.path.dirname(SEED_FILE_PATH)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # 3. Write to persistent storage
        with open(SEED_FILE_PATH, "w") as f:
            f.write(hex_seed)
            
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error decrypting: {e}")
        return Response(content='{"error": "Decryption failed"}', media_type="application/json", status_code=500)

@app.get("/generate-2fa")
def api_generate_2fa():
    """
    Generates the current TOTP code using the stored seed.
    """
    try:
        hex_seed = get_stored_seed()
        result = generate_totp_code(hex_seed)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-2fa")
def api_verify_2fa(payload: VerifyCodeRequest):
    """
    Verifies a provided code against the stored seed.
    """
    if not payload.code:
        raise HTTPException(status_code=400, detail="Missing code")
        
    hex_seed = get_stored_seed()
    
    is_valid = verify_totp_code(hex_seed, payload.code)
    return {"valid": is_valid}

# Optional: Health check
@app.get("/health")
def health_check():
    return {"status": "active"}