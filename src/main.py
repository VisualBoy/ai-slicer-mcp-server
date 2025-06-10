import sys
import json
import traceback
import inspect  # Added import
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

            if method == "mcp/getTools":  # Changed from mcp/setTools
                tools_schema = []
                for tool_name, tool_func in TOOL_DEFINITIONS.items():
                    docstring = inspect.getdoc(tool_func)
                    description = docstring.split('
')[0] if docstring else "No description available." # Extract first line of docstring

                    sig = inspect.signature(tool_func)
                    parameters_schema = []
                    for param_name, param in sig.parameters.items():
                        param_type = str(param.annotation) if param.annotation != inspect.Parameter.empty else "any"
                        # Remove <class ' '> wrapper if present
                        if param_type.startswith("<class '") and param_type.endswith("'>"):
                            param_type = param_type[8:-2]

                        parameters_schema.append({
                            "name": param_name,
                            "type": param_type,
                            "required": param.default == inspect.Parameter.empty,
                            # "description": "Parameter description placeholder" # Optional: Add later if needed
                        })

                    # Output schema
                    return_annotation = sig.return_annotation
                    output_type = str(return_annotation) if return_annotation != inspect.Signature.empty else "any"
                    if output_type.startswith("<class '") and output_type.endswith("'>"):
                        output_type = output_type[8:-2]


                    tools_schema.append({
                        "name": tool_name,
                        "description": description,
                        "inputs": parameters_schema,
                        "outputs": {"type": output_type, "description": "The result of the tool execution."} # Generic output description
                    })
                response = {"jsonrpc": "2.0", "id": request_id, "result": tools_schema}
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
            elif method == "mcp/setRoots":
                roots_param = params.get("roots")
                if roots_param is None:
                    send_error(request_id, -32602, "Invalid params", "The 'roots' parameter is required.")
                    continue

                # Log to stdout as requested
                print(f"MCP_SERVER_LOG: Received roots: {roots_param}")
                sys.stdout.flush() # Ensure it's printed immediately

                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"status": "success", "message": "Roots received"}
                }
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
