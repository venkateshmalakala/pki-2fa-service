import requests
import json
import sys

# ================= CONFIGURATION =================
# TODO: Replace these two variables with your actual details!
STUDENT_ID = "23P31A05M5" 
GITHUB_REPO_URL = "https://github.com/venkateshmalakala/pki-2fa-service" 
# =================================================

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def get_encrypted_seed():
    print(f"--- Requesting Seed for {STUDENT_ID} ---")

    # 1. Read your Public Key
    try:
        with open("student_public.pem", "r") as f:
            public_key_content = f.read()
    except FileNotFoundError:
        print("❌ Error: student_public.pem not found. Did you run Phase 1?")
        sys.exit(1)

    # 2. Prepare the data payload
    # Note: The API handles the newlines in the key automatically if we send it as a JSON string
    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": GITHUB_REPO_URL,
        "public_key": public_key_content
    }

    # 3. Send POST request
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if "encrypted_seed" in data:
                enc_seed = data["encrypted_seed"]
                
                # 4. Save to file
                with open("encrypted_seed.txt", "w") as f:
                    f.write(enc_seed)
                
                print("✅ Success! Encrypted seed saved to 'encrypted_seed.txt'")
                print(f"Received (first 20 chars): {enc_seed[:20]}...")
            else:
                print("❌ Error: Response did not contain 'encrypted_seed'")
                print("Response:", data)
        else:
            print(f"❌ API Error (Status {response.status_code}):")
            print(response.text)

    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")

if __name__ == "__main__":
    get_encrypted_seed()