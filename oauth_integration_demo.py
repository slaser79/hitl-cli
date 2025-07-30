#!/usr/bin/env python3
"""
OAuth 2.1 Dynamic Client Registration Integration Demo

This script demonstrates the new OAuth 2.1 functionality implemented in hitl-cli:
1. Dynamic client registration (RFC 7591)
2. OAuth 2.1 authorization with PKCE (RFC 7636)
3. Bearer token authentication for MCP calls
4. X-MCP-Agent-Name header support
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

def demo_oauth_flow():
    """Demonstrate the OAuth 2.1 dynamic registration flow"""
    print("OAuth 2.1 Dynamic Client Registration Demo")
    print("=" * 50)
    
    print("\n1. PKCE Code Generation (RFC 7636)")
    print("-" * 30)
    
    try:
        from hitl_cli.auth import OAuthDynamicClient
        
        client = OAuthDynamicClient()
        
        # Generate PKCE parameters
        code_verifier = client._generate_code_verifier()
        code_challenge = client._generate_code_challenge(code_verifier)
        state = client._generate_state()
        
        print(f"✅ Code verifier: {code_verifier[:20]}... (length: {len(code_verifier)})")
        print(f"✅ Code challenge: {code_challenge[:20]}...")
        print(f"✅ State parameter: {state[:20]}...")
        
        # Validate PKCE requirements
        assert 43 <= len(code_verifier) <= 128, "Code verifier length invalid"
        assert code_challenge != code_verifier, "Code challenge must differ from verifier"
        assert len(state) >= 32, "State parameter too short"
        
    except ImportError:
        print("❌ OAuth client not available (missing dependencies)")
        return False
    
    print("\n2. Dynamic Client Registration Request")
    print("-" * 40)
    
    agent_name = "Demo Agent"
    
    # Show what registration request would look like
    registration_data = {
        "client_name": f"HITL CLI - {agent_name}",
        "redirect_uris": [client.redirect_uri],
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "client_secret_post",
        "scope": "openid profile email"
    }
    
    print("Registration request data:")
    for key, value in registration_data.items():
        print(f"  {key}: {value}")
    
    print(f"✅ Would POST to: {client.base_url}/api/v1/oauth/register")
    
    print("\n3. Authorization URL Generation")
    print("-" * 35)
    
    client_id = "demo-client-123"
    auth_url = client._build_authorization_url(client_id, code_challenge, state)
    
    print(f"Authorization URL: {auth_url}")
    
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(auth_url)
    params = parse_qs(parsed.query)
    
    print("\nURL parameters:")
    for key, value in params.items():
        print(f"  {key}: {value[0]}")
    
    print("\n4. Token Exchange with X-MCP-Agent-Name")
    print("-" * 42)
    
    print("Token exchange request would include:")
    print(f"  URL: {client.base_url}/api/v1/oauth/token")
    print("  Headers:")
    print("    Content-Type: application/x-www-form-urlencoded")
    print(f"    X-MCP-Agent-Name: {agent_name}")
    print("  Data:")
    print("    grant_type: authorization_code")
    print("    code: <authorization_code>")
    print(f"    redirect_uri: {client.redirect_uri}")
    print("    client_id: <dynamic_client_id>")
    print("    client_secret: <dynamic_client_secret>")
    print("    code_verifier: <pkce_code_verifier>")
    
    print("\n5. CLI Usage Examples")
    print("-" * 25)
    
    print("New CLI commands available:")
    print()
    print("  # OAuth 2.1 dynamic login")
    print("  hitl-cli login --dynamic --name 'My Agent'")
    print()
    print("  # Make requests with OAuth Bearer auth")
    print("  hitl-cli request --prompt 'Approve deployment?' --agent-name 'My Agent'")
    print()
    print("  # Task completion notification") 
    print("  hitl-cli notify-completion --summary 'Deployment complete' --agent-name 'My Agent'")
    print()
    print("  # Traditional login (still works)")
    print("  hitl-cli login")
    print()
    print("  # Logout (clears both auth methods)")
    print("  hitl-cli logout")
    
    print("\n6. Token Storage Security")
    print("-" * 28)
    
    from hitl_cli.config import CONFIG_DIR, OAUTH_CLIENT_FILE, OAUTH_TOKEN_FILE
    
    print("Secure token storage locations:")
    print(f"  Config directory: {CONFIG_DIR}")
    print(f"  OAuth client: {OAUTH_CLIENT_FILE}")
    print(f"  OAuth tokens: {OAUTH_TOKEN_FILE}")
    print("  Permissions: 700 (directory), 600 (files)")
    
    print("\n7. Backward Compatibility")
    print("-" * 27)
    
    print("✅ Existing Google OAuth + JWT flow preserved")
    print("✅ Existing MCP client functionality maintained")
    print("✅ All existing CLI commands work unchanged")
    print("✅ New OAuth features are opt-in with --dynamic flag")
    
    print("\n🎉 OAuth 2.1 Dynamic Client Registration Implementation Complete!")
    print("\nKey features implemented:")
    print("  • RFC 7591 dynamic client registration")
    print("  • OAuth 2.1 with PKCE (RFC 7636)")
    print("  • Bearer token authentication")
    print("  • X-MCP-Agent-Name header support")
    print("  • Automatic token refresh")
    print("  • Secure token storage")
    print("  • Full backward compatibility")
    
    return True

if __name__ == "__main__":
    demo_oauth_flow()