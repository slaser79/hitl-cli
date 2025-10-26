# A Guide to Testing MCP Clients and Servers with FastMCP

## Introduction
FastMCP is a Pythonic library designed to simplify the creation of MCP (Microservice Communication Protocol) servers and clients [3]. It emphasizes ease of use and provides robust features for building, testing, and integrating AI assistants and other microservices [4, 8]. This guide will walk you through the process of testing both MCP clients and servers using FastMCP, including specific considerations for OAuth 2.1 authentication flows.

## FastMCP Setup and Basic Server/Client Creation
To get started with FastMCP, you typically install it via pip. A basic FastMCP server can expose resources and define prompts, while a client can interact with these components [3, 5].

### Installation
pip install fastmcp
## Testing MCP Clients and Servers

FastMCP provides an efficient way to test both clients and servers, primarily through its in-memory testing capabilities. This approach allows you to test your server logic without the overhead of network communication, making tests faster and more reliable [2, 7].

### In-Memory Server Testing

The most straightforward way to test an MCP server built with FastMCP is to instantiate a `FastMCPClient` directly with your server object. This bypasses the need to run the server on a specific port and allows for direct method calls [2, 5].

Consider a more complex server with multiple tools or resources:

from fastmcp import FastMCP, Prompt, Resource

server = FastMCP()

@server.resource("/data/{item_id}")
def get_item_data(item_id: str):
    """Retrieves data for a specific item."""
    items = {"item1": "Data for Item 1", "item2": "Data for Item 2"}
    return items.get(item_id, "Item not found")

@server.tool("process_text")
async def process_text_tool(prompt: Prompt) -> Resource:
    """Processes text from a prompt and returns a modified resource."""
    if prompt.type == "text_input" and "content" in prompt.data:
        processed_content = prompt.data["content"].upper()
        return Resource(type="processed_text", data={"result": processed_content})
    return Resource(type="error", data={"message": "Invalid prompt for text processing"})

# Create an in-memory client for testing
client = FastMCPClient(server)

# Test a resource endpoint
response_resource = client.get("/data/item1")
print(f"Resource Test: {response_resource}") # Expected: "Data for Item 1"

response_not_found = client.get("/data/item3")
print(f"Resource Test (Not Found): {response_not_found}") # Expected: "Item not found"

# Test a tool call
text_prompt = Prompt(type="text_input", data={"content": "hello world"})
response_tool = await client.call("process_text", prompt=text_prompt)
print(f"Tool Test: {response_tool.data['result']}") # Expected: "HELLO WORLD"

invalid_prompt = Prompt(type="invalid_type", data={})
response_invalid_tool = await client.call("process_text", prompt=invalid_prompt)
print(f"Tool Test (Invalid): {response_invalid_tool.data['message']}") # Expected: "Invalid prompt for text processing"
## Testing OAuth 2.1 Flows with FastMCP

Recent updates to FastMCP have introduced first-class support for authentication, including pragmatic Bearer token support and seamless OAuth 2.1 integration [6]. This is a significant development for securing MCP servers and clients, moving towards a more fortified and robust communication protocol [2, 4]. OAuth 2.1 is a streamlined and more secure version of OAuth 2.0, emphasizing best practices like PKCE (Proof Key for Code Exchange) and removing less secure flows [7].

### Integrating OAuth 2.1 with FastMCP

While FastMCP itself handles the integration of authentication mechanisms, testing involves ensuring that your MCP server correctly enforces access policies and that your clients can successfully authenticate and authorize. The general approach involves:

1.  **Configuring your FastMCP server** to require authentication for certain resources or tools.
2.  **Obtaining an OAuth 2.1 token** from an Authorization Server.
3.  **Using the FastMCP client** to send this token with requests.

FastMCP's design allows for the separation of concerns, where an OAuth 2.1 server handles authentication flows and token management, while the FastMCP server focuses on its core functionality [2].

### Example: Testing an Authenticated Resource

Let's assume you have an OAuth 2.1 Authorization Server (e.g., using a library like Authlib or a dedicated service) that issues access tokens. Your FastMCP server would then be configured to validate these tokens.

from fastmcp import FastMCP, FastMCPClient, Resource
from fastmcp.security import BearerTokenAuth
import jwt # You might use PyJWT for token validation on the server side

# --- Server Side (Conceptual) ---
# In a real scenario, this would involve a more robust token validation mechanism
# that communicates with your OAuth 2.1 Authorization Server or validates JWTs.

SECRET_KEY = "your-super-secret-key" # In production, use environment variables and strong keys

class MyAuthenticatedFastMCP(FastMCP):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply a security dependency to a resource or tool
        # This is a simplified example; actual implementation would involve
        # validating the token against an OAuth 2.1 provider.
        @self.resource("/secure_data")
        def get_secure_data(auth: BearerTokenAuth):
            try:
                # In a real app, you'd validate the token with your OAuth provider
                # For demonstration, we'll just check if it's present
                if auth.token:
                    # Decode and validate the token (e.g., check signature, expiry, audience)
                    # payload = jwt.decode(auth.token, SECRET_KEY, algorithms=["HS256"])
                    # print(f"Token payload: {payload}")
                    return Resource(type="secure_info", data={"message": "Access granted to secure data!"})
                else:
                    raise ValueError("Authentication required")
            except Exception as e:
                # Handle token validation failures
                raise ValueError(f"Authentication failed: {e}")

# Instantiate the authenticated server
secure_server = MyAuthenticatedFastMCP()

# --- Client Side Testing ---
# Simulate obtaining an access token (e.g., from an OAuth 2.1 authorization code flow)
# In a real test, you'd integrate with your OAuth provider's test environment
# For this example, we'll use a dummy token or a pre-generated one.
dummy_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Create a client for the secure server
secure_client = FastMCPClient(secure_server)

# Test access without a token (should fail)
try:
    response_no_auth = secure_client.get("/secure_data")
    print(f"No Auth Response: {response_no_auth}")
except Exception as e:
    print(f"No Auth Error: {e}") # Expected: Authentication failed

# Test access with a valid token
# FastMCPClient can be configured with a default bearer token or pass it per request
authenticated_client = FastMCPClient(secure_server, auth=BearerTokenAuth(dummy_access_token))
try:
    response_with_auth = authenticated_client.get("/secure_data")
    print(f"With Auth Response: {response_with_auth.data['message']}") # Expected: Access granted
except Exception as e:
    print(f"With Auth Error: {e}")

# You can also pass the token directly in the headers for specific requests
# response_direct_auth = secure_client.get("/secure_data", headers={"Authorization": f"Bearer {dummy_access_token}"})
# print(f"Direct Auth Response: {response_direct_auth.data['message']}")
## References

[1] LevelUp. (2025, July 18). *Session Security is MCP Security: What Broke in Prod (and What Finally Worked)*. Retrieved from https://levelup.gitconnected.com/session-security-is-mcp-security-what-broke-in-prod-and-what-finally-worked-dd94ad333e6e
[2] Hightower, R. (2025, June 20). *Securing MCP: From Vulnerable to Fortified — Building Secure HTTP-Based AI Integrations*. Medium. Retrieved from https://medium.com/@richardhightower/securing-mcp-from-vulnerable-to-fortified-building-secure-http-based-ai-integrations-b706b0281e73
[3] jlowin/fastmcp. (n.d.). *The fast, Pythonic way to build MCP servers and clients*. GitHub. Retrieved from https://github.com/jlowin/fastmcp
[4] DataCamp. (2025, July 15). *Building an MCP Server and Client with FastMCP 2.0*. Retrieved from https://www.datacamp.com/tutorial/building-mcp-server-client-fastmcp
[5] Apidog. (2025, July 16). *A Beginner's Guide to Use FastMCP*. Retrieved from https://apidog.com/blog/fastmcp/
[6] FastMCP. (2025, June 23). *FastMCP Updates*. Retrieved from https://gofastmcp.com/updates
[7] jlowin.dev. (2025, May 21). *Stop Vibe-Testing Your MCP Server*. Retrieved from https://www.jlowin.dev/blog/stop-vibe-testing-mcp-servers
[8] Pondhouse Data. (2025, April 27). *Creating an MCP Server Using FastMCP: A Comprehensive Guide*. Retrieved from https://www.pondhouse-data.com/blog/create-mcp-server-with-fastmcp
[9] bioerrorlog.work. (2025, April 11). *How to Use MCP Inspector: A Testing Tool for MCP Servers*. Retrieved from https://en.bioerrorlog.work/entry/how-to-use-mcp-inspector
[10] Goyal, A. (2025, July 16). *How to Test your MCP Server using MCP Inspector*. Medium. Retrieved from https://medium.com/@anil.goyal0057/how-to-test-your-mcp-server-using-mcp-inspector-c873c417eec1
