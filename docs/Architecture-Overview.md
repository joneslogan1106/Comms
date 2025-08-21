# Architecture Overview

This document provides a comprehensive overview of the General Communications system architecture, design decisions, and system interactions.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Client A    │    │     Client B    │    │     Client N    │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   comms.py  │ │    │ │   comms.py  │ │    │ │   comms.py  │ │
│ │             │ │    │ │             │ │    │ │             │ │
│ │ ┌─────────┐ │ │    │ │ ┌─────────┐ │ │    │ │ ┌─────────┐ │ │
│ │ │UI Thread│ │ │    │ │ │UI Thread│ │ │    │ │ │UI Thread│ │ │
│ │ └─────────┘ │ │    │ │ └─────────┘ │ │    │ │ └─────────┘ │ │
│ │ ┌─────────┐ │ │    │ │ ┌─────────┐ │ │    │ │ ┌─────────┐ │ │
│ │ │Heartbeat│ │ │    │ │ │Heartbeat│ │ │    │ │ │Heartbeat│ │ │
│ │ │ Thread  │ │ │    │ │ │ Thread  │ │ │    │ │ │ Thread  │ │ │
│ │ └─────────┘ │ │    │ │ └─────────┘ │ │    │ │ └─────────┘ │ │
│ │ ┌─────────┐ │ │    │ │ ┌─────────┐ │ │    │ │ ┌─────────┐ │ │
│ │ │Message  │ │ │    │ │ │Message  │ │ │    │ │ │Message  │ │ │
│ │ │Receiver │ │ │    │ │ │Receiver │ │ │    │ │ │Receiver │ │ │
│ │ └─────────┘ │ │    │ │ └─────────┘ │ │    │ │ └─────────┘ │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌────┴───────────────────────┴───────────────────────┴────┐
    │                                                         │
    │                    Network Layer                        │
    │         (TCP Sockets on Multiple Ports)                 │
    │                                                         │
    └────┬───────────────────────┬───────────────────────┬────┘
         │                       │                       │
┌─────────────────────────────────────────────────────────────────┐
│                         Server                                  │
│                                                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│ │  server.py  │  │    db.py    │  │   c16.py    │              │
│ │             │  │             │  │             │              │
│ │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │              │
│ │ │Main     │ │  │ │Message  │ │  │ │C Library│ │              │
│ │ │Accept   │ │  │ │Storage  │ │  │ │Interface│ │              │
│ │ │Thread   │ │  │ │         │ │  │ │         │ │              │
│ │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │              │
│ │ ┌─────────┐ │  │ ┌─────────┐ │  │             │              │
│ │ │Auth     │ │  │ │Message  │ │  │             │              │
│ │ │Threads  │ │  │ │Parsing  │ │  │             │              │
│ │ │(Per     │ │  │ │         │ │  │             │              │
│ │ │Client)  │ │  │ └─────────┘ │  │             │              │
│ │ └─────────┘ │  │ ┌─────────┐ │  │             │              │
│ │ ┌─────────┐ │  │ │Message  │ │  │             │              │
│ │ │Heartbeat│ │  │ │Validation│ │  │             │              │
│ │ │Threads  │ │  │ │         │ │  │             │              │
│ │ │(Per     │ │  │ └─────────┘ │  │             │              │
│ │ │Client)  │ │  │             │  │             │              │
│ │ └─────────┘ │  │             │  │             │              │
│ │ ┌─────────┐ │  │             │  │             │              │
│ │ │Message  │ │  │             │  │             │              │
│ │ │Listener │ │  │             │  │             │              │
│ │ │Threads  │ │  │             │  │             │              │
│ │ │(Per     │ │  │             │  │             │              │
│ │ │Client)  │ │  │             │  │             │              │
│ │ └─────────┘ │  │             │  │             │              │
│ └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                    Database Layer                           │ │
│ │                                                             │ │
│ │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │ │
│ │  │database.db  │    │usernames.db │    │   16.c      │     │ │
│ │  │             │    │             │    │             │     │ │
│ │  │Message      │    │User         │    │Encoding/    │     │ │
│ │  │Storage      │    │Credentials  │    │Decoding     │     │ │
│ │  │             │    │             │    │Functions    │     │ │
│ │  └─────────────┘    └─────────────┘    └─────────────┘     │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Client Components
- **Main Thread**: User interface and message input
- **Heartbeat Thread**: Responds to server health checks
- **Message Receiver Thread**: Handles incoming message display
- **Database Interface**: Local message caching (optional)

#### Server Components
- **Main Accept Thread**: Accepts new client connections
- **Authentication Threads**: Handle client authentication (one per client)
- **Heartbeat Threads**: Monitor client health (one per client)
- **Message Listener Threads**: Receive messages from clients (one per client)
- **Database Layer**: Message storage and retrieval
- **C Library Interface**: High-performance encoding/decoding

## Communication Protocol

### Port Allocation Strategy

| Port  | Purpose           | Direction        | Connection Type | Lifecycle |
|-------|-------------------|------------------|-----------------|-----------|
| 10740 | Initial Connect   | Client → Server  | Short-lived     | Per connection attempt |
| 9281  | Authentication    | Client → Server  | Short-lived     | Per authentication |
| 12090 | Auth Callback     | Server → Client  | Short-lived     | Per authentication |
| 8070  | Heartbeat         | Server → Client  | Short-lived     | Periodic |
| 6090  | Message Delivery  | Server → Client  | Short-lived     | Per message batch |
| 9980  | Message Sending   | Client → Server  | Short-lived     | Per message |

### Protocol State Machine

```
Client State Machine:
┌─────────────┐    connect(10740)    ┌─────────────┐
│ DISCONNECTED│ ──────────────────→  │ CONNECTING  │
└─────────────┘                      └─────────────┘
                                            │
                                            │ ping/pong
                                            ▼
                                     ┌─────────────┐
                                     │ CONNECTED   │
                                     └─────────────┘
                                            │
                                            │ auth_request(9281)
                                            ▼
                                     ┌─────────────┐
                                     │AUTHENTICATING│
                                     └─────────────┘
                                            │
                                            │ auth_callback(12090)
                                            ▼
                                     ┌─────────────┐
                                     │AUTHENTICATED│
                                     └─────────────┘
                                            │
                                            │ start_threads()
                                            ▼
                                     ┌─────────────┐
                                     │   ACTIVE    │
                                     └─────────────┘

Server State Machine (per client):
┌─────────────┐   accept_connection  ┌─────────────┐
│   WAITING   │ ──────────────────→  │  CONNECTED  │
└─────────────┘                      └─────────────┘
                                            │
                                            │ authenticate()
                                            ▼
                                     ┌─────────────┐
                                     │AUTHENTICATING│
                                     └─────────────┘
                                            │
                                            │ auth_success
                                            ▼
                                     ┌─────────────┐
                                     │AUTHENTICATED│
                                     └─────────────┘
                                            │
                                            │ spawn_threads()
                                            ▼
                                     ┌─────────────┐
                                     │   ACTIVE    │
                                     └─────────────┘
```

## Data Flow Architecture

### Message Flow

```
1. Message Input (Client)
   │
   ▼
2. Message Validation & Formatting
   │
   ▼
3. Send to Server (Port 9980)
   │
   ▼
4. Server Receives & Validates
   │
   ▼
5. Store in Database
   │
   ▼
6. Add to Broadcast Queue
   │
   ▼
7. Heartbeat Triggers Message Check
   │
   ▼
8. Send to All Clients (Port 6090)
   │
   ▼
9. Client Receives & Displays
```

### Authentication Flow

```
Client                           Server
  │                               │
  │ 1. Connect(10740)             │
  │ ─────────────────────────────→│
  │                               │
  │ 2. "Ping"                     │
  │ ─────────────────────────────→│
  │                               │
  │ 3. "Pong"                     │
  │ ←─────────────────────────────│
  │                               │
  │ 4. Connect(9281)              │
  │ ─────────────────────────────→│
  │                               │
  │ 5. "AuthRequest"              │
  │ ─────────────────────────────→│
  │                               │
  │ 6. "Auth1"                    │
  │ ←─────────────────────────────│
  │                               │
  │ 7. Listen(12090)              │
  │                               │
  │ 8. Connect(client:12090)      │
  │ ←─────────────────────────────│
  │                               │
  │ 9. "Authed"                   │
  │ ←─────────────────────────────│
  │                               │
  │ 10. Start Threads             │
  │                               │
```

## Threading Architecture

### Server Threading Model

```
Main Process
├── Main Thread (Connection Acceptance)
│   └── accept() loop on port 10740
│
├── Per-Client Thread Pool
│   ├── Authentication Thread (per connecting client)
│   │   ├── Handle auth handshake
│   │   └── Spawn operational threads on success
│   │
│   ├── Heartbeat Thread (per active client)
│   │   ├── Connect to client:8070
│   │   ├── Send ping, receive timestamp
│   │   └── Trigger message delivery
│   │
│   └── Message Listener Thread (per active client)
│       ├── Listen on port 9980
│       ├── Receive client messages
│       └── Store in database
│
└── Utility Threads
    ├── Signal Handler (SIGINT cleanup)
    ├── Module Loader (plugin system)
    └── Database Maintenance (optional)
```

### Client Threading Model

```
Main Process
├── Main Thread (User Interface)
│   ├── Message input loop
│   ├── Send messages to server
│   └── Handle user commands
│
├── Heartbeat Thread
│   ├── Listen on port 8070
│   ├── Respond to server pings
│   └── Send current timestamp
│
└── Message Receiver Thread
    ├── Listen on port 6090
    ├── Receive message batches
    └── Display messages to user
```

## Database Architecture

### Message Storage Schema

```sql
-- Conceptual SQL representation of flat-file format
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    timestamp REAL NOT NULL,
    username TEXT NOT NULL,
    message TEXT NOT NULL
);

-- Actual flat-file format:
-- {id};{timestamp};{username};{message_content}
-- Example: 1;1640995200.123;alice;Hello, world!
```

### Database Operations

#### Write Operations
- **Append-only**: New messages always appended to end of file
- **Atomic writes**: Single write operation per message
- **No transactions**: Simple file I/O for reliability
- **Auto-increment ID**: Global counter for message IDs

#### Read Operations
- **Sequential scan**: Read entire file for message retrieval
- **Time-based filtering**: Filter messages by timestamp
- **Parse on read**: Extract fields during retrieval
- **No indexing**: Simple linear search through messages

### Data Consistency

#### Concurrency Control
- **File locking**: OS-level file locking for write operations
- **Read-while-write**: Readers can access file during writes
- **No corruption protection**: Relies on OS atomic write guarantees
- **Manual recovery**: Corrupted files require manual intervention

## Security Architecture

### Current Security Model

#### Authentication
- **Minimal authentication**: Basic handshake without credentials
- **IP-based identification**: Clients identified by IP address
- **No encryption**: All communication in plaintext
- **No authorization**: All authenticated clients have equal access

#### Network Security
- **Multiple ports**: Increases attack surface
- **No rate limiting**: Vulnerable to DoS attacks
- **No input validation**: Accepts arbitrary message content
- **No session management**: No concept of user sessions

### Security Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    Network Boundary                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                Application Boundary                     ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │              Process Boundary                       │││
│  │  │  ┌─────────────────────────────────────────────────┐│││
│  │  │  │            Thread Boundary                      ││││
│  │  │  │                                                 ││││
│  │  │  │  Client Threads ←→ Server Threads               ││││
│  │  │  │                                                 ││││
│  │  │  └─────────────────────────────────────────────────┘│││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘

Trust Levels:
- Network: Untrusted (plaintext, no authentication)
- Application: Partially trusted (basic handshake)
- Process: Trusted (same process space)
- Thread: Trusted (shared memory space)
```

## Performance Characteristics

### Scalability Limits

#### Current Bottlenecks
1. **Thread-per-client model**: Limited by OS thread limits (~1000-5000)
2. **Synchronous I/O**: Blocking operations limit throughput
3. **File-based database**: Sequential access limits query performance
4. **No connection pooling**: New connections for each operation
5. **No message batching**: Individual network operations per message

#### Performance Metrics
- **Connection setup time**: ~10-50ms per client
- **Message latency**: ~5-20ms end-to-end
- **Throughput**: ~100-500 messages/second
- **Memory usage**: ~1-5MB per connected client
- **CPU usage**: ~1-5% per 10 connected clients

### Optimization Opportunities

#### Short-term Improvements
1. **Connection reuse**: Maintain persistent connections
2. **Message batching**: Group multiple messages per transmission
3. **Async I/O**: Use asyncio for non-blocking operations
4. **Database indexing**: Add timestamp-based indexing
5. **Input validation**: Sanitize and validate all inputs

#### Long-term Improvements
1. **Event-driven architecture**: Replace threading with event loops
2. **Database migration**: Move to proper database system
3. **Protocol optimization**: Reduce number of required ports
4. **Caching layer**: Add in-memory message caching
5. **Load balancing**: Support multiple server instances

## Extension Points

### Plugin Architecture

#### Server Extensions (`src/Server/mods/`)
```python
# Plugin interface
class ServerPlugin:
    def on_client_connect(self, client_ip):
        """Called when client connects"""
        pass
    
    def on_message_received(self, client_ip, message):
        """Called when message received"""
        return message  # Can modify or block message
    
    def on_client_disconnect(self, client_ip):
        """Called when client disconnects"""
        pass
```

#### Client Extensions (`src/Client/mods/`)
```python
# Plugin interface
class ClientPlugin:
    def on_message_display(self, username, message):
        """Called before displaying message"""
        return f"[{username}]: {message}"  # Can modify display
    
    def on_message_send(self, message):
        """Called before sending message"""
        return message  # Can modify outgoing message
```

### Integration Points

#### C Library Extensions
- **Custom encoding**: Implement new encoding algorithms
- **Performance optimization**: Add SIMD or GPU acceleration
- **Compression**: Add message compression support
- **Encryption**: Add cryptographic functions

#### Database Extensions
- **Multiple backends**: Support different storage systems
- **Replication**: Add database replication support
- **Backup**: Implement automated backup systems
- **Migration**: Support schema migrations

#### Network Extensions
- **Protocol variants**: Support different network protocols
- **Encryption**: Add TLS/SSL support
- **Compression**: Add network-level compression
- **Multiplexing**: Support connection multiplexing

## Design Decisions and Rationale

### Architecture Decisions

#### Multi-Port Design
**Decision**: Use separate ports for different communication types
**Rationale**: 
- Clear separation of concerns
- Easier debugging and monitoring
- Protocol flexibility
**Trade-offs**: 
- Increased complexity
- More firewall configuration
- Higher resource usage

#### Thread-per-Client Model
**Decision**: Create dedicated threads for each client
**Rationale**:
- Simple programming model
- Good isolation between clients
- Easy to understand and debug
**Trade-offs**:
- Limited scalability
- Higher memory usage
- Context switching overhead

#### Flat-File Database
**Decision**: Use simple text file for message storage
**Rationale**:
- No external dependencies
- Easy to inspect and debug
- Simple backup and recovery
**Trade-offs**:
- Poor query performance
- No ACID properties
- Limited concurrent access

#### Custom Protocol
**Decision**: Implement custom TCP-based protocol
**Rationale**:
- Full control over communication
- Optimized for specific use case
- Learning opportunity
**Trade-offs**:
- More development effort
- Potential security issues
- Compatibility challenges

### Future Architecture Evolution

#### Phase 1: Stability and Security
- Add proper authentication and authorization
- Implement input validation and sanitization
- Add comprehensive error handling
- Improve logging and monitoring

#### Phase 2: Performance and Scalability
- Migrate to async I/O model
- Implement connection pooling
- Add message batching and caching
- Optimize database operations

#### Phase 3: Features and Integration
- Add file transfer capabilities
- Implement user management system
- Add plugin system enhancements
- Support multiple server instances

#### Phase 4: Production Readiness
- Add comprehensive testing suite
- Implement deployment automation
- Add monitoring and alerting
- Create administration tools

This architecture overview provides a comprehensive understanding of the General Communications system design, implementation, and evolution path. It serves as a foundation for development, optimization, and extension efforts.