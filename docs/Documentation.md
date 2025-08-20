# Documentation

This documentation covers the General Communications system architecture, development guidelines, and implementation details.

## Development Stack

### Primary Languages
- **Python**: Main application logic for both client and server
- **C**: Low-level encoding/decoding operations for performance
- **C++**: Alternative communication implementations (experimental)

### Key Dependencies
- **threading**: Multi-threaded client handling
- **socket**: Network communication
- **ctypes**: Python-C library integration
- **prompt_toolkit**: Enhanced CLI input handling

## Architecture Overview

### Server Architecture
The server uses a multi-threaded design with separate threads for:
- **Client acceptance**: Main thread accepting new connections
- **Authentication**: Secure client verification process
- **Heartbeat monitoring**: Client health checking
- **Message handling**: Receiving and broadcasting messages
- **Database operations**: Message persistence

### Client Architecture
The client implements:
- **Connection management**: Multi-stage authentication process
- **Message sending**: Interactive message composition
- **Message receiving**: Real-time message display
- **Heartbeat response**: Server health monitoring

### Database Schema
Messages are stored in a semicolon-delimited format:
```
{id};{timestamp};{username};{message_content}
```

## Key Functions

### Server Functions
- `acception()`: Main client acceptance loop
- `authentication(client)`: Client authentication process
- `heartbeat(client)`: Client health monitoring
- `listen_messages(client)`: Message reception handling
- `send_messages(client, timed)`: Message delivery to clients

### Client Functions
- `main()`: Connection and authentication sequence
- `heartbeat()`: Server health response
- `fetch_messages()`: Message reception and display
- `send_message()`: Interactive message sending

### Database Functions
- `add_message(time, user, message)`: Store new message
- `fetch_message(message)`: Extract message content
- `fetch_user(message)`: Extract username
- `validate_message(message)`: Message format validation

### C Library Functions
- `encode_B(char* in)`: Encode single character to two-character format
- `decode_B(char* in)`: Decode two-character format to single character
- `pairint(pair in)`: Convert character pair to integer
- `intpair(int in)`: Convert integer to character pair

## Development Guidelines

### Code Style
- Use descriptive variable names
- Implement proper error handling
- Add threading safety for shared resources
- Follow Python PEP 8 conventions

### Testing
- Test client-server communication thoroughly
- Verify authentication sequences
- Test message encoding/decoding
- Validate database operations

### Security Considerations
- Implement proper input validation
- Use secure authentication methods
- Sanitize message content
- Handle connection timeouts gracefully

## Extending the System

### Adding New Features
1. Update protocol documentation
2. Implement server-side handling
3. Add client-side functionality
4. Update database schema if needed
5. Test thoroughly with multiple clients

### Modular Extensions
The system supports modular extensions through the `mods/` directory. Create new Python modules to extend functionality without modifying core code.

## Basics
For getting started information, see [Basics.md](./Basics.md)