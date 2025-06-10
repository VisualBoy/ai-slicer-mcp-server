import sys
import json
import traceback
from src.tools import TOOL_DEFINITIONS

def main():
    """Main loop to read from stdin, process requests, and write to stdout."""
    for line in sys.stdin:
        try:
            request = json.loads(line)
            jsonrpc_version = request.get("jsonrpc")
            request_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if jsonrpc_version != "2.0":
                send_error(request_id, -32600, "Invalid Request", "JSON-RPC version must be 2.0")
                continue

            if method == "mcp/setTools":
                response = {"jsonrpc": "2.0", "id": request_id, "result": {"status": "success"}}
            elif method == "mcp/runTool":
                tool_name = params.get("name")
                tool_params = params.get("arguments", {})

                if tool_name in TOOL_DEFINITIONS:
                    try:
                        tool_function = TOOL_DEFINITIONS[tool_name]
                        result = tool_function(**tool_params)
                        response = {"jsonrpc": "2.0", "id": request_id, "result": result}
                    except Exception as e:
                        tb_str = traceback.format_exc()
                        send_error(request_id, -32000, "Tool Execution Error", f"Error in '{tool_name}': {e}
{tb_str}")
                        continue
                else:
                    send_error(request_id, -32601, "Method not found", f"Tool '{tool_name}' is not defined.")
                    continue
            else:
                send_error(request_id, -32601, "Method not found", f"Method '{method}' is not supported.")
                continue

            send_response(response)

        except json.JSONDecodeError:
            send_error(None, -32700, "Parse error", "Invalid JSON received.")
        except Exception as e:
            tb_str = traceback.format_exc()
            send_error(None, -32603, "Internal error", f"{e}
{tb_str}")


def send_response(response):
    """Sends a JSON-RPC response to stdout."""
    message = json.dumps(response)
    sys.stdout.write(message + "
")
    sys.stdout.flush()

def send_error(request_id, code, message, data=None):
    """Constructs and sends a JSON-RPC error response."""
    error_payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message, "data": data},
    }
    send_response(error_payload)

if __name__ == "__main__":
    main()
