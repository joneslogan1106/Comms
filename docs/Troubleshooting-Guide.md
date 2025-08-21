# Troubleshooting Guide

This guide provides solutions to common issues encountered when setting up, running, or developing with the General Communications system.

## Quick Diagnostic Commands

### System Status Check
```bash
# Check if Python is installed and version
python3 --version

# Check if required ports are available
netstat -tulpn | grep -E "(6090|8070|9281|9980|10740|12090)"

# Check if C library is compiled
ls -la src/Server/lib16.so  # Linux/macOS
ls -la src/Server/16.dll    # Windows

# Test C library loading
cd src/Server && python3 c16.py
```

### Process Monitoring
```bash
# Check running server processes
ps aux | grep python | grep server

# Monitor network connections
sudo netstat -tulpn | grep python

# Check system resources
top -p $(pgrep -f "python.*server")
```

## Installation Issues

### Python Environment Problems

#### Issue: "python3: command not found"
**Symptoms**: Cannot run Python scripts
**Solutions**:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip
# or
sudo dnf install python3 python3-pip

# macOS
brew install python3

# Windows
# Download from python.org and add to PATH
```

#### Issue: "No module named 'prompt_toolkit'"
**Symptoms**: ImportError when running client
**Solutions**:
```bash
# Install missing dependency
pip3 install prompt_toolkit

# If pip3 not found
python3 -m pip install prompt_toolkit

# For user-only installation
pip3 install --user prompt_toolkit

# Verify installation
python3 -c "import prompt_toolkit; print('OK')"
```

#### Issue: Permission denied on Linux/macOS
**Symptoms**: Cannot execute Python scripts
**Solutions**:
```bash
# Make scripts executable
chmod +x src/Server/server.py
chmod +x src/Client/comms.py

# Or run with python3 explicitly
python3 src/Server/server.py
```

### C Library Compilation Issues

#### Issue: "gcc: command not found"
**Symptoms**: Cannot compile C library
**Solutions**:
```bash
# Ubuntu/Debian
sudo apt install build-essential gcc

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install gcc

# Fedora
sudo dnf groupinstall "Development Tools"
sudo dnf install gcc

# macOS
xcode-select --install

# Windows
# Install MinGW-w64 or Visual Studio Build Tools
```

#### Issue: "cannot find -lc" or linking errors
**Symptoms**: Compilation fails during linking
**Solutions**:
```bash
# Ubuntu/Debian
sudo apt install libc6-dev

# CentOS/RHEL
sudo yum install glibc-devel

# Alternative compilation flags
gcc -shared -fPIC -o lib16.so 16.c -lc

# For debugging
gcc -shared -fPIC -g -v -o lib16.so 16.c
```

#### Issue: "lib16.so: cannot open shared object file"
**Symptoms**: Python cannot load C library
**Solutions**:
```bash
# Check if file exists
ls -la src/Server/lib16.so

# Check file permissions
chmod 755 src/Server/lib16.so

# Check library dependencies
ldd src/Server/lib16.so

# Recompile with correct flags
cd src/Server
gcc -shared -fPIC -o lib16.so 16.c
```

#### Issue: Windows DLL compilation problems
**Symptoms**: Cannot create 16.dll on Windows
**Solutions**:
```cmd
# Using MinGW
gcc -shared -o 16.dll 16.c

# Using Visual Studio
cl /LD 16.c /Fe16.dll

# Check if DLL is created
dir 16.dll

# Test DLL loading
python -c "import ctypes; ctypes.CDLL('./16.dll')"
```

## Network and Connection Issues

### Port-Related Problems

#### Issue: "Address already in use"
**Symptoms**: Server fails to start with port binding error
**Solutions**:
```bash
# Find process using the port
sudo netstat -tulpn | grep :10740
sudo lsof -i :10740

# Kill the process
sudo kill -9 <PID>

# Or kill all Python processes (careful!)
sudo pkill -f python

# Check if port is free
telnet localhost 10740
```

#### Issue: "Connection refused"
**Symptoms**: Client cannot connect to server
**Diagnosis**:
```bash
# Check if server is running
ps aux | grep server.py

# Test server connectivity
telnet localhost 10740
nc -zv localhost 10740

# Check firewall status
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS/RHEL
```

**Solutions**:
```bash
# Start server if not running
cd src/Server && python3 server.py

# Configure firewall (Ubuntu)
sudo ufw allow 10740/tcp
sudo ufw allow 9281/tcp
sudo ufw allow 12090/tcp
sudo ufw allow 8070/tcp
sudo ufw allow 6090/tcp
sudo ufw allow 9980/tcp

# Configure firewall (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=10740/tcp
sudo firewall-cmd --permanent --add-port=9281/tcp
sudo firewall-cmd --permanent --add-port=12090/tcp
sudo firewall-cmd --permanent --add-port=8070/tcp
sudo firewall-cmd --permanent --add-port=6090/tcp
sudo firewall-cmd --permanent --add-port=9980/tcp
sudo firewall-cmd --reload
```

#### Issue: "Connection timeout"
**Symptoms**: Client hangs during connection
**Diagnosis**:
```bash
# Test network connectivity
ping <server_ip>

# Check routing
traceroute <server_ip>

# Test specific port
timeout 10 telnet <server_ip> 10740
```

**Solutions**:
- Verify server IP address in client configuration
- Check network connectivity between client and server
- Increase timeout values in code if needed
- Verify no proxy or VPN interference

### Authentication Issues

#### Issue: Authentication hangs or fails
**Symptoms**: Client connects but authentication doesn't complete
**Diagnosis**:
```bash
# Enable debug mode in server.py
# Set debug = 1

# Monitor server logs
tail -f server.log

# Check authentication ports
netstat -tulpn | grep -E "(9281|12090)"
```

**Solutions**:
```python
# In server.py, add debugging
def authentication(client):
    print(f"[DEBUG] Authenticating client: {client}")
    # ... rest of function

# Verify callback connection works
# Check if client can accept connections on port 12090
```

#### Issue: "Authed" message not received
**Symptoms**: Client waits indefinitely for authentication
**Solutions**:
- Ensure client can accept incoming connections
- Check if port 12090 is blocked by firewall
- Verify client IP address is reachable from server
- Try running client and server on same machine first

## Runtime Issues

### Message Handling Problems

#### Issue: Messages not appearing
**Symptoms**: Messages sent but not displayed on other clients
**Diagnosis**:
```bash
# Check database file
cat src/Server/database.db

# Monitor message ports
netstat -tulpn | grep -E "(6090|9980)"

# Enable debug output
# Add print statements in send_messages() and fetch_messages()
```

**Solutions**:
```python
# In server.py, add debugging to send_messages()
def send_messages(client, timed):
    print(f"[DEBUG] Sending messages to {client}, timed={timed}")
    # ... rest of function

# In comms.py, add debugging to fetch_messages()
def fetch_messages():
    print("[DEBUG] Waiting for messages...")
    # ... rest of function
```

#### Issue: Database corruption
**Symptoms**: Invalid message format errors
**Diagnosis**:
```bash
# Check database content
cat src/Server/database.db | head -10

# Validate message format
cd src/Server && python3 -c "
import db
with open('database.db', 'r') as f:
    for line in f:
        if line.strip():
            print(f'Valid: {db.validate_message(line.strip())}, Line: {line.strip()[:50]}')
"
```

**Solutions**:
```bash
# Backup current database
cp src/Server/database.db src/Server/database.db.backup

# Clean database (removes all messages)
> src/Server/database.db

# Or manually fix format issues
# Each line should be: {id};{timestamp};{username};{message}
```

#### Issue: Memory leaks or high CPU usage
**Symptoms**: Server performance degrades over time
**Diagnosis**:
```bash
# Monitor resource usage
top -p $(pgrep -f "python.*server")

# Check thread count
ps -eLf | grep server.py | wc -l

# Monitor memory usage over time
while true; do
    ps -p $(pgrep -f "python.*server") -o pid,vsz,rss,pcpu,pmem,time
    sleep 60
done
```

**Solutions**:
- Implement thread cleanup for disconnected clients
- Add periodic cleanup of old messages
- Monitor and limit maximum concurrent connections
- Use connection pooling instead of unlimited threads

### Client-Side Issues

#### Issue: Client crashes or hangs
**Symptoms**: Client stops responding or exits unexpectedly
**Diagnosis**:
```python
# Add exception handling to main functions
def main():
    try:
        # ... existing code
    except Exception as e:
        print(f"[ERROR] Client error: {e}")
        import traceback
        traceback.print_exc()

def fetch_messages():
    try:
        # ... existing code
    except Exception as e:
        print(f"[ERROR] Message fetch error: {e}")
```

**Solutions**:
- Add proper exception handling around network operations
- Implement reconnection logic for dropped connections
- Add timeout handling for all socket operations
- Use try-catch blocks around threading operations

#### Issue: Multi-line input not working
**Symptoms**: Alt+Enter or Esc+Enter doesn't work for multi-line messages
**Solutions**:
```bash
# Verify prompt_toolkit installation
python3 -c "from prompt_toolkit import PromptSession; print('OK')"

# Test terminal compatibility
python3 -c "
from prompt_toolkit import PromptSession
session = PromptSession()
print('Test multi-line input (Alt+Enter to finish):')
result = session.prompt('> ', multiline=True)
print(f'Result: {repr(result)}')
"

# Alternative key combinations to try:
# - Ctrl+Enter
# - Shift+Enter
# - Esc followed by Enter
```

## Performance Issues

### Server Performance

#### Issue: Slow message delivery
**Symptoms**: Messages take long time to appear on clients
**Diagnosis**:
```python
# Add timing to message delivery
import time

def send_messages(client, timed):
    start_time = time.time()
    # ... existing code
    end_time = time.time()
    print(f"[DEBUG] Message delivery took {end_time - start_time:.2f}s")
```

**Solutions**:
- Optimize database queries
- Implement message caching
- Use connection pooling
- Reduce heartbeat frequency if not needed

#### Issue: High memory usage
**Symptoms**: Server uses excessive RAM
**Solutions**:
```python
# Implement message cleanup
def cleanup_old_messages():
    # Remove messages older than 24 hours
    cutoff_time = time.time() - (24 * 60 * 60)
    # Implementation depends on your needs

# Add to server main loop
threading.Thread(target=cleanup_old_messages, daemon=True).start()
```

### Client Performance

#### Issue: Client becomes unresponsive
**Symptoms**: Client UI freezes during heavy message traffic
**Solutions**:
- Implement message batching
- Add message display limits
- Use asynchronous message processing
- Optimize terminal output

## Development and Debugging

### Debug Mode Setup

#### Enable Comprehensive Logging
```python
# Add to server.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use throughout code
logger.debug(f"Client {client} connected")
logger.info(f"Message received from {username}")
logger.error(f"Error in authentication: {e}")
```

#### Network Traffic Analysis
```bash
# Monitor all traffic on communication ports
sudo tcpdump -i any -n port 10740 or port 9281 or port 12090 or port 8070 or port 6090 or port 9980

# Monitor specific port
sudo tcpdump -i any -n port 10740 -A

# Save to file for analysis
sudo tcpdump -i any -n port 10740 -w traffic.pcap
```

### Code Debugging

#### Python Debugger Integration
```python
# Add breakpoints in code
import pdb

def authentication(client):
    pdb.set_trace()  # Debugger will stop here
    # ... rest of function

# Or use ipdb for better interface
import ipdb
ipdb.set_trace()
```

#### Thread Debugging
```python
# Monitor thread status
import threading

def print_thread_info():
    threads = threading.enumerate()
    print(f"Active threads: {len(threads)}")
    for thread in threads:
        print(f"  {thread.name}: {thread.is_alive()}")

# Call periodically
threading.Timer(30.0, print_thread_info).start()
```

## Error Reference

### Common Error Messages

#### "ConnectionRefusedError: [Errno 111] Connection refused"
- **Cause**: Server not running or port blocked
- **Solution**: Start server, check firewall, verify port availability

#### "OSError: [Errno 98] Address already in use"
- **Cause**: Port already bound by another process
- **Solution**: Kill existing process or change port

#### "ModuleNotFoundError: No module named 'prompt_toolkit'"
- **Cause**: Missing Python dependency
- **Solution**: `pip3 install prompt_toolkit`

#### "ctypes.OSError: lib16.so: cannot open shared object file"
- **Cause**: C library not compiled or not found
- **Solution**: Compile C library with correct flags

#### "ValueError: invalid literal for int() with base 10"
- **Cause**: Database corruption or invalid message format
- **Solution**: Validate and clean database file

#### "BrokenPipeError: [Errno 32] Broken pipe"
- **Cause**: Client disconnected unexpectedly
- **Solution**: Add proper exception handling and client cleanup

### Recovery Procedures

#### Complete System Reset
```bash
# Stop all processes
sudo pkill -f "python.*server"
sudo pkill -f "python.*comms"

# Clean databases
> src/Server/database.db
> src/Client/cdatabase.db

# Recompile C library
cd src/Server
rm -f lib16.so 16.dll
gcc -shared -fPIC -o lib16.so 16.c

# Restart server
python3 server.py
```

#### Database Recovery
```bash
# Backup corrupted database
cp src/Server/database.db src/Server/database.db.corrupted

# Extract valid messages
python3 -c "
import db
valid_messages = []
with open('database.db.corrupted', 'r') as f:
    for line in f:
        line = line.strip()
        if line and db.validate_message(line):
            valid_messages.append(line)

with open('database.db', 'w') as f:
    for msg in valid_messages:
        f.write(msg + '\n')
"
```

## Getting Help

### Information to Collect
When reporting issues, include:
1. Operating system and version
2. Python version (`python3 --version`)
3. Complete error messages
4. Steps to reproduce the issue
5. Network configuration (if relevant)
6. Log files (if available)

### Diagnostic Script
```bash
#!/bin/bash
# Save as diagnose.sh and run to collect system info

echo "=== System Information ==="
uname -a
python3 --version
gcc --version 2>/dev/null || echo "gcc not installed"

echo -e "\n=== Port Status ==="
netstat -tulpn | grep -E "(6090|8070|9281|9980|10740|12090)" || echo "No ports in use"

echo -e "\n=== File Status ==="
ls -la src/Server/lib16.so 2>/dev/null || echo "lib16.so not found"
ls -la src/Server/16.dll 2>/dev/null || echo "16.dll not found"
ls -la src/Server/database.db 2>/dev/null || echo "database.db not found"

echo -e "\n=== Process Status ==="
ps aux | grep python | grep -E "(server|comms)" || echo "No server/client processes running"

echo -e "\n=== Python Dependencies ==="
python3 -c "import prompt_toolkit; print('prompt_toolkit: OK')" 2>/dev/null || echo "prompt_toolkit: MISSING"
python3 -c "import ctypes; print('ctypes: OK')" 2>/dev/null || echo "ctypes: MISSING"

echo -e "\n=== C Library Test ==="
cd src/Server && python3 c16.py 2>/dev/null || echo "C library test failed"
```

This troubleshooting guide covers the most common issues encountered with the General Communications system. For additional help, refer to the other documentation files or create an issue with the diagnostic information.