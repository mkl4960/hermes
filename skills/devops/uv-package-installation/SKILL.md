---
name: uv-package-installation
description: Install Python packages using uv in Hermes environments when pip is unavailable or permissions are restricted.
category: devops
---

# UV Package Installation for Hermes

## Trigger Conditions
When you need to install a Python package but:
- Standard `pip` is not available (`python3 -m pip --version` fails)
- You lack sudo/system-wide installation privileges
- You're in a Hermes/Agent environment with restricted permissions
- You need to install packages for email functionality, web scraping, or other integrations

## Overview
This skill provides a reliable method to install Python packages in Hermes environments by discovering and using the `uv` package manager, which is often pre-configured in these systems.

## Steps

### 1. Check Available Package Managers
```bash
# Check if uv is available
which uv

# Check if pip is available (often missing in restricted environments)
which pip pip3
python3 -m pip --version  # Will likely fail with "No module named pip"
```

### 2. Install Using UV (Preferred Method in Hermes)
If `uv` is available (typically at `/usr/local/bin/uv`):
```bash
# Install package with uv
uv pip install <package-name>

# Example for AgentMail:
uv pip install agentmail

# Install in user space if needed (uv handles this automatically in most Hermes setups)
uv pip install --user <package-name>  # Though --user flag may not be supported
```

### 3. Verify Installation
```bash
# List installed packages to confirm
uv pip list | grep -i <package-name>

# Test import in Python
python3 -c "import <package-name>; print('Successfully imported', <package-name>.__version__)"
```

### 4. Alternative Approaches (if UV also fails)
If neither pip nor uv work:
- Check if the package is already available via system packages (apt/apk/yum)
- Look for pre-installed versions in `/opt/hermes/.venv/` or similar
- Consider if the task can be accomplished with alternative tools that are already installed

## Hermes-Specific Notes\n- In Hermes images, `uv` is typically pre-installed at `/usr/local/bin/uv`\n- The Python environment often uses `uv` for package management rather than traditional pip\n- Packages installed with `uv pip install` are usually available in `/opt/hermes/.venv/lib/python3.x/site-packages/`\n- You may need to add this path to `sys.path` in Python if imports fail initially:\n  ```python\n  import sys\n  sys.path.insert(0, '/opt/hermes/.venv/lib/python3.13/site-packages')\n  ```\n- **Important**: After installing packages with `uv`, you must use the Hermes-specific Python interpreter (`/opt/hermes/.venv/bin/python`) rather than the system Python (`/usr/bin/python3`) to access the installed packages. Always test with the interpreter you intend to use for your script.\n- When running scripts via cron that depend on newly installed packages, ensure the cron job uses the Hermes Python interpreter and that environment variables (like API keys from `/opt/data/.env`) are loaded. The script may need to source the .env file or explicitly load variables as shown in the check_agentmail.py example.

## Pitfalls and How to Avoid Them
1. **Assuming pip is available**: Always check first - in restricted environments, pip is often missing
2. **Trying sudo when not available**: Many Hermes environments don't have sudo - look for alternatives like uv
3. **Not verifying installation**: Always test that you can import the package after installation
4. **Ignoring environment paths**: Hermes may use virtual environments - check where packages are actually installed
5. **Overlooking version conflicts**: Use `uv pip list` to see what's already installed before adding new packages

## Verification
After installation, confirm:
- Package appears in `uv pip list` output
- Python can import the package without errors
- Basic functionality of the package works (e.g., for AgentMail, you can instantiate the client)

## Example: Installing AgentMail for Email Functionality
```bash
# 1. Check for uv
which uv
# Returns: /usr/local/bin/uv

# 2. Install AgentMail
uv pip install agentmail
# Output shows successful installation

# 3. Verify
uv pip list | grep agentmail
python3 -c "import agentmail; print(agentmail.__version__)"
# Should print: 0.4.15 (or current version)

# 4. Test basic usage (in Python)
from agentmail import AgentMail
client = AgentMail()  # Will need API key for actual use
```

## Related Skills
- `himalaya`: For CLI email management (alternative to AgentMail)
- `google-workspace`: For Gmail/Workspace integration
- Any skill requiring Python package installation can benefit from this approach

## When to Use This Skill
- Installing AgentMail for email sending
- Adding web scraping dependencies (beautifulsoup4, requests, etc.)
- Installing data analysis packages (pandas, numpy, etc.)
- Setting up authentication libraries for API integrations
- Any time standard pip installation fails in a Hermes environment