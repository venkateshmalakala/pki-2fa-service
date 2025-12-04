#!/usr/bin/env python3
import sys
import os
import datetime

# Add the parent directory to the path so we can import crypto_utils
# This allows the script to see the file in the folder above it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto_utils import generate_totp_code

# CONFIGURATION
# In Docker, this will be /data/seed.txt
# Locally, we fallback to seed.txt in parent folder
SEED_FILE_PATH = os.getenv("SEED_PATH", os.path.join(os.path.dirname(__file__), '..', 'seed.txt'))

def job():
    # 1. Check if seed exists
    if not os.path.exists(SEED_FILE_PATH):
        # Print to stderr so it shows up in logs as an error
        print(f"CRON ERROR: Seed file not found at {SEED_FILE_PATH}", file=sys.stderr)
        return

    # 2. Read Seed
    with open(SEED_FILE_PATH, "r") as f:
        hex_seed = f.read().strip()

    # 3. Generate Code
    try:
        result = generate_totp_code(hex_seed)
        code = result["code"]
        
        # 4. Get UTC Timestamp (CRITICAL requirement: UTC)
        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        # 5. Print to stdout (Docker cron will redirect this to file)
        print(f"{now_utc} - 2FA Code: {code}")
        
    except Exception as e:
        print(f"CRON ERROR: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    job()