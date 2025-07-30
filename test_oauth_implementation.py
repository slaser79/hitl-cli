#!/usr/bin/env python3
"""
Simple test script to verify OAuth 2.1 dynamic client registration implementation
"""

import base64
import hashlib
import secrets
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_pkce_code_generation():
    """Test PKCE code verifier and challenge generation"""
    print("Testing PKCE code generation...")
    
    # Generate code verifier (43-128 characters, URL-safe)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    print(f"Code verifier: {code_verifier}")
    print(f"Code verifier length: {len(code_verifier)}")
    
    # Verify length requirements
    assert 43 <= len(code_verifier) <= 128, f"Code verifier length {len(code_verifier)} not in range 43-128"
    
    # Generate code challenge (SHA256 hash of verifier, base64url encoded)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
    print(f"Code challenge: {code_challenge}")
    
    # Verify they're different
    assert code_challenge != code_verifier, "Code challenge should differ from verifier"
    
    print("✅ PKCE code generation test passed!")
    return True

def test_oauth_client_creation():
    """Test OAuth client initialization"""
    print("\nTesting OAuth client creation...")
    
    try:
        from hitl_cli.auth import OAuthDynamicClient
        
        client = OAuthDynamicClient()
        print(f"Base URL: {client.base_url}")
        print(f"Callback port: {client.callback_port}")
        print(f"Redirect URI: {client.redirect_uri}")
        
        # Test PKCE methods
        code_verifier = client._generate_code_verifier()
        code_challenge = client._generate_code_challenge(code_verifier)
        state = client._generate_state()
        
        print(f"Generated code verifier: {code_verifier[:20]}...")
        print(f"Generated code challenge: {code_challenge[:20]}...")
        print(f"Generated state: {state[:20]}...")
        
        # Verify PKCE generation
        assert 43 <= len(code_verifier) <= 128
        assert len(code_challenge) > 0
        assert len(state) >= 32
        
        print("✅ OAuth client creation test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ OAuth client test failed: {e}")
        return False

def test_oauth_token_management():
    """Test OAuth token save/load functionality"""
    print("\nTesting OAuth token management...")
    
    try:
        from hitl_cli.auth import save_oauth_token, load_oauth_token, is_oauth_token_expired
        import tempfile
        import time
        from pathlib import Path
        
        # Create temporary config directory
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".config" / "hitl-cli"
            oauth_token_file = config_dir / "oauth_token.json"
            
            # Mock the config paths
            import hitl_cli.auth as auth_module
            original_config_dir = auth_module.CONFIG_DIR
            original_oauth_token_file = auth_module.OAUTH_TOKEN_FILE
            
            auth_module.CONFIG_DIR = config_dir
            auth_module.OAUTH_TOKEN_FILE = oauth_token_file
            
            try:
                # Test token data
                token_data = {
                    "access_token": "test-access-token",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "refresh_token": "test-refresh-token",
                    "expires_at": int(time.time()) + 3600
                }
                
                # Test save
                save_oauth_token(token_data)
                assert oauth_token_file.exists(), "OAuth token file should be created"
                
                # Test load
                loaded_token = load_oauth_token()
                assert loaded_token is not None, "Should load OAuth token"
                assert loaded_token["access_token"] == "test-access-token"
                assert loaded_token["token_type"] == "Bearer"
                
                # Test expiry check (not expired)
                assert not is_oauth_token_expired(loaded_token), "Token should not be expired"
                
                # Test expiry check (expired)
                expired_token = {**token_data, "expires_at": int(time.time()) - 3600}
                assert is_oauth_token_expired(expired_token), "Token should be expired"
                
                print("✅ OAuth token management test passed!")
                return True
                
            finally:
                # Restore original paths
                auth_module.CONFIG_DIR = original_config_dir
                auth_module.OAUTH_TOKEN_FILE = original_oauth_token_file
                
    except Exception as e:
        print(f"❌ OAuth token management test failed: {e}")
        return False

def test_oauth_url_building():
    """Test OAuth authorization URL building"""
    print("\nTesting OAuth URL building...")
    
    try:
        from hitl_cli.auth import OAuthDynamicClient
        from urllib.parse import urlparse, parse_qs
        
        client = OAuthDynamicClient()
        
        # Test parameters
        client_id = "test-client-id"
        code_challenge = "test-code-challenge"
        state = "test-state"
        
        # Build authorization URL
        auth_url = client._build_authorization_url(client_id, code_challenge, state)
        print(f"Authorization URL: {auth_url}")
        
        # Parse and verify URL
        parsed = urlparse(auth_url)
        query_params = parse_qs(parsed.query)
        
        assert parsed.path == "/api/v1/oauth/authorize", f"Wrong path: {parsed.path}"
        assert query_params["response_type"][0] == "code"
        assert query_params["client_id"][0] == client_id
        assert query_params["redirect_uri"][0] == client.redirect_uri
        assert query_params["scope"][0] == "openid profile email"
        assert query_params["state"][0] == state
        assert query_params["code_challenge"][0] == code_challenge
        assert query_params["code_challenge_method"][0] == "S256"
        
        print("✅ OAuth URL building test passed!")
        return True
        
    except Exception as e:
        print(f"❌ OAuth URL building test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("OAuth 2.1 Dynamic Client Registration Implementation Tests")
    print("=" * 60)
    
    tests = [
        test_pkce_code_generation,
        test_oauth_client_creation,
        test_oauth_token_management,
        test_oauth_url_building,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! OAuth 2.1 implementation is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())