# Development Guide

This guide provides comprehensive information for developers who want to understand, modify, or extend the General Communications system.

## Architecture Overview

### System Design Principles

#### Multi-threaded Architecture
The system uses a thread-per-client model:
- **Server**: Main thread accepts connections, spawns worker threads per client
- **Client**: Separate threads for heartbeat, message receiving, and user input
- **Synchronization**: Minimal shared state, mostly message passing

#### Protocol-First Design
- Custom TCP protocol with multiple specialized ports
- Each port serves a specific communication purpose
- Stateful connections with proper cleanup handling

#### Modular Structure
- Clear separation between server, client, and shared components
- Plugin system through `mods/` directories
- C library integration for performance-critical operations

### Code Organization

```
src/
├── Server/           # Server-side components
│   ├── server.py     # Main server application
│   ├── db.py         # Database operations
│   ├── c16.py        # C library interface
│   ├── 16.c          # C encoding library
│   └── mods/         # Server plugins
├── Client/           # Client-side components
│   ├── comms.py      # Client application
│   ├── db.py         # Client database operations
│   └── mods/         # Client plugins
└── Components/       # Shared components
    └── c16 components/ # Compiled libraries
```

## Development Environment Setup

### Prerequisites
- Python 3.6+ with development headers
- C compiler (gcc, clang, or MSVC)
- Git for version control
- Text editor or IDE with Python support

### Development Dependencies
```bash
pip install prompt_toolkit pytest black flake8 mypy
```

### Build System
```bash
# Development build with debug symbols
cd src/Server
gcc -shared -fPIC -g -O0 -o lib16.so 16.c

# Production build
gcc -shared -fPIC -O2 -o lib16.so 16.c
```

## Core Components Deep Dive

### Server Architecture (`server.py`)

#### Main Event Loop
```python
def acception():
    # Main server loop
    # 1. Accept client connections
    # 2. Spawn authentication thread
    # 3. Add client to active list
    # 4. Handle graceful shutdown
```

#### Client Lifecycle Management
1. **Connection**: Client connects to port 10740
2. **Authentication**: Multi-stage auth on ports 9281/12090
3. **Active State**: Heartbeat monitoring and message handling
4. **Cleanup**: Automatic removal on disconnect/timeout

#### Threading Model
- **Main Thread**: Connection acceptance
- **Auth Threads**: One per connecting client
- **Heartbeat Threads**: One per authenticated client
- **Message Threads**: One listener per client

### Client Architecture (`comms.py`)

#### Connection Sequence
```python
def main():
    # 1. Initial connection and ping
    # 2. Authentication handshake
    # 3. Start background threads
    # 4. Enter message input loop
```

#### Thread Responsibilities
- **Main Thread**: User input and message sending
- **Heartbeat Thread**: Respond to server health checks
- **Message Thread**: Receive and display incoming messages

### Database Layer (`db.py`)

#### Message Storage Format
```
{id};{timestamp};{username};{message_content}
```

#### Key Functions
- **Storage**: Append-only message logging
- **Retrieval**: ID-based and time-based queries
- **Parsing**: Extract components from message records
- **Validation**: Type checking and format verification

### C Library Integration (`16.c`, `c16.py`)

#### Encoding Algorithm
```c
// Character to two-character encoding
char* encode_B(char* in) {
    // Split byte into nibbles
    // Add 'A' offset for ASCII representation
    // Return allocated string
}
```

#### Python Interface
```python
# Load platform-appropriate library
c16 = ctypes.CDLL("./lib16.so")  # Linux
c16 = ctypes.CDLL("./16.dll")    # Windows

# Configure return types
c16.encode_B.restype = ctypes.c_char_p
c16.decode_B.restype = ctypes.c_char_p
```

## Development Workflows

### Adding New Features

#### 1. Protocol Extension
```python
# Define new port and message format
NEW_FEATURE_PORT = 11000

# Update server.py
def handle_new_feature(client):
    # Implementation here
    pass

# Update comms.py
def use_new_feature():
    # Client-side implementation
    pass
```

#### 2. Database Schema Changes
```python
# Update db.py parsing functions
def fetch_new_field(message):
    # Extract new field from message
    pass

# Update message format
def add_message(time, user, message, new_field):
    # Include new field in storage
    pass
```

#### 3. C Library Extensions
```c
// Add new function to 16.c
char* new_encoding_function(char* input) {
    // Implementation
    return result;
}
```

```python
# Update c16.py interface
c16.new_encoding_function.restype = ctypes.c_char_p
```

### Testing Strategies

#### Unit Testing
```python
# test/test_db.py
import unittest
from src.Server import db

class TestDatabase(unittest.TestCase):
    def test_message_validation(self):
        valid_msg = "1;1234567890.123;user;Hello"
        self.assertTrue(db.validate_message(valid_msg))
        
    def test_message_parsing(self):
        msg = "1;1234567890.123;user;Hello"
        self.assertEqual(db.fetch_user(msg), "user")
```

#### Integration Testing
```python
# test/test_integration.py
def test_client_server_communication():
    # Start server in background
    # Connect client
    # Send test message
    # Verify message received
    pass
```

#### Load Testing
```python
# test/test_load.py
def test_multiple_clients():
    # Spawn multiple client threads
    # Send concurrent messages
    # Verify all messages received
    # Check server stability
    pass
```

### Debugging Techniques

#### Server Debugging
```python
# Enable debug mode in server.py
debug = 1

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Client {client} connected")
```

#### Client Debugging
```python
# Add debug prints in comms.py
print(f"Sending message: {message}")
print(f"Received: {messages}")
```

#### Network Debugging
```bash
# Monitor network traffic
sudo tcpdump -i lo port 10740

# Check port usage
netstat -tulpn | grep python
```

## Plugin Development

### Server Plugins (`src/Server/mods/`)

#### Plugin Template
```python
# mods/example_plugin.py
def on_client_connect(client_ip):
    """Called when client connects"""
    print(f"Plugin: Client {client_ip} connected")

def on_message_received(client_ip, message):
    """Called when message received"""
    # Process message
    return message  # Return modified message or None to block

def on_client_disconnect(client_ip):
    """Called when client disconnects"""
    print(f"Plugin: Client {client_ip} disconnected")
```

#### Plugin Loading
```python
# server.py automatically loads plugins
def load_mods():
    for file in os.listdir("mods"):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            importlib.import_module(f"mods.{module_name}")
```

### Client Plugins (`src/Client/mods/`)

#### Client Plugin Template
```python
# mods/client_plugin.py
def on_message_display(username, message):
    """Called before displaying message"""
    # Modify display format
    return f"[{username}]: {message}"

def on_message_send(message):
    """Called before sending message"""
    # Modify outgoing message
    return message.upper()  # Example: convert to uppercase
```

## Performance Optimization

### Server Optimization

#### Connection Handling
```python
# Increase socket backlog for high concurrency
server_socket.listen(100)  # Default is 5

# Use connection pooling
connection_pool = []
```

#### Memory Management
```python
# Limit message history
MAX_MESSAGES = 10000

def cleanup_old_messages():
    # Remove messages older than threshold
    pass
```

#### Threading Optimization
```python
# Use thread pools instead of unlimited threads
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=50)
```

### Client Optimization

#### Message Caching
```python
# Cache recent messages for faster display
message_cache = []

def cache_message(message):
    message_cache.append(message)
    if len(message_cache) > 100:
        message_cache.pop(0)
```

#### Connection Management
```python
# Implement connection retry logic
def connect_with_retry(host, port, max_retries=3):
    for attempt in range(max_retries):
        try:
            return socket.connect((host, port))
        except ConnectionRefusedError:
            time.sleep(2 ** attempt)  # Exponential backoff
    raise ConnectionError("Max retries exceeded")
```

## Security Considerations

### Input Validation
```python
def sanitize_message(message):
    # Remove dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'"]
    for char in dangerous_chars:
        message = message.replace(char, '')
    return message
```

### Authentication Enhancement
```python
# Implement proper authentication
import hashlib
import secrets

def generate_auth_token():
    return secrets.token_hex(32)

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', 
                              password.encode(), 
                              salt.encode(), 
                              100000)
```

### Network Security
```python
# Add SSL/TLS support
import ssl

def create_secure_socket():
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_sock = context.wrap_socket(sock)
    return secure_sock
```

## Code Style Guidelines

### Python Style (PEP 8)
```python
# Use descriptive variable names
client_socket = socket.socket()  # Good
s = socket.socket()              # Bad

# Function documentation
def authenticate_client(client_ip: str) -> bool:
    """
    Authenticate a client connection.
    
    Args:
        client_ip: IP address of the client
        
    Returns:
        True if authentication successful, False otherwise
    """
    pass
```

### C Style
```c
// Use consistent indentation
char* encode_character(char* input) {
    char* output = malloc(3);
    if (output == NULL) {
        return NULL;  // Handle allocation failure
    }
    
    // Implementation here
    return output;
}
```

### Error Handling
```python
# Always handle exceptions appropriately
try:
    client_socket.connect((host, port))
except ConnectionRefusedError:
    logging.error(f"Cannot connect to {host}:{port}")
    return False
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    return False
```

## Deployment Considerations

### Production Deployment
```python
# Use proper logging instead of print statements
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
```

### Configuration Management
```python
# Use configuration files
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('server', 'host', fallback='127.0.0.1')
PORT = config.getint('server', 'port', fallback=10740)
```

### Monitoring and Metrics
```python
# Add metrics collection
import time

class Metrics:
    def __init__(self):
        self.connections = 0
        self.messages_sent = 0
        self.start_time = time.time()
    
    def uptime(self):
        return time.time() - self.start_time
```

## Contributing Guidelines

### Code Review Process
1. Create feature branch from main
2. Implement changes with tests
3. Run linting and type checking
4. Submit pull request with description
5. Address review feedback
6. Merge after approval

### Documentation Requirements
- Update API documentation for new functions
- Add examples for new features
- Update installation guide if dependencies change
- Include troubleshooting information

### Testing Requirements
- Unit tests for all new functions
- Integration tests for protocol changes
- Load testing for performance improvements
- Regression testing for bug fixes

This development guide provides the foundation for understanding and extending the General Communications system. For specific implementation details, refer to the source code and API documentation.