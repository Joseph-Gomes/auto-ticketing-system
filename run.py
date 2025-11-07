import os
import sys
import json

# Ensure src folder is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import create_app


# -------------------------------------------------------------------
# 🔒 Utility: Recreate JSON files from environment variables
# -------------------------------------------------------------------
def recreate_file_from_env(env_var_name, file_path):
    """Create a file from an environment variable containing JSON if it exists."""
    data = os.getenv(env_var_name)
    if data and not os.path.exists(file_path):
        try:
            with open(file_path, "w") as f:
                json.dump(json.loads(data), f)
            print(f"✅ {file_path} created from {env_var_name}.")
        except Exception as e:
            print(f"⚠️ Failed to create {file_path}: {e}")


# -------------------------------------------------------------------
# 🧠 Rebuild credentials automatically for Render (safe for local too)
# -------------------------------------------------------------------
base_dir = os.path.dirname(__file__)

# Google Service Account
recreate_file_from_env("GOOGLE_SERVICE_JSON", os.path.join(base_dir, "service_account.json"))

# Gmail OAuth Token (used for sending confirmation emails)
recreate_file_from_env("GMAIL_TOKEN_JSON", os.path.join(base_dir, "token.json"))


# -------------------------------------------------------------------
# 🚀 Create Flask app
# -------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
