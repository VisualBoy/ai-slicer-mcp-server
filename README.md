# OctoPrint/PrusaSlicer MCP Server

This project is a Model Context Protocol (MCP) compliant server that exposes 3D model slicing functionalities (via PrusaSlicer CLI) and 3D printer management capabilities (via the OctoPrint API). It allows AI agents and other MCP clients to interact with your 3D printing workflow programmatically.

## Features (MCP Tools)

The server provides the following tools, which can be invoked by an MCP client:

*   **`list_models`**: Lists all available 3D model files (.stl, .obj, .3mf) in the models folder.
*   **`list_gcode_files`**: Lists all generated .gcode files in the G-code folder.
*   **`get_slicer_profiles`**: Retrieves and lists available slicer profile names from OctoPrint.
*   **`run_slicer`**: Slices a 3D model using a specified profile via PrusaSlicer CLI, saving the output G-code.
*   **`upload_file_to_octoprint`**: Uploads a specified model or G-code file to OctoPrint, optionally selecting it and starting print.
*   **`print_gcode_file`**: Selects a G-code file already on OctoPrint and initiates the printing process.
*   **`analyze_model_printability`**: (Placeholder) Analyzes a 3D model for potential printability issues like overhangs or thin walls.
*   **`optimize_model_orientation`**: (Placeholder) Suggests an optimal orientation for a 3D model based on a specified goal (e.g., minimize supports).
*   **`select_slicing_profile`**: (Placeholder) Suggests the best slicing profile for a given model and printing goal.
*   **`diagnose_print_issue`**: (Placeholder) Provides troubleshooting suggestions for common 3D printing issues based on description.

## Prerequisites

1.  **Python 3.9+** installed.
2.  **`uv`**: An extremely fast Python package installer and virtual environment manager. If you don't have it, install it via pip:
    ```bash
    pip install uv
    ```
3.  **PrusaSlicer**: You must have PrusaSlicer installed on your system. The path to its executable will be needed in the configuration.
4.  **OctoPrint**: An instance of OctoPrint running and accessible on your network. You'll need its URL and an API key.

## Setup and Configuration

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/VisualBoy/AI-Slicer.git
    cd AI-Slicer
    ```

2.  **Create and Activate Virtual Environment:**
    Use `uv` to create an isolated virtual environment.
    ```bash
    uv venv
    ```
    This creates a `.venv` folder and `uv` will automatically use this environment for subsequent commands. If you need to activate it manually for your shell:
    ```bash
    source .venv/bin/activate  # On macOS/Linux
    .venv\Scripts\activate    # On Windows
    ```

3.  **Install Dependencies:**
    The project dependencies (like `python-dotenv` for managing environment variables and `requests` for API communication) are defined in `pyproject.toml`. Install them using `uv`:
    ```bash
    uv pip install -e .
    ```
    (The `-e` flag installs the project in editable mode.)

4.  **Configure Environment Variables:**
    Copy the example environment file `.env.example` to a new file named `.env`.
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file with a text editor and provide the correct values for your setup:
    *   `PRUSA_SLICER_PATH`: The full path to your PrusaSlicer console executable (e.g., `/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer --console` on macOS or `C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe` on Windows).
    *   `MODELS_FOLDER_PATH`: The full path to the folder where your 3D model files (e.g., `.stl`, `.obj`) are stored.
    *   `GCODE_FOLDER_PATH`: The full path to the folder where generated `.gcode` files should be saved.
    *   `OCTOPRINT_URL`: The base URL of your OctoPrint instance (e.g., `http://octopi.local` or `http://192.168.1.100`).
    *   `OCTOPRINT_API_KEY`: Your OctoPrint API key, which can be found in OctoPrint's settings.

## Running the Server

To start the MCP server, run the following command from the project's root directory:
```bash
uv run python src/main.py
```
The server will start and listen for JSON-RPC 2.0 messages on its standard input (stdin) and send responses to standard output (stdout).

## MCP Compliance

This server is designed to be compatible with the Model Context Protocol (MCP). MCP is a specification that allows AI models and other software clients to interact with various tools and servers (like this one) in a standardized way. This enables seamless integration of this server's 3D printing capabilities into larger AI-driven workflows.

MCP clients can discover and interface with this server using a `mcp.json` file. Here's the `mcp.json` configuration for this server:

```json
{
  "$schema": "https://modelcontextprotocol.io/schemas/mcp-server.schema.json",
  "name": "OctoPrint-MCP-Bridge",
  "description": "MCP server providing tools to interact with OctoPrint and PrusaSlicer for 3D printing workflows.",
  "homepage": "https://github.com/VisualBoy/AI-Slicer",
  "server": {
    "run": [
      "python",
      "src/main.py"
    ],
    "protocols": ["json-rpc-2.0"]
  }
}
```

(Note: While `uv run python src/main.py` is recommended for local execution to ensure the correct environment, the `mcp.json` specifies `python src/main.py` for broader compatibility with MCP clients that might not be `uv`-aware and assume a standard Python execution.)

## How to Use with an MCP Client

An MCP client would typically be configured to use this server via a "stdio" (standard input/output) transport mechanism. The client will use the `server.run` command specified in `mcp.json` (or a path to the `mcp.json` file itself) to start and communicate with this server.

Refer to the documentation of your specific MCP client for details on how to connect to an MCP server using stdio. The client will then be able to call the methods listed in the "Features" section (e.g., `mcp/getTools`, `mcp/runTool`, `mcp/setRoots`).
