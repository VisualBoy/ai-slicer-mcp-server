# AI-Slicer-mcp-server

This project is an MCP server that exposes 3D slicing functionalities (via PrusaSlicer CLI) and printer management (via the OctoPrint API).

## Prerequisites

1.  **Python 3.9+** installed.
2.  **uv**: An extremely fast Python package and environment manager. Install it with:
    ```bash
    pip install uv
    ```
3.  **PrusaSlicer**: You must have PrusaSlicer installed on your system.
4.  **OctoPrint**: An instance of OctoPrint running and accessible on the network.

## Installation and Configuration Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <URL_OF_THIS_PROJECT>
    cd AI-Slicer-mcp-server
    ```

2.  **Create the Virtual Environment:**
    Use `uv` to create an isolated virtual environment.
    ```bash
    uv venv
    ```
    This command creates a `.venv` folder in the project root and automatically activates it for subsequent commands run with `uv`.

3.  **Install Dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```
    Or, using `pyproject.toml`:
    ```bash
    uv pip install -e .
    ```

4.  **Configure Environment Variables:**
    Copy the example file `.env.example` to a new file named `.env`.
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file with a text editor and enter the correct values for your system:
    *   `PRUSA_SLICER_PATH`: The full path to the PrusaSlicer console executable.
    *   `MODELS_FOLDER_PATH`: The full path to the folder where you keep your `.stl`/`.obj` files.
    *   `GCODE_FOLDER_PATH`: The full path to the folder where you want to save the generated `.gcode` files.
    *   `OCTOPRINT_URL`: The URL of your OctoPrint instance (e.g., `http://192.168.1.100`).
    *   `OCTOPRINT_API_KEY`: Your OctoPrint API key.

## Starting the Server

Your MCP client will automatically detect and start the server thanks to the `.mcp.json` file.

To test the server manually from the command line, run:
```bash
uv run python src/main.py
```
The server will wait for JSON-RPC input from `stdin`. You can send test commands to verify that everything is working correctly.

Once the MCP client is started, the AI will have access to all the tools defined in `src/tools.py` to interact with your 3D printers.
