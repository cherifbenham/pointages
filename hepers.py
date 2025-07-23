import os
from dotenv import load_dotenv

def load_env(env_path: str = ".env"):
    """
    Loads environment variables from the specified .env file.
    Usage:
        load_env()  # loads from .env in current directory
        load_env("/path/to/.env")  # loads from a specific path
    """
    load_dotenv(env_path)
    # Optionally, return all loaded environment variables as a dict
    return {key: os.getenv(key) for key in os.environ}

