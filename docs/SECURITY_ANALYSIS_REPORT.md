# JavaScript Security Analysis Report for Lever-MCP

## Executive Summary

This report analyzes the security posture of JavaScript expressions in the Lever-MCP codebase compared to the existing Lua implementation. **Critical security vulnerabilities were discovered that allow complete sandbox escape and arbitrary code execution.**

## Key Findings

### 🚨 Critical Security Issues

1. **Complete Sandbox Escape via Python Bridge**
   - JavaScript expressions can execute arbitrary Python code via `python.eval()`
   - Full filesystem read/write access through Python
   - System command execution capabilities
   - Environment variable access
   - No sandboxing or restrictions in place

2. **Lack of Security Framework**
   - No safe mode implementation for JavaScript (unlike Lua)
   - No `--unsafe` flag equivalent for JavaScript
   - No configuration to restrict dangerous operations

### ✅ Current Security State Comparison

| Feature | Lua | JavaScript | Status |
|---------|-----|------------|--------|
| Safe Mode Default | ✅ Yes | ❌ No | CRITICAL ISSUE |
| Filesystem Access Blocked | ✅ Yes | ❌ No | CRITICAL ISSUE |
| System Commands Blocked | ✅ Yes | ❌ No | CRITICAL ISSUE |
| Unsafe Flag Available | ✅ Yes | ❌ No | MISSING FEATURE |
| Module Loading Restricted | ✅ Yes | ❌ No | CRITICAL ISSUE |
| Python Code Execution | ✅ N/A | ❌ Full Access | CRITICAL ISSUE |

## Detailed Vulnerability Analysis

### 1. Python Bridge Exploitation

**Vulnerability**: JavaScript expressions have unrestricted access to Python execution environment.

**Proof of Concept**:
```javascript
// Read sensitive files
python.eval('open("/etc/passwd").read()[:100]')

// Execute system commands
python.eval('__import__("subprocess").run(["whoami"], capture_output=True, text=True).stdout.strip()')

// Write malicious files
python.eval('open("/tmp/malicious.txt", "w").write("COMPROMISED")')

// Import any Python module
python.eval('__import__("os").listdir("/")')
```

**Impact**: Complete system compromise, data exfiltration, privilege escalation.

### 2. Network Access via XMLHttpRequest

**Vulnerability**: XMLHttpRequest object is available without restrictions.

**Proof of Concept**:
```javascript
// While synchronous XHR is blocked, async requests may be possible
new XMLHttpRequest()  // Returns functional XHR object
```

**Impact**: Data exfiltration, SSRF attacks, information disclosure.

### 3. Prototype Pollution

**Vulnerability**: JavaScript prototype pollution is possible.

**Proof of Concept**:
```javascript
Object.prototype.polluted = 'test'  // Succeeds
```

**Impact**: Application logic manipulation, potential escalation.

## Lua Security Implementation (Reference)

Lua implements comprehensive security through:

```python
if safe_mode:
    # Apply safety rails - disable dangerous functions but keep useful ones
    lua_runtime.execute("""
        -- Disable dangerous file/system operations
        os = {
            -- Keep safe time/date functions
            time = os.time,
            date = os.date,
            clock = os.clock,
            difftime = os.difftime,
            -- Remove dangerous ones: execute, exit, getenv, remove, rename, etc.
        }

        -- Disable file I/O
        io = nil

        -- Disable module loading that could access filesystem
        require = nil
        dofile = nil
        loadfile = nil

        -- Disable debug library (could be used for introspection attacks)
        debug = nil
    """)
```

This approach:
- ✅ Blocks dangerous operations by default
- ✅ Preserves safe, useful functions
- ✅ Can be disabled with `--unsafe` flag
- ✅ Provides clear security boundaries

## Recommendations

### Immediate Actions (Priority 1 - Critical)

1. **Implement JavaScript Safe Mode**
   ```python
   # In lib/js.py
   JS_SAFE_MODE = True  # Default to safe mode

   def create_js_runtime(safe_mode=None):
       if safe_mode is None:
           safe_mode = JS_SAFE_MODE

       if safe_mode:
           # Remove dangerous globals
           pm.eval("delete globalThis.python")
           pm.eval("delete globalThis.pmEval")
           # Additional restrictions...
   ```

2. **Disable Python Bridge by Default**
   - Remove `python` object from JavaScript global scope
   - Remove `pmEval` access
   - Only enable with explicit `--javascript-unsafe` flag

3. **Add Command Line Security Controls**
   ```bash
   # Safe by default
   python main.py --javascript

   # Explicit unsafe mode required
   python main.py --javascript --javascript-unsafe
   ```

### Short-term Actions (Priority 2)

1. **Restrict Global Objects**
   - Audit all available globals in JavaScript runtime
   - Remove or restrict Function constructor, eval, Proxy, Reflect
   - Implement whitelist approach for globals

2. **Network Access Controls**
   - Disable or restrict XMLHttpRequest
   - Block file:// protocol access
   - Implement request filtering

3. **Add Security Warnings**
   ```python
   if not safe_mode:
       print("WARNING: JavaScript unsafe mode enabled - expressions can access filesystem and execute system commands")
   ```

### Long-term Actions (Priority 3)

1. **Configuration Integration**
   - Link JavaScript safe mode to global `SAFE_MODE` setting
   - Ensure `--unsafe` flag affects both Lua and JavaScript
   - Consistent security model across engines

2. **Security Documentation**
   - Document security model and risks
   - Provide guidance on safe usage
   - Add security considerations to README

3. **Security Testing**
   - Implement automated security tests
   - Regular security audits
   - Penetration testing for new features

## Proposed Secure Implementation

### Modified lib/js.py

```python
# Global configuration for JavaScript safety mode
JS_SAFE_MODE = True  # Default to safe mode

def create_js_runtime(safe_mode=None):
    """Create a JavaScript runtime with optional sandboxing."""
    if safe_mode is None:
        safe_mode = JS_SAFE_MODE

    # Register MCP tools first
    _register_mcp_tools_in_js()

    if safe_mode:
        # Remove dangerous Python bridge
        pm.eval("delete globalThis.python")
        pm.eval("delete globalThis.pmEval")

        # Restrict dangerous constructors
        pm.eval("globalThis.Function = undefined")
        pm.eval("globalThis.eval = undefined")

        # Limit XMLHttpRequest (if keeping it)
        pm.eval("""
            const OriginalXHR = XMLHttpRequest;
            globalThis.XMLHttpRequest = function() {
                throw new Error('XMLHttpRequest disabled in safe mode');
            };
        """)

        # Add security marker
        pm.eval("globalThis.__SAFE_MODE__ = true")

    return pm.eval("globalThis")
```

### Modified main.py Integration

```python
# Update global configuration based on command line args
SAFE_MODE = not args.unsafe
JS_SAFE_MODE = not args.javascript_unsafe if hasattr(args, 'javascript_unsafe') else SAFE_MODE

# Pass safe mode to JavaScript lib
import lib.js
lib.js.JS_SAFE_MODE = JS_SAFE_MODE
```

## Risk Assessment

| Risk Category | Current Risk Level | Post-Implementation Risk Level |
|---------------|-------------------|-------------------------------|
| Arbitrary Code Execution | CRITICAL | LOW |
| Filesystem Access | CRITICAL | LOW |
| System Command Execution | CRITICAL | LOW |
| Network Access | HIGH | MEDIUM |
| Data Exfiltration | CRITICAL | LOW |
| Privilege Escalation | CRITICAL | LOW |

## Conclusion

The current JavaScript implementation in Lever-MCP represents a **critical security vulnerability** that provides unrestricted access to the underlying Python environment and system resources. This is in stark contrast to the secure-by-default Lua implementation.

**Immediate action is required** to implement proper sandboxing for JavaScript expressions to prevent malicious code execution and system compromise. The proposed secure implementation follows the proven security model used by Lua and should be implemented before JavaScript expressions are used in production environments.

The security model should follow the principle of **secure by default** with an explicit opt-in for unsafe operations, matching the existing Lua behavior and user expectations.

---

*Report generated on: 2025-01-08*
*Test files available: js_security_test.py, js_security_test_advanced.py, js_python_bridge_test.py, security_comparison.py*
