import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Load Configuration ---
PRUSA_SLICER_PATH = os.getenv("PRUSA_SLICER_PATH")
MODELS_FOLDER_PATH = os.getenv("MODELS_FOLDER_PATH")
GCODE_FOLDER_PATH = os.getenv("GCODE_FOLDER_PATH")
OCTOPRINT_URL = os.getenv("OCTOPRINT_URL")
OCTOPRINT_API_KEY = os.getenv("OCTOPRINT_API_KEY")

# --- Validate Configuration ---
def validate_config():
    """Checks if all required environment variables are set."""
    required_vars = {
        "PRUSA_SLICER_PATH": PRUSA_SLICER_PATH,
        "MODELS_FOLDER_PATH": MODELS_FOLDER_PATH,
        "GCODE_FOLDER_PATH": GCODE_FOLDER_PATH,
        "OCTOPRINT_URL": OCTOPRINT_URL,
        "OCTOPRINT_API_KEY": OCTOPRINT_API_KEY,
    }

    missing_vars = [key for key, value in required_vars.items() if not value]

    if missing_vars:
        raise ValueError(f"Configuration error: Missing required environment variables: {', '.join(missing_vars)}. Please check your .env file.")

    if not os.path.exists(PRUSA_SLICER_PATH):
        raise FileNotFoundError(f"PrusaSlicer executable not found at path: {PRUSA_SLICER_PATH}")
    if not os.path.isdir(MODELS_FOLDER_PATH):
        raise NotADirectoryError(f"Models folder not found at path: {MODELS_FOLDER_PATH}")
    if not os.path.isdir(GCODE_FOLDER_PATH):
        raise NotADirectoryError(f"G-code folder not found at path: {GCODE_FOLDER_PATH}")

# Run validation on import
validate_config()
