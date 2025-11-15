# CLAUDE.md - AI Assistant Guide for Proxy Poxy

## Project Overview

**Proxy Poxy** is a Python tool that connects to cloud instances (AWS or Digital Ocean) and establishes an SSH tunnel to be used as a SOCKS proxy. The tool automatically discovers running instances in the configured cloud provider and connects to the first available instance.

**Primary Use Case**: Create temporary SOCKS proxies through cloud instances for secure/anonymous browsing.

**Status**: Early development stage - basic functionality implemented, but with known limitations.

## Codebase Structure

```
proxypoxy/
├── poxy.py           # Main entry point and orchestration
├── aws.py            # AWS cloud provider implementation
├── digitalocean.py   # Digital Ocean cloud provider implementation
├── ssh.py            # SSH tunnel/proxy management
├── README.md         # User-facing documentation
├── LICENSE           # License file
└── .gitignore        # Ignores *.pyc and *.json files
```

### File Responsibilities

#### poxy.py (Main Entry Point)
- **Lines 10-22**: Configuration loading from JSON file
- **Lines 24-25**: Proxy initialization with SSH key and port
- **Lines 32-35**: Cloud provider selection logic (AWS vs Digital Ocean)
- **Lines 46**: Retrieves public IP address from cloud instance
- **Lines 52-53**: Establishes SSH tunnel and waits for termination

**Key Flow**:
1. Load config from command-line argument
2. Initialize Proxy object with SSH keys
3. Select cloud provider based on config (AWS has priority)
4. Get public IP from first available instance
5. Connect via SSH and establish SOCKS tunnel
6. Wait for user to terminate connection

#### aws.py (AWS Cloud Provider)
- **Class**: `Cloud`
- **Lines 8-10**: Constructor - initializes boto3 EC2 client
- **Lines 12-16**: Placeholder methods for create/destroy (not implemented)
- **Lines 18-30**: `getPublicAddress()` - returns public IP from first instance
- **Lines 32-34**: `list_instances()` - wrapper around boto3 describe_instances

**Important**: create_instance and destroy_instance are stubs (copy-paste error on line 16).

#### digitalocean.py (Digital Ocean Provider)
- **Class**: `Cloud`
- **Lines 10-15**: Constructor - requires token, creates urllib3 pool manager
- **Lines 17-24**: Token management (getter/setter)
- **Lines 26-40**: `getPublicAddress()` - extracts public IPv4 from first droplet
- **Lines 42-56**: `list_instances()` - API call to Digital Ocean droplets endpoint
- **Lines 58-62**: Debug helper for rate limit tracking

**Note**: Uses urllib3 + certifi for HTTPS requests to DO API.

#### ssh.py (SSH Tunnel Management)
- **Class**: `Proxy`
- **Lines 16-19**: Constructor - stores SSH keys and port
- **Lines 21-34**: `connect()` - launches SSH subprocess with SOCKS proxy enabled
- **Lines 35-41**: `just_wait()` - blocks until SSH terminates, handles Ctrl+C

**Important Notes**:
- Uses subprocess instead of paramiko (commented out code on lines 29-34)
- SSH command: `ssh -D <port> -i <private_key> <username>@<ip_address>`
- Graceful shutdown on KeyboardInterrupt

## Architecture & Design Patterns

### Cloud Provider Abstraction
Both `aws.py` and `digitalocean.py` implement a `Cloud` class with:
- `__init__(...)`: Provider-specific initialization
- `getPublicAddress()`: Returns IP of first available instance
- `list_instances()`: Returns provider's instance data
- `username`: Stored as instance variable for SSH connection

**Selection Logic**: AWS takes priority if username is configured (poxy.py:32-35).

### Configuration-Driven
- Single JSON config file passed as command-line argument
- Cloud credentials separate from SSH/SOCKS settings
- Username moved to cloud-specific config (per commit c33accd)

### Subprocess-Based SSH
- Previously attempted paramiko implementation (failed)
- Currently uses subprocess.Popen with ssh command
- Blocks until SSH session terminates

## Development Workflows

### Python Version
- **Python 2.x** (evident from `print >>` syntax and string handling)
- Not compatible with Python 3 without modifications

### Adding a New Cloud Provider
1. Create new file `<provider>.py`
2. Implement `Cloud` class with:
   - `__init__(self, username, **auth_params)`
   - `getPublicAddress(self)` - return string IP
   - `list_instances(self)` - return provider data
   - Set `self.username` for SSH
3. Import in `poxy.py`
4. Add conditional in poxy.py:32-39 for provider selection
5. Update config.json schema in README.md

### Testing Approach
- No automated tests currently exist
- Manual testing required
- Test with actual cloud credentials
- **Warning**: README notes "not expect it to work and have a fire extinguisher close to you"

### Git Workflow
- Development on feature branches (claude/*)
- Commit messages should be descriptive
- Recent commits show pattern: "verb + description" or "* bulleted changes"

## Configuration File

### Required Structure
```json
{
  "aws": {
    "username": "ec2-user"  // Empty string disables AWS
  },
  "digitalocean": {
    "username": "root",
    "token": "dop_v1_..."  // Empty string disables DO
  },
  "socks": {
    "key": {
      "private": "/path/to/private_key",
      "public": "/path/to/public_key"
    },
    "port": 8080
  }
}
```

### Important Config Notes
- Username field moved from "socks" to cloud-specific sections (commit c33accd)
- AWS requires only username (uses default boto3 credentials chain)
- Digital Ocean requires token + username
- Config files ignored by .gitignore (*.json)

## Dependencies

### Required Libraries
```
subprocess  # Standard library - SSH execution
json        # Standard library - config parsing
sys         # Standard library
boto3       # AWS SDK
urllib3     # HTTP client for Digital Ocean API
certifi     # SSL certificate validation
```

### Installation
No requirements.txt exists. Install manually:
```bash
pip install boto3 urllib3 certifi
```

## Common Tasks & TODO Items

### Current TODO List (from README.md)
1. **Start/Stop Commands**:
   - `./poxy.py start` - begin procedure, create instance if needed
   - `./poxy.py stop` - destroy instance if created by script

2. **Instance Lifecycle** (from poxy.py:43-44, 55-62):
   - Verify if instance exists, create smallest if not
   - Destroy instances created by script on exit
   - Tag/name instances with hash for tracking

### Known Issues
1. **AWS stubs**: create_instance and destroy_instance not implemented
2. **Paramiko commented out**: SSH implementation switched to subprocess
3. **No error handling**: Missing validation for missing instances
4. **Python 2 only**: Not Python 3 compatible
5. **Single instance logic**: Always uses first instance found

## Key Conventions for AI Assistants

### Code Style
- **Indentation**: 4 spaces
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Private members**: Double underscore prefix (e.g., `__token__`)
- **Comments**: Inline comments with `#`, docstrings for functions
- **Debug output**: Use `print >> sys.stderr` for debugging

### Error Handling Patterns
- Return None for failures in constructors (see digitalocean.py:12)
- Use `sys.exit(1)` for fatal errors (see poxy.py:16, 39)
- Minimal try/except - only in ssh.py for KeyboardInterrupt

### API Consistency
When modifying cloud providers, maintain:
- `Cloud` class name
- `username` instance variable
- `getPublicAddress()` method signature
- `list_instances()` method signature

### Documentation
- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update config file examples when schema changes
- Maintain TODO sections in both README.md and code comments

### Security Considerations
- Never commit config files (blocked by .gitignore)
- SSH keys should be file paths, not embedded
- Validate all config inputs before use
- Be cautious with cloud API tokens

### Testing Changes
Before committing:
1. Test with both AWS and Digital Ocean configs
2. Verify SSH tunnel establishes correctly
3. Test proxy functionality (e.g., `curl --socks5 localhost:8080`)
4. Check graceful shutdown with Ctrl+C
5. Verify no credentials leaked in debug output

## Important Implementation Details

### SSH Constructor Signature Issue
`ssh.py:16` - Constructor accepts `public_key` parameter but ssh.py:24 never uses it. When calling from poxy.py:25, only private key is passed.

**Resolution**: When modifying SSH logic, clarify if public_key is needed.

### Cloud Selection Priority
AWS is checked first (poxy.py:32), Digital Ocean second (poxy.py:34). Empty username string disables that provider.

**Note**: If both configured, AWS wins. Document this behavior if changing.

### Port Configuration
Port appears in two places:
- `poxy.py:25` - Proxy initialization
- `poxy.py:52` - Connect call

Both should use `data["socks"]["port"]` for consistency.

### IP Address Discovery
Both cloud providers expect at least one running instance. No handling for zero instances scenario - will crash.

**Improvement opportunity**: Add instance creation if none found (per TODO).

## Development Environment

### Minimal Setup
```bash
git clone <repo>
cd proxypoxy
pip install boto3 urllib3 certifi
# Create config.json (see README.md)
./poxy.py config.json
```

### AWS Authentication
Uses boto3 default credential chain:
1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
2. ~/.aws/credentials
3. IAM role (if on EC2)

### Digital Ocean Authentication
Requires API token in config file. Generate from DO dashboard.

## Recent Changes (from Git History)

- **bff63d3**: Updated README.md to match config file changes
- **c33accd**: Major refactor - username moved to cloud configs, AWS support added
- **70cd46f**: Added .gitignore
- **adef004**: Custom port support, switched to subprocess from paramiko
- **4548c47**: Added usage instructions to README

## OpenStack Support (Planned)

Per README.md, OpenStack support is planned but not implemented. To add:
1. Create `openstack.py` with `Cloud` class
2. Likely use python-openstackclient or similar
3. Add to config schema under "openstack" key
4. Add conditional in poxy.py provider selection

---

**Last Updated**: 2025-11-15
**Repository**: proxypoxy
**Primary Language**: Python 2.x
**Maintainer**: See git history
