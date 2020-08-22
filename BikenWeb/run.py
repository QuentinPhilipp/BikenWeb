"""Application entry point."""
from biken import create_app
from dotenv import load_dotenv
import os
load_dotenv()


app = create_app()

if __name__ == "__main__":
    app.run('0.0.0.0')
