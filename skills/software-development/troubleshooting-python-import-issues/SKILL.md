---
name: troubleshooting-python-import-issues
description: Diagnose and resolve Python import errors when packages appear installed but fail to import
---

# Troubleshooting Python Import Issues

## When to Use This Skill
When encountering import errors like `ModuleNotFoundError` or `ImportError` for packages that appear to be installed, particularly when the package structure differs from expected import patterns.

## Steps to Diagnose and Fix

### 1. Verify Installation Location
Check where the package is actually installed:
```bash
find /opt/hermes/.venv -type d -name packagename 2>/dev/null
```

### 2. Examine Package Structure
Look at the actual package directory to understand its structure:
```bash
ls -la /path/to/package/
```

### 3. Check __init__.py for Exports
Examine what's actually exported in the package's __init__.py:
```bash
head -50 /path/to/package/__init__.py
grep -n "class.*ClassName" /path/to/package/module.py
```

### 4. Test Python Path
Verify what Python can see:
```bash
python3 -c "import sys; print('\\n'.join(sys.path))"
python3 -c "import packagename; print(packagename.__file__)"
```

### 5. Adjust Import Based on Findings
If direct import fails, try importing from the specific module:
```python
# Instead of: from packagename import ClassName
# Try: from packagename.module import ClassName
```

### 6. Set PYTHONPATH if Needed
If the package isn't in Python's path:
```bash
export PYTHONPATH="/path/to/package:$PYTHONPATH"
```

### 7. Verify with Simple Import Test
Test the corrected import:
```bash
PYTHONPATH="/correct/path:$PYTHONPATH" python3 -c "from packagename.module import ClassName; print('Success')"
```

## Specific Example: AgentMail Package
For the AgentMail package, the correct import is:
```python
from agentmail.client import AgentMail
```
Not:
```python
from agentmail import AgentMail  # This fails
```

## Verification Steps
1. Check if package is installed in expected location
2. Examine actual package structure and __init__.py
3. Test import with corrected path/module
4. Run the actual script with proper PYTHONPATH if needed
5. Verify the fix works in the target environment

## Common Pitfalls
- Assuming package exports match directory structure
- Not checking __init__.py for what's actually exported
- Overlooking submodules that contain the actual classes/functions
- Forgetting to set PYTHONPATH for cron jobs or scheduled tasks

## Prevention
- Always verify imports work in a test script before scheduling
- Document non-standard import patterns in project README
- Use virtual environments consistently to avoid path issues