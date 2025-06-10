import subprocess
import json
import threading
import time
import os

# --- Server Process Management ---
SERVER_COMMAND = ["python", "src/main.py"]
server_proc = None
stderr_lines = []

def read_stderr(pipe):
    """Reads stderr from the server process non-blockingly."""
    try:
        for line in iter(pipe.readline, b''):
            line_str = line.decode('utf-8').strip()
            stderr_lines.append(line_str)
            # To see stderr in real-time during tests, uncomment next line
            # print(f"SERVER_STDERR: {line_str}", flush=True)
    except Exception as e:
        # This might happen if pipe is closed
        stderr_lines.append(f"Error reading stderr: {e}")
    finally:
        if hasattr(pipe, 'close'):
            pipe.close()

def start_server():
    """Starts the MCP server as a subprocess."""
    global server_proc, stderr_lines
    stderr_lines = []
    try:
        # Ensure .env exists by copying from .env.example if needed,
        # as config.py validation runs on server import.
        if not os.path.exists(".env") and os.path.exists(".env.example"):
            print("INFO: .env file not found. Copying from .env.example for tests.")
            with open(".env.example", "r") as f_example, open(".env", "w") as f_env:
                f_env.write(f_example.read())
            print("INFO: Example .env content (ensure placeholders are valid for server startup):")
            with open(".env", "r") as f_env_check:
                print(f_env_check.read())

        print(f"Starting server with command: {' '.join(SERVER_COMMAND)}")
        # Pass current environment variables, which should include those from .env if loaded by a test runner
        # or if the shell has them. For direct python execution, .env is usually loaded by the app itself.
        # The server (src/config.py) loads .env.
        current_env = os.environ.copy()

        server_proc = subprocess.Popen(
            SERVER_COMMAND,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=current_env, # Ensure server can see environment variables
            cwd=os.getcwd() # Run from project root
        )
        # Start a thread to read stderr non-blockingly
        stderr_thread = threading.Thread(target=read_stderr, args=(server_proc.stderr,))
        stderr_thread.daemon = True
        stderr_thread.start()

        # Give the server a moment to start up and print any initial errors
        time.sleep(0.5) # Adjust if server needs more time
        if server_proc.poll() is not None: # Check if server terminated prematurely
             raise RuntimeError(f"Server terminated unexpectedly. Exit code: {server_proc.returncode}. Stderr: {get_stderr()}")
        print("Server started successfully.")
        return server_proc
    except Exception as e:
        print(f"Failed to start server: {e}")
        if server_proc:
            print(f"Server stderr before failure: {get_stderr()}")
        raise

def stop_server():
    """Stops the MCP server process."""
    global server_proc
    if server_proc:
        try:
            if server_proc.stdin:
                server_proc.stdin.close()
            if server_proc.poll() is None: # If still running
                server_proc.terminate()
                server_proc.wait(timeout=5) # Wait for termination
        except Exception as e:
            print(f"Error during server termination: {e}")
            if server_proc.poll() is None:
                server_proc.kill() # Force kill if terminate fails
        finally:
            server_proc = None
            print("Server stopped.")

def get_stderr():
    """Returns all stderr lines captured so far."""
    return "\n".join(stderr_lines)

# --- Request/Response Handling ---
request_id_counter = 1

def send_mcp_request(proc, method, params=None, is_notification=False, raw_payload=None):
    """Sends a JSON-RPC request to the server and returns the response."""
    global request_id_counter
    if raw_payload:
        payload_str = raw_payload
    else:
        payload = {"jsonrpc": "2.0", "method": method}
        if params:
            payload["params"] = params
        if not is_notification:
            payload["id"] = request_id_counter
            request_id_counter += 1
        payload_str = json.dumps(payload) + "\n"

    try:
        # print(f"SENDING: {payload_str.strip()}") # Debug: show what's being sent
        proc.stdin.write(payload_str.encode('utf-8'))
        proc.stdin.flush()

        if is_notification and not raw_payload: # No response for notifications
            return None

        # Read response
        response_line = proc.stdout.readline()
        if not response_line:
            # This can happen if server closes stdout or crashes
            # Check stderr for clues
            time.sleep(0.1) # Give stderr thread a moment
            server_err_output = get_stderr()
            raise ConnectionError(f"No response from server. It might have crashed or closed stdout. Server stderr:\n{server_err_output}")

        # print(f"RECEIVED: {response_line.decode('utf-8').strip()}") # Debug: show what's received
        return json.loads(response_line.decode('utf-8'))
    except BrokenPipeError:
        server_err_output = get_stderr()
        raise ConnectionError(f"Broken pipe. Server likely crashed. Server stderr:\n{server_err_output}")
    except Exception as e:
        server_err_output = get_stderr()
        raise Exception(f"Error during communication: {e}. Server stderr:\n{server_err_output}")


# --- Test Cases ---
def test_get_tools(proc):
    print("Running test_get_tools...", end=" ")
    response = send_mcp_request(proc, "mcp/getTools")
    assert response is not None, "Response should not be None"
    assert "result" in response, "Response should contain 'result'"
    assert isinstance(response["result"], list), "Result should be a list"
    tool_names = [tool["name"] for tool in response["result"]]
    assert "list_models" in tool_names, "Should find 'list_models' tool"
    assert "diagnose_print_issue" in tool_names, "Should find 'diagnose_print_issue' tool"
    print("PASS")

def test_run_placeholder_tool(proc):
    print("Running test_run_placeholder_tool...", end=" ")
    params = {"name": "diagnose_print_issue", "arguments": {"issue_description": "my printer is making weird noises"}}
    response = send_mcp_request(proc, "mcp/runTool", params)
    assert response is not None, "Response should not be None"
    assert "result" in response, "Response should contain 'result'"
    assert isinstance(response["result"], str), "Result for diagnose_print_issue should be a string"
    print("PASS")

def test_set_roots(proc):
    print("Running test_set_roots...", end=" ")
    params = {"roots": [{"uri": "file:///tmp/projectA", "priority": 1}]}
    response = send_mcp_request(proc, "mcp/setRoots", params)
    assert response is not None, "Response should not be None"
    assert "result" in response, "Response should contain 'result'"
    assert response["result"].get("status") == "success", "setRoots should return success status"
    print("PASS")

def test_invalid_json(proc):
    print("Running test_invalid_json...", end=" ")
    # Send raw string that is not valid JSON
    response = send_mcp_request(proc, method=None, raw_payload='{"jsonrpc": "2.0", "method": "foo", "params": "bar", "id": 1') # Missing closing brace
    assert response is not None, "Response should not be None"
    assert "error" in response, "Response should contain 'error'"
    assert response["error"]["code"] == -32700, f"Error code should be -32700 (Parse error), got {response['error']['code']}"
    print("PASS")

def test_method_not_found(proc):
    print("Running test_method_not_found...", end=" ")
    response = send_mcp_request(proc, "mcp/nonExistentMethod")
    assert response is not None, "Response should not be None"
    assert "error" in response, "Response should contain 'error'"
    assert response["error"]["code"] == -32601, f"Error code should be -32601 (Method not found), got {response['error']['code']}"
    print("PASS")

def test_tool_not_found(proc):
    print("Running test_tool_not_found...", end=" ")
    params = {"name": "thisToolDoesNotExist", "arguments": {}}
    response = send_mcp_request(proc, "mcp/runTool", params)
    assert response is not None, "Response should not be None"
    assert "error" in response, "Response should contain 'error'"
    assert response["error"]["code"] == -32601, f"Error code should be -32601 (Tool not found), got {response['error']['code']}"
    print("PASS")

# --- Main Execution ---
if __name__ == "__main__":
    tests = [
        test_get_tools,
        test_run_placeholder_tool,
        test_set_roots,
        test_invalid_json,
        test_method_not_found,
        test_tool_not_found,
    ]
    passed_all = True

    try:
        print("Starting MCP server for testing...")
        proc = start_server()

        # It's possible the server printed something to stdout that's not a JSON response (e.g. debug prints).
        # Try to consume any such lines before running tests.
        # This is a bit hacky; ideally server only prints JSON-RPC to stdout.
        initial_stdout_read_attempts = 3
        for _ in range(initial_stdout_read_attempts):
            if proc.stdout.peek(1): # Check if there's data without blocking
                line = proc.stdout.readline().decode('utf-8').strip()
                if line and not line.startswith('{'): # If it's not JSON, print it as a warning
                    print(f"WARN: Initial non-JSON server stdout: {line}")
                elif line.startswith('{'): # If it IS json, this is unexpected. Push it back? Or fail?
                    print(f"WARN: Initial JSON server stdout (unexpected): {line}")
                    # This simple test script doesn't have a way to "unread" from stdout.
                    # For now, we'll hope it doesn't interfere.
                    break
            else:
                break

        print("\nRunning tests...")
        for test_func in tests:
            try:
                test_func(proc)
            except AssertionError as e:
                print(f"FAIL - {e}")
                passed_all = False
                print(f"Server stderr for {test_func.__name__}:\n{get_stderr()}")
                stderr_lines.clear() # Clear for next test
            except Exception as e:
                print(f"ERROR in {test_func.__name__} - {e}")
                passed_all = False
                print(f"Server stderr for {test_func.__name__}:\n{get_stderr()}")
                stderr_lines.clear() # Clear for next test


    except Exception as e:
        print(f"\n--- Test Suite CRITICAL ERROR --- : {e}")
        print(f"Last captured server stderr:\n{get_stderr()}")
        passed_all = False
    finally:
        print("\nStopping MCP server...")
        stop_server()
        # Print any final stderr messages
        final_stderr = get_stderr()
        if final_stderr:
            print(f"\nFinal server stderr dump:\n{final_stderr}")


    if passed_all:
        print("\nAll tests passed!")
        exit(0)
    else:
        print("\nSome tests failed.")
        exit(1)
