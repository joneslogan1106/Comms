# General Communications Protocol Specification

## Protocol Overview

The General Communications Protocol implements a multi-port, multi-stage communication system for real-time messaging. The protocol uses TCP sockets and implements custom authentication, heartbeat monitoring, and message delivery mechanisms.

## Port Allocation

| Port  | Purpose | Direction | Description |
|-------|---------|-----------|-------------|
| 10740 | Main Connection | Client → Server | Initial client connection and ping |
| 9281  | Authentication | Client → Server | Authentication handshake |
| 12090 | Auth Callback | Server → Client | Server authentication confirmation |
| 8070  | Heartbeat | Server → Client | Health monitoring |
| 6090  | Message Delivery | Server → Client | Message broadcasting |
| 9980  | Message Sending | Client → Server | Message submission |

## Connection Sequence

### 1. Initial Connection (Port 10740)
- Client connects to server
- Client sends "Ping" message
- Server responds with "Pong"
- Connection establishes basic communication

### 2. Authentication (Port 9281)
- Client connects to authentication port
- Client sends "AuthRequest"
- Server responds with "Auth1"
- Server initiates callback to client

### 3. Authentication Callback (Port 12090)
- Server connects back to client
- Server sends "Authed" confirmation
- Full authentication completed
- Client threads start

## Heartbeat Protocol (Port 8070)

### Purpose
Monitor client health and synchronize message delivery timing.

### Process
1. Server connects to client heartbeat port
2. Server sends "Ping" message
3. Client responds with current timestamp (float)
4. Server uses timestamp to determine new messages to send
5. Connection closes after each heartbeat

### Timeout Handling
- 5-second connection timeout
- Client removal on connection failure
- Automatic cleanup of disconnected clients

## Message Protocols

### Message Sending (Port 9980)
**Client to Server**

#### Format
```
{username};{message_content}
```

#### Process
1. Client connects to server message port
2. Client sends formatted message
3. Server validates message format
4. Server stores message with timestamp and ID
5. Server responds with "Thx" confirmation

### Message Delivery (Port 6090)
**Server to Client**

#### Format
```
{id};{timestamp};{username};{message_content}
{id};{timestamp};{username};{message_content}
...
```

#### Process
1. Server connects to client delivery port
2. Server sends all new messages since last heartbeat
3. Client receives and displays messages
4. Connection closes after delivery

## Message Format Specification

### Database Storage Format
```
{id};{timestamp};{username};{message_content}
```

- **id**: Sequential integer identifier
- **timestamp**: Unix timestamp (float)
- **username**: Client identifier string
- **message_content**: Escaped message text

### Message Escaping
Special characters are escaped in message content:
- `\n` → `\\n` (newlines)
- `\` → `\\\\` (backslashes)

## Error Handling

### Connection Errors
- **ConnectionRefusedError**: Client removed from active list
- **TimeoutError**: Client marked as disconnected
- **BrokenPipeError**: Connection terminated, client cleanup
- **ConnectionResetError**: Client forcibly disconnected

### Data Validation
- Message format validation before storage
- Type checking for message components
- Input sanitization for security

## Security Considerations

### Authentication
- Multi-stage authentication process
- Server-initiated callback verification
- Connection timeout enforcement

### Input Validation
- Message format validation
- Type checking for all protocol fields
- Proper error handling for malformed data

## Encoding Protocol

### C Library Integration
The system uses a custom C library for character encoding:

#### Functions
- `encode_B(char* in)`: Encodes single character to two-character format
- `decode_B(char* in)`: Decodes two-character format back to single character

#### Format
- Input character split into nibbles
- Each nibble offset by 'A' (65) for ASCII representation
- Results in two-character encoded output

## Threading Model

### Server Threads
- **Main thread**: Client acceptance loop
- **Per-client threads**: 
  - Heartbeat monitoring
  - Message listening
  - Authentication handling

### Client Threads
- **Heartbeat thread**: Responds to server health checks
- **Message receiver thread**: Handles incoming messages
- **Main thread**: User input and message sending

## Protocol Extensions

The protocol supports modular extensions through:
- Plugin system in `mods/` directory
- Configurable port assignments
- Extensible message formats
- Custom authentication mechanisms