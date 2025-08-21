# API Reference

This document provides a comprehensive reference for all functions, classes, and modules in the General Communications system.

## Server API (`src/Server/`)

### server.py

#### Core Functions

##### `acception()`
Main server loop that accepts incoming client connections.
- **Returns**: None
- **Threading**: Runs in main thread
- **Purpose**: Continuously listens for new client connections on port 10740

##### `authentication(client)`
Handles the multi-stage authentication process for a client.
- **Parameters**: 
  - `client` (str): Client IP address
- **Returns**: None
- **Threading**: Spawns new thread per client
- **Ports Used**: 9281 (incoming), 12090 (outgoing)

##### `heartbeat(client)`
Monitors client health and synchronizes message delivery.
- **Parameters**:
  - `client` (str): Client IP address
- **Returns**: None
- **Threading**: Runs in dedicated thread per client
- **Timeout**: 5 seconds
- **Port**: 8070

##### `listen_messages(client)`
Listens for incoming messages from a specific client.
- **Parameters**:
  - `client` (str): Client IP address
- **Returns**: None
- **Threading**: Runs in dedicated thread per client
- **Port**: 9980

##### `send_messages(client, timed)`
Sends new messages to a client based on timestamp.
- **Parameters**:
  - `client` (str): Client IP address
  - `timed` (float): Timestamp threshold for new messages
- **Returns**: None
- **Port**: 6090

#### Utility Functions

##### `glue(i, s=" ")`
Joins list elements with a separator.
- **Parameters**:
  - `i` (list): List of strings to join
  - `s` (str): Separator string (default: " ")
- **Returns**: str

##### `fix_string(i)`
Escapes special characters in message strings.
- **Parameters**:
  - `i` (str): Input string
- **Returns**: str with escaped characters
- **Escapes**: `\n` → `\\n`, `\` → `\\\\`

#### Global Variables

- `exiting` (bool): Server shutdown flag
- `clients` (list): Active client IP addresses
- `debug` (int): Debug output level (0=off, 1=on)
- `server_sockets` (list): Active server socket objects

### db.py (Server Database Operations)

#### Message Operations

##### `add_message(time, user, message)`
Stores a new message in the database.
- **Parameters**:
  - `time` (float): Unix timestamp
  - `user` (str): Username
  - `message` (str): Message content
- **Returns**: None
- **File**: Appends to `database.db`

##### `remove_message(i)`
Removes a message by ID from the database.
- **Parameters**:
  - `i` (int): Message ID
- **Returns**: None
- **File**: Rewrites `database.db`

##### `fetch_message(i)`
Retrieves a message by ID.
- **Parameters**:
  - `i` (int): Message ID
- **Returns**: str (message record) or -1 if not found

#### Message Parsing

##### `fetch_message(message)`
Extracts message content from database record.
- **Parameters**:
  - `message` (str): Database record
- **Returns**: str (message content)

##### `fetch_time(message)`
Extracts timestamp from database record.
- **Parameters**:
  - `message` (str): Database record
- **Returns**: float (Unix timestamp)

##### `fetch_user(message)`
Extracts username from database record.
- **Parameters**:
  - `message` (str): Database record
- **Returns**: str (username)

##### `fetch_id(message)`
Extracts message ID from database record.
- **Parameters**:
  - `message` (str): Database record
- **Returns**: int (message ID)

##### `validate_message(i)`
Validates message format and data types.
- **Parameters**:
  - `i` (str): Message record
- **Returns**: bool (True if valid)
- **Format**: `{id};{timestamp};{username};{message}`

### c16.py (C Library Interface)

#### Library Loading
Automatically loads platform-appropriate C library:
- Windows: `16.dll`
- Linux/Unix: `lib16.so`

#### Available Functions
- `c16.encode_B(char*)`: Encode single character
- `c16.decode_B(char*)`: Decode character pair
- Both functions return `ctypes.c_char_p`

## Client API (`src/Client/`)

### comms.py

#### Core Functions

##### `main()`
Main client connection and authentication sequence.
- **Returns**: None
- **Ports**: Connects to 10740, 9281
- **Threading**: Spawns heartbeat and message receiver threads

##### `heartbeat()`
Responds to server heartbeat requests.
- **Returns**: None
- **Port**: 8070 (listening)
- **Response**: Current timestamp as float

##### `fetch_messages()`
Receives and displays messages from server.
- **Returns**: None
- **Port**: 6090 (listening)
- **Threading**: Runs in dedicated thread

##### `send_message()`
Interactive message composition and sending.
- **Returns**: None
- **Port**: 9980 (connects to server)
- **Input**: Multi-line support via prompt_toolkit

#### Utility Functions

##### `unfix_message(i)`
Unescapes special characters in received messages.
- **Parameters**:
  - `i` (str): Escaped message string
- **Returns**: str with unescaped characters
- **Unescapes**: `\\n` → `\n`, `\\\\` → `\`

#### Global Variables

- `past_time` (float): Last heartbeat timestamp
- `session` (PromptSession): prompt_toolkit session object
- `username` (str): Client username (default: "Bob")

## C Library API (`src/Server/16.c`)

### Data Structures

#### `pair`
Structure for character pair operations.
```c
typedef struct {
    char A;
    char B;
} pair;
```

### Encoding Functions

#### `char* encode_B(char* in)`
Encodes a single character into two-character format.
- **Parameters**: `in` - Input character pointer
- **Returns**: Allocated string with encoded result
- **Algorithm**: Splits byte into nibbles, adds 'A' offset
- **Memory**: Caller must free returned pointer

#### `char* decode_B(char* in)`
Decodes two-character format back to single character.
- **Parameters**: `in` - Two-character encoded input
- **Returns**: Allocated string with decoded result
- **Algorithm**: Subtracts 'A' offset, combines nibbles
- **Memory**: Caller must free returned pointer

### Utility Functions

#### `int pairint(pair in)`
Converts character pair to integer.
- **Parameters**: `in` - Character pair structure
- **Returns**: Integer representation

#### `pair intpair(int in)`
Converts integer to character pair.
- **Parameters**: `in` - Integer value
- **Returns**: Character pair structure

## Error Handling

### Common Exceptions

#### Network Errors
- `ConnectionRefusedError`: Client unavailable
- `TimeoutError`: Connection timeout (5s default)
- `BrokenPipeError`: Connection terminated
- `ConnectionResetError`: Forceful disconnection

#### Data Errors
- `ValueError`: Invalid data type conversion
- `KeyError`: Missing dictionary key
- `IndexError`: List/string index out of range

### Error Recovery
- Automatic client cleanup on connection errors
- Graceful degradation for invalid messages
- Timeout handling for all network operations

## Threading Model

### Server Threads
- **Main Thread**: Client acceptance loop
- **Per-Client Threads**:
  - Authentication handler
  - Heartbeat monitor
  - Message listener
  - Message sender (on-demand)

### Client Threads
- **Main Thread**: User input and message sending
- **Heartbeat Thread**: Server health response
- **Message Receiver Thread**: Incoming message display

## Database Schema

### Message Format
```
{id};{timestamp};{username};{message_content}
```

### Field Specifications
- **id**: Sequential integer, auto-increment
- **timestamp**: Unix timestamp, float precision
- **username**: String identifier, no semicolons
- **message_content**: Escaped string content

### File Locations
- Server: `src/Server/database.db`
- Client: `src/Client/cdatabase.db`

## Configuration

### Port Configuration
All ports are hardcoded in source files:
- Modify server.py and comms.py to change port assignments
- Ensure firewall allows traffic on all required ports

### Debug Mode
Set `debug = 1` in server.py for verbose output:
- Client connection status
- Authentication progress
- Message handling details

### Platform-Specific Settings
- C library compilation flags vary by platform
- Socket options may need adjustment for different OS
- File paths use forward slashes (cross-platform compatible)