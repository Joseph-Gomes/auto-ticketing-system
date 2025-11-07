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
    if data:
        try:
            # If directory doesn’t exist (e.g. src/), create it
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w") as f:
                json.dump(json.loads(data), f)
            print(f"✅ {os.path.basename(file_path)} created from {env_var_name}.")
        except Exception as e:
            print(f"⚠️ Failed to create {os.path.basename(file_path)}: {e}")


# -------------------------------------------------------------------
# 🧠 Rebuild credentials automatically for Render (safe for local too)
# -------------------------------------------------------------------
base_dir = os.path.dirname(__file__)
src_dir = os.path.join(base_dir, "src")

# Google Service Account (for Google Sheets)
recreate_file_from_env("GOOGLE_SERVICE_JSON", os.path.join(src_dir, "google_service_account.json"))

# Gmail OAuth Token (optional: for sending confirmation emails)
recreate_file_from_env("GMAIL_TOKEN_JSON", os.path.join(src_dir, "token.json"))


# -------------------------------------------------------------------
# 🚀 Create Flask app
# -------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
