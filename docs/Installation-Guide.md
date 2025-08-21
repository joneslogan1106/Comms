# Installation Guide

This guide provides step-by-step instructions for setting up the General Communications system on different platforms.

## System Requirements

### Minimum Requirements
- **Operating System**: Linux, Windows, or macOS
- **Python**: Version 3.6 or higher
- **Memory**: 256 MB RAM minimum
- **Storage**: 50 MB free disk space
- **Network**: TCP/IP networking capability

### Recommended Requirements
- **Python**: Version 3.8 or higher
- **Memory**: 512 MB RAM or more
- **CPU**: Multi-core processor for better threading performance
- **Network**: Gigabit Ethernet for high-throughput messaging

## Dependencies

### Python Packages
Install required Python packages using pip:

```bash
pip install prompt_toolkit
```

### System Dependencies

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip gcc build-essential
```

#### Linux (CentOS/RHEL/Fedora)
```bash
sudo yum install python3 python3-pip gcc gcc-c++ make
# or for newer versions:
sudo dnf install python3 python3-pip gcc gcc-c++ make
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Python (if not already installed)
brew install python3
```

#### Windows
1. Install Python from [python.org](https://python.org)
2. Install Microsoft Visual C++ Build Tools or Visual Studio
3. Ensure Python and pip are in your PATH

## Installation Steps

### 1. Clone or Download the Repository

#### Option A: Git Clone (Recommended)
```bash
git clone <repository-url>
cd general-communications
```

#### Option B: Download ZIP
1. Download the project ZIP file
2. Extract to your desired directory
3. Navigate to the extracted folder

### 2. Build C Libraries

The system requires compiled C libraries for encoding/decoding operations.

#### Linux/macOS
```bash
cd src/Server
gcc -shared -fPIC -o lib16.so 16.c
```

#### Windows (MinGW)
```bash
cd src/Server
gcc -shared -o 16.dll 16.c
```

#### Windows (Visual Studio)
```cmd
cd src\Server
cl /LD 16.c /Fe16.dll
```

### 3. Verify Installation

#### Test C Library Loading
```bash
cd src/Server
python3 c16.py
```

Expected output: Encoded character representation

#### Test Database Operations
```bash
cd src/Server
python3 db.py
```

Expected output: 
```
True
False
```

### 4. Configure Network Settings

#### Firewall Configuration

##### Linux (iptables)
```bash
# Allow required ports
sudo iptables -A INPUT -p tcp --dport 6090 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8070 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9281 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9980 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 10740 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 12090 -j ACCEPT
```

##### Linux (ufw)
```bash
sudo ufw allow 6090/tcp
sudo ufw allow 8070/tcp
sudo ufw allow 9281/tcp
sudo ufw allow 9980/tcp
sudo ufw allow 10740/tcp
sudo ufw allow 12090/tcp
```

##### Windows Firewall
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Create inbound rules for ports: 6090, 8070, 9281, 9980, 10740, 12090
4. Allow TCP connections for each port

##### macOS
```bash
# Add firewall rules if needed
sudo pfctl -f /etc/pf.conf
```

#### Network Interface Configuration
By default, the system binds to localhost (127.0.0.1). To allow external connections:

1. Edit server.py and change `HOST = "127.0.0.1"` to `HOST = "0.0.0.0"`
2. Edit comms.py and change server IP to your server's actual IP address

## First Run

### 1. Start the Server
```bash
cd src/Server
python3 server.py
```

Expected output:
```
[SERVER]: Starting General Communications Server
[SERVER]: Listening on port 10740
```

### 2. Connect a Client
Open a new terminal:
```bash
cd src/Client
python3 comms.py
```

Expected output:
```
Connected to server
Authentication successful
Enter message: 
```

### 3. Send Test Messages
1. Type a message in the client terminal
2. Press Enter to send
3. Message should appear in real-time
4. Try connecting multiple clients to test multi-user functionality

## Troubleshooting

### Common Installation Issues

#### "No module named 'prompt_toolkit'"
```bash
pip3 install prompt_toolkit
# or
python3 -m pip install prompt_toolkit
```

#### "gcc: command not found"
Install build tools for your platform (see System Dependencies above)

#### "Permission denied" on Linux/macOS
```bash
chmod +x src/Server/server.py
chmod +x src/Client/comms.py
```

#### C Library Compilation Errors

##### Linux: "cannot find -lc"
```bash
sudo apt install libc6-dev
# or
sudo yum install glibc-devel
```

##### Windows: "cl is not recognized"
Ensure Visual Studio Build Tools are installed and run from Developer Command Prompt

#### Port Already in Use
```bash
# Find process using port
sudo netstat -tulpn | grep :10740
# Kill process if needed
sudo kill -9 <PID>
```

### Runtime Issues

#### "Connection refused"
1. Verify server is running
2. Check firewall settings
3. Ensure correct IP address in client configuration

#### "Authentication failed"
1. Restart both server and client
2. Check network connectivity
3. Verify all required ports are open

#### Messages not appearing
1. Check client heartbeat thread is running
2. Verify message format in database
3. Restart client to refresh connection

## Advanced Configuration

### Custom Port Configuration
Edit the following files to change port assignments:
- `src/Server/server.py`: Server-side port definitions
- `src/Client/comms.py`: Client-side port definitions

### Database Location
Change database file paths in:
- `src/Server/db.py`: Server database location
- `src/Client/db.py`: Client database location

### Performance Tuning

#### Server Optimization
- Increase socket listen backlog for high-concurrency
- Adjust thread pool sizes for better resource management
- Enable debug mode only during development

#### Client Optimization
- Reduce heartbeat frequency for lower bandwidth usage
- Implement message caching for better responsiveness
- Use connection pooling for multiple client instances

### Security Hardening

#### Network Security
- Use VPN or SSH tunneling for remote connections
- Implement IP whitelisting in server code
- Enable SSL/TLS encryption (requires code modification)

#### System Security
- Run server with limited user privileges
- Restrict file system permissions on database files
- Monitor system logs for suspicious activity

## Deployment

### Production Deployment

#### Server Setup
1. Use a dedicated server or VPS
2. Configure automatic startup scripts
3. Set up log rotation and monitoring
4. Implement backup procedures for database files

#### Client Distribution
1. Package client with all dependencies
2. Create installation scripts for end users
3. Provide configuration templates
4. Document user setup procedures

### Docker Deployment (Optional)

Create a Dockerfile for containerized deployment:
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install prompt_toolkit
RUN gcc -shared -fPIC -o src/Server/lib16.so src/Server/16.c
EXPOSE 6090 8070 9281 9980 10740 12090
CMD ["python3", "src/Server/server.py"]
```

## Next Steps

After successful installation:
1. Read the [Basics Guide](./Basics.md) for usage instructions
2. Review the [Protocol Specification](./Protocol.md) for technical details
3. Explore the [API Reference](./API-Reference.md) for development
4. Check out [Development Guide](./Development-Guide.md) for customization

For additional help, refer to the troubleshooting section or check the project documentation.