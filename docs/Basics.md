# Getting Started with General Communications

## Overview
This guide covers the essential information needed to understand, use, and modify the General Communications system. The system implements a custom socket-based messaging protocol designed for real-time communication between multiple clients and a central server.

## System Requirements

### Dependencies
- Python 3.6+ with threading support
- C compiler (gcc/clang) for building encoding libraries
- prompt_toolkit for enhanced CLI experience

### Platform Support
- Linux (primary platform)
- Windows (with appropriate DLL compilation)
- macOS (with shared library compilation)

## Quick Setup

### 1. Build C Libraries
```bash
# For Linux/macOS
cd src/Server
gcc -shared -fPIC -o lib16.so 16.c

# For Windows
cd src/Server
gcc -shared -o 16.dll 16.c
```

### 2. Start the Server
```bash
cd src/Server
python server.py
```

### 3. Connect Clients
```bash
cd src/Client
python comms.py
```

## Basic Usage

### Server Operations
- Automatically handles client connections
- Manages authentication sequences
- Monitors client health via heartbeats
- Stores and broadcasts messages
- Supports graceful shutdown (Ctrl+C)

### Client Operations
- Interactive message composition
- Real-time message display
- Automatic reconnection handling
- Multi-line message support

### Message Commands
- Press `Alt+Enter` or `Esc` then `Enter` for multi-line input
- Type messages and press Enter to send
- Messages appear in real-time for all connected clients

## Architecture Components

### Core Files
- **server.py**: Main server application
- **comms.py**: Client communication interface
- **db.py**: Database operations (shared between client/server)
- **c16.py**: Python wrapper for C encoding functions
- **16.c**: C library for character encoding/decoding

### Database Structure
Messages are stored in a simple flat-file database with the format:
```
{id};{timestamp};{username};{message}
```

### Network Protocol
The system uses 6 different ports for various communication types:
- Main connection and authentication
- Heartbeat monitoring
- Message sending and receiving

## Development Guidelines

### Code Organization
- Server code in `src/Server/`
- Client code in `src/Client/`
- Shared components in `src/Components/`
- Extensions in respective `mods/` directories

### Adding Features
1. Understand the existing protocol (see [Protocol.md](./Protocol.md))
2. Implement server-side changes first
3. Update client-side functionality
4. Test with multiple concurrent clients
5. Update documentation

### Common Modifications
- **GUI Development**: Extend the CLI client with graphical interfaces
- **File Transfer**: Add file sharing capabilities
- **Encryption**: Implement message encryption
- **User Management**: Add user registration and authentication
- **Message History**: Implement message persistence and search

## Troubleshooting

### Common Issues
- **Port conflicts**: Ensure ports 6090, 8070, 9281, 9980, 10740, 12090 are available
- **Library loading**: Verify C libraries are compiled for your platform
- **Connection timeouts**: Check firewall settings and network connectivity
- **Authentication failures**: Ensure proper connection sequence

### Debug Mode
Enable debug output in server.py by setting `debug = 1` to see client connection status.

## Extension Points

### Modular System
The system supports extensions through:
- Plugin modules in `mods/` directories
- Custom encoding/decoding functions
- Protocol extensions
- Database adapters

### API Integration
The core functions can be imported and used in other applications:
- Database operations from `db.py`
- Encoding functions from `c16.py`
- Network utilities from communication modules

## Next Steps

- Read the detailed [Protocol Specification](./Protocol.md)
- Review the [Development Documentation](./Documentation.md)
- Explore the source code structure
- Try building your first extension

For advanced usage and protocol details, see the comprehensive documentation in the other files in this directory.