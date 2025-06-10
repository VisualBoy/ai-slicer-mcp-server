import os
import subprocess
import requests
import json
from src import config

# --- Helper Functions ---
def _get_octoprint_headers():
    return {"X-Api-Key": config.OCTOPRINT_API_KEY}

def _get_full_model_path(model_name):
    return os.path.join(config.MODELS_FOLDER_PATH, model_name)

def _get_full_gcode_path(gcode_filename):
    return os.path.join(config.GCODE_FOLDER_PATH, gcode_filename)

# --- Original Repository Tools ---

def list_models() -> list[str]:
    """Lists all available 3D model files (.stl, .obj, .3mf)."""
    allowed_extensions = ['.stl', '.obj', '.3mf']
    files = [f for f in os.listdir(config.MODELS_FOLDER_PATH) if any(f.lower().endswith(ext) for ext in allowed_extensions)]
    return files

def list_gcode_files() -> list[str]:
    """Lists all generated .gcode files."""
    files = [f for f in os.listdir(config.GCODE_FOLDER_PATH) if f.lower().endswith('.gcode')]
    return files

def get_slicer_profiles() -> list[str]:
    """Retrieves the list of available slicer profiles from OctoPrint."""
    url = f"{config.OCTOPRINT_URL}/api/slicing/prusa/profiles"
    response = requests.get(url, headers=_get_octoprint_headers())
    response.raise_for_status()
    return list(response.json().keys())

def run_slicer(model_name: str, profile_name: str, output_filename: str = None) -> str:
    """Slices a 3D model using PrusaSlicer CLI with a specified profile."""
    model_path = _get_full_model_path(model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_name}")

    if not output_filename:
        output_filename = f"{os.path.splitext(model_name)[0]}.gcode"

    output_path = _get_full_gcode_path(output_filename)

    command = [
        config.PRUSA_SLICER_PATH,
        "--export-gcode",
        f"--load={profile_name}.ini", # Note: PrusaSlicer might need full path to profiles
        f"--output={output_path}",
        model_path
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return f"Slicing successful. Output saved to {output_path}. PrusaSlicer output:
{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Slicing failed. Error:
{e.stderr}"

def upload_file_to_octoprint(filepath: str, select: bool = False, print_after_upload: bool = False) -> dict:
    """Uploads a file (model or gcode) to OctoPrint."""
    if not os.path.isabs(filepath):
         raise ValueError("Please provide an absolute path to the file.")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File to upload not found: {filepath}")

    filename = os.path.basename(filepath)
    url = f"{config.OCTOPRINT_URL}/api/files/local"
    files = {'file': (filename, open(filepath, 'rb'), 'application/octet-stream')}
    payload = {'select': select, 'print': print_after_upload}

    response = requests.post(url, files=files, data=payload, headers=_get_octoprint_headers())
    response.raise_for_status()
    return response.json()

def print_gcode_file(gcode_filename: str) -> dict:
    """Selects a G-code file on OctoPrint and starts printing it."""
    url = f"{config.OCTOPRINT_URL}/api/files/local/{gcode_filename}"
    payload = {"command": "select", "print": True}
    response = requests.post(url, json=payload, headers=_get_octoprint_headers())
    response.raise_for_status()
    return {"status": f"Print command sent for {gcode_filename}. Status code: {response.status_code}"}

# --- New AI-Powered Placeholder Tools ---

def analyze_model_printability(model_name: str) -> dict:
    """(Placeholder) Analyzes a 3D model for printability issues."""
    model_path = _get_full_model_path(model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_name}")
    # In a real implementation, this would use a library like PyMeshLab or a custom algorithm
    return {
        "model_name": model_name,
        "status": "Analysis not yet implemented.",
        "details": "This is a placeholder for a future feature that will check for overhangs, thin walls, etc."
    }

def optimize_model_orientation(model_name: str, goal: str = "minimi_supporti") -> dict:
    """(Placeholder) Suggests the optimal orientation for printing."""
    # Goal can be 'minimi_supporti', 'massima_robustezza', 'migliore_finitura'
    return {
        "model_name": model_name,
        "goal": goal,
        "status": "Optimization not yet implemented.",
        "suggested_orientation_xyz_rot": [0, 0, 0],
        "reason": "This is a placeholder. A real implementation would use geometric analysis."
    }

def select_slicing_profile(model_name: str, print_goal: str = "prototipo_veloce") -> str:
    """(Placeholder) Suggests the best slicing profile based on the print goal."""
    # print_goal can be 'prototipo_veloce', 'massimo_dettaglio', 'pezzo_funzionale'
    profiles = get_slicer_profiles()
    if not profiles:
        return "No profiles found on OctoPrint."
    # Basic logic: suggest the first available profile. A real implementation would be smarter.
    return f"Suggested profile for '{print_goal}': {profiles[0]}. (This is a basic suggestion)."

def diagnose_print_issue(issue_description: str) -> str:
    """(Placeholder) Provides suggestions for common 3D printing issues."""
    issue = issue_description.lower()
    if "warping" in issue or "angoli sollevati" in issue:
        return "For warping, try: 1. Using a brim or raft. 2. Cleaning the print bed. 3. Increasing bed temperature slightly. 4. Checking for drafts."
    if "stringing" in issue or "fili" in issue:
        return "For stringing, try: 1. Increasing retraction distance. 2. Increasing retraction speed. 3. Lowering print temperature. 4. Enabling 'Wipe' or 'Coasting' settings."
    return "Diagnosis not yet implemented for this issue. Please describe common problems like 'warping' or 'stringing'."

# --- Toolset Definition ---
TOOL_DEFINITIONS = {
    # Original
    "list_models": list_models,
    "list_gcode_files": list_gcode_files,
    "get_slicer_profiles": get_slicer_profiles,
    "run_slicer": run_slicer,
    "upload_file_to_octoprint": upload_file_to_octoprint,
    "print_gcode_file": print_gcode_file,
    # New
    "analyze_model_printability": analyze_model_printability,
    "optimize_model_orientation": optimize_model_orientation,
    "select_slicing_profile": select_slicing_profile,
    "diagnose_print_issue": diagnose_print_issue,
}
