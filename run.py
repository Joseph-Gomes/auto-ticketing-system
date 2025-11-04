import os
import sys
import json

# Ensure src folder is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import create_app

# -------------------------------------------------------------------
# 🔒 Recreate Google service account file from Render environment
# -------------------------------------------------------------------
# On Render, store your service account JSON as an environment variable
# named GOOGLE_SERVICE_JSON. This will rebuild the actual JSON file
# before the app starts.
service_json_env = os.getenv("GOOGLE_SERVICE_JSON")
service_json_path = os.path.join(os.path.dirname(__file__), "service_account.json")

if service_json_env and not os.path.exists(service_json_path):
    try:
        with open(service_json_path, "w") as f:
            json.dump(json.loads(service_json_env), f)
        print("✅ Service account JSON created from environment variable.")
    except Exception as e:
        print("⚠️ Failed to write service account JSON:", e)

# -------------------------------------------------------------------
# Create Flask app
# -------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
