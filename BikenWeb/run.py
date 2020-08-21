"""Application entry point."""
from biken import create_app
from dotenv import load_dotenv
import os
load_dotenv()


app = create_app()

if __name__ == "__main__":
    if os.environ.get("ENV", None) == "DEV":
        print("Start in dev mode")
        app.run(host='0.0.0.0',debug=True,ssl_context="adhoc")

    if os.environ.get("ENV", None) == "LIVE":
        print("Start in dev mode")
        app.run(host='0.0.0.0',debug=False)
