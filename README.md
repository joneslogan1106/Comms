# General Communications Protocol

A socket-based messaging system implementing a custom communication protocol for real-time messaging between clients and servers.

## Features

- **Real-time messaging**: Send and receive messages through socket connections
- **Multi-threaded architecture**: Concurrent handling of multiple clients
- **Custom encoding**: C-based encoding/decoding functions for data processing
- **Heartbeat monitoring**: Automatic client health checking and timeout handling
- **Database persistence**: Message storage and retrieval system
- **Cross-platform support**: Works on Linux and Windows systems

## Architecture

The system consists of three main components:

### Server (`src/Server/`)
- **server.py**: Main server application handling client connections, authentication, and message routing
- **db.py**: Database operations for message storage and retrieval
- **c16.py**: Python wrapper for C encoding/decoding functions
- **16.c**: C library providing encoding/decoding functionality

### Client (`src/Client/`)
- **comms.py**: Client application for connecting to server and sending/receiving messages
- **db.py**: Client-side database operations (shared with server)

### Components (`src/Components/`)
- **c16 components/**: Compiled C libraries for encoding/decoding operations

## Protocol Overview

The system uses multiple ports for different communication types:

- **Port 10740**: Main client connection and heartbeat
- **Port 9281**: Authentication handshake
- **Port 12090**: Server authentication callback
- **Port 8070**: Heartbeat monitoring
- **Port 6090**: Message delivery (server to client)
- **Port 9980**: Message sending (client to server)

## Quick Start

1. Start the server:
   ```bash
   cd src/Server
   python server.py
   ```

2. Connect a client:
   ```bash
   cd src/Client
   python comms.py
   ```

3. Start sending messages through the interactive prompt

## Documentation

For detailed information, see the [docs](./docs/) folder:
- [Basics](./docs/Basics.md) - Getting started guide
- [Protocol](./docs/Protocol.md) - Detailed protocol specification
- [Documentation](./docs/Documentation.md) - Development guidelines
