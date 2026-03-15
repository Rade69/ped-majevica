import os
import sys

# Ensure we're in the backend directory
# This is critical for debug mode reloader
if not os.getcwd().endswith('backend'):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Changed working directory to: {os.getcwd()}")

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Disable reloader to avoid path issues
    # In production, use gunicorn instead
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
