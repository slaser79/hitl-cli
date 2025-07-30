# Migration Guide: From Local to Cloud Production

This guide walks you through migrating from local development to using the production cloud deployment of the HITL relay system.

## 🌐 Production Service Information

- **Production URL**: https://hitl-relay-193514263276.europe-west2.run.app
- **API Documentation**: https://hitl-relay-193514263276.europe-west2.run.app/docs
- **MCP Server**: https://hitl-relay-193514263276.europe-west2.run.app/mcp-server
- **OAuth Server**: https://hitl-relay-193514263276.europe-west2.run.app/.well-known/oauth-authorization-server

## 📱 Step 1: Update Mobile App Configuration

### Option A: Environment Configuration (Recommended)

Create a configuration file to easily switch between environments:

```dart
// mobile_app/lib/src/config/api_config.dart
class ApiConfig {
  static const bool isProduction = bool.fromEnvironment('PRODUCTION', defaultValue: false);
  
  static String get baseUrl {
    return isProduction 
        ? 'https://hitl-relay-193514263276.europe-west2.run.app'
        : 'http://127.0.0.1:8000';
  }
  
  static String get mcpUrl => '$baseUrl/mcp-server';
  static String get docsUrl => '$baseUrl/docs';
}
```

Usage in your API client:
```dart
// mobile_app/lib/src/api/api_client.dart
import '../config/api_config.dart';

class ApiClient {
  final String baseUrl = ApiConfig.baseUrl;
  // ... rest of implementation
}
```

### Option B: Direct Update

Update your existing API client configuration:

```dart
// Find your API client configuration and update the base URL
static const String baseUrl = 'https://hitl-relay-193514263276.europe-west2.run.app';
```

### Building for Production

Build your Flutter app with the production flag:

```bash
# For production build
flutter build apk --dart-define=PRODUCTION=true

# For development build (default)
flutter build apk
```

## 🖥️ Step 2: Update CLI Configuration

### Option A: Environment Variable

Set the production server URL as an environment variable:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export HITL_SERVER_URL=https://hitl-relay-193514263276.europe-west2.run.app

# Or set for current session
export HITL_SERVER_URL=https://hitl-relay-193514263276.europe-west2.run.app
```

### Option B: Configuration File

Create a configuration file for the CLI:

```bash
# Create CLI config directory
mkdir -p ~/.config/hitl-cli

# Create config file
cat > ~/.config/hitl-cli/config.yaml << EOF
server:
  url: https://hitl-relay-193514263276.europe-west2.run.app
  timeout: 30

auth:
  token_cache: ~/.config/hitl-cli/tokens
EOF
```

### Verify CLI Connection

Test the CLI connection to the production server:

```bash
# Test connection (this should respond with API documentation)
curl https://hitl-relay-193514263276.europe-west2.run.app/docs

# Test CLI authentication
hitl-cli login

# List your agents
hitl-cli agents list
```

## 🤖 Step 3: Update MCP Client Configuration

### For mcp-remote

Update your MCP client configuration:

```json
{
  "mcp_server": {
    "url": "https://hitl-relay-193514263276.europe-west2.run.app/mcp-server",
    "auth": {
      "type": "oauth",
      "authorization_server": "https://hitl-relay-193514263276.europe-west2.run.app"
    }
  }
}
```

### For Custom MCP Clients

Update your MCP client code:

```python
# MCP client configuration
MCP_SERVER_URL = "https://hitl-relay-193514263276.europe-west2.run.app/mcp-server"
OAUTH_SERVER_URL = "https://hitl-relay-193514263276.europe-west2.run.app"

# Example tool call
async def call_human_input(prompt: str, choices: list = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MCP_SERVER_URL}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": "request_1",
                "method": "tools/call",
                "params": {
                    "name": "request_human_input",
                    "arguments": {
                        "prompt": prompt,
                        "choices": choices
                    }
                }
            },
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        return response.json()
```

## 🔧 Step 4: Development Workflow Changes

### Local Development Options

You now have three development options:

#### Option 1: Full Local Development (Default)
- Local FastAPI server
- Local SQLite database
- Good for: Feature development, testing

```bash
# No special configuration needed
./scripts/start.sh
```

#### Option 2: Local Server + Cloud Database
- Local FastAPI server
- Cloud PostgreSQL database
- Good for: Testing with production data

```bash
# Set database URL to connect to cloud
export DATABASE_URL="postgresql://user:password@host:5432/hitl_relay"
./scripts/start.sh
```

#### Option 3: Full Cloud (Recommended for Testing)
- Cloud FastAPI server
- Cloud PostgreSQL database
- Good for: Integration testing, user acceptance testing

```bash
# Update mobile app and CLI to point to production
# No local server needed
```

### Testing Your Migration

1. **Test Mobile App**:
   ```bash
   flutter run
   # Verify it connects to production API
   # Test authentication flow
   # Test request/response cycle
   ```

2. **Test CLI**:
   ```bash
   hitl-cli login
   hitl-cli request --prompt "Test production deployment" --choice "Works" --choice "Broken"
   ```

3. **Test MCP Integration**:
   ```bash
   # Test OAuth flow
   curl https://hitl-relay-193514263276.europe-west2.run.app/.well-known/oauth-authorization-server
   
   # Test MCP endpoint
   curl https://hitl-relay-193514263276.europe-west2.run.app/mcp-server
   ```

## 📊 Step 5: Monitoring and Troubleshooting

### Check Production Status

```bash
# Check service health
curl https://hitl-relay-193514263276.europe-west2.run.app/docs

# Check Cloud Run service
gcloud run services describe hitl-relay --region=europe-west2

# View logs
gcloud logs read --service=hitl-relay --limit=50
```

### Common Issues and Solutions

#### Issue: Mobile app can't connect
**Solution**: Check network connectivity and ensure you're using HTTPS URLs

#### Issue: Authentication failures
**Solution**: Verify Google OAuth client IDs are configured correctly for production

#### Issue: CLI timeouts
**Solution**: Check if you're behind a corporate firewall; production server may need to be whitelisted

#### Issue: MCP client can't authenticate
**Solution**: Ensure OAuth client is registered via the admin CLI command

### Rollback Plan

If you need to rollback to local development:

1. **Mobile App**: Build without `PRODUCTION=true` flag
2. **CLI**: Unset `HITL_SERVER_URL` environment variable
3. **Local Server**: Start with `./scripts/start.sh`

## 🎯 Next Steps

After migration, you can:

1. **Scale**: Monitor usage and adjust Cloud Run scaling parameters
2. **Monitor**: Set up alerting and monitoring in Google Cloud Console
3. **Optimize**: Review costs and optimize resource allocation
4. **Backup**: Ensure database backups are configured
5. **Security**: Review and tighten security policies

## 🔗 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Project README](../README.md)
- [Project Technical Documentation](../CLAUDE.md)

## 📞 Support

If you encounter issues during migration:

1. Check the [troubleshooting section](../CLAUDE.md#emergency-troubleshooting-workflow) in CLAUDE.md
2. Review GitHub Actions logs for deployment issues
3. Check Cloud Run logs for runtime issues
4. Verify environment variables and secrets are correctly configured
