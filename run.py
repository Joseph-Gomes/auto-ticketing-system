import os
import sys
import json

# Ensure /src is importable
BASE_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(BASE_DIR, "src")
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")  # not inside src!
os.makedirs(CREDENTIALS_DIR, exist_ok=True)
sys.path.insert(0, SRC_DIR)

from app import create_app


def recreate_file_from_env(env_var_name: str, file_path: str):
    """Create a file from an environment variable containing JSON."""
    data = os.getenv(env_var_name)
    if data and not os.path.exists(file_path):
        try:
            parsed = json.loads(data)
            with open(file_path, "w") as f:
                json.dump(parsed, f)
            print(f"✅ {os.path.basename(file_path)} created from {env_var_name}.")
        except Exception as e:
            print(f"⚠️ Failed to create {file_path}: {e}")


# ✅ Google service account should be in /credentials/, not /src/
recreate_file_from_env(
    "GOOGLE_SERVICE_JSON",
    os.path.join(CREDENTIALS_DIR, "google_service_account.json")
)

# ✅ Gmail token.json for auto-reply
recreate_file_from_env(
    "GMAIL_TOKEN_JSON",
    os.path.join(BASE_DIR, "token.json")
)

# 🚀 Create Flask app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
