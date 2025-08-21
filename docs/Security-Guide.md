# Security Guide

This document outlines security considerations, vulnerabilities, and hardening measures for the General Communications system.

## Current Security Status

### Security Assessment

#### ⚠️ Current Vulnerabilities
The system in its current state has several security limitations:

1. **No Authentication**: Clients can connect without credentials
2. **Plaintext Communication**: All messages sent in clear text
3. **No Input Validation**: Messages not sanitized for malicious content
4. **No Access Control**: All clients can send/receive all messages
5. **No Rate Limiting**: Susceptible to spam and DoS attacks
6. **Hardcoded Credentials**: Default username "Bob" for all clients

#### ✅ Existing Security Features
- Multi-stage connection process provides basic handshake verification
- Automatic client cleanup prevents resource exhaustion
- Thread isolation limits impact of client failures
- Database validation prevents some malformed data

## Threat Model

### Attack Vectors

#### Network-Based Attacks
1. **Man-in-the-Middle (MITM)**
   - **Risk**: High - All traffic is plaintext
   - **Impact**: Message interception and modification
   - **Mitigation**: Implement TLS/SSL encryption

2. **Denial of Service (DoS)**
   - **Risk**: Medium - No rate limiting
   - **Impact**: Server resource exhaustion
   - **Mitigation**: Connection limits and rate limiting

3. **Port Scanning**
   - **Risk**: Low - Multiple open ports
   - **Impact**: Service discovery
   - **Mitigation**: Firewall configuration and port obfuscation

#### Application-Level Attacks
1. **Message Injection**
   - **Risk**: High - No input sanitization
   - **Impact**: Database corruption or client crashes
   - **Mitigation**: Input validation and sanitization

2. **Buffer Overflow**
   - **Risk**: Medium - C library usage
   - **Impact**: Code execution or crashes
   - **Mitigation**: Bounds checking and safe string functions

3. **Authentication Bypass**
   - **Risk**: High - Minimal authentication
   - **Impact**: Unauthorized access
   - **Mitigation**: Proper authentication system

## Security Hardening

### Network Security

#### 1. Implement TLS/SSL Encryption
```python
import ssl
import socket

def create_secure_server_socket(port):
    # Create SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('server.crt', 'server.key')
    
    # Create and wrap socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_sock = context.wrap_socket(sock, server_side=True)
    secure_sock.bind(('0.0.0.0', port))
    
    return secure_sock

def create_secure_client_socket(host, port):
    # Create SSL context for client
    context = ssl.create_default_context()
    
    # Create and wrap socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_sock = context.wrap_socket(sock, server_hostname=host)
    secure_sock.connect((host, port))
    
    return secure_sock
```

#### 2. Certificate Management
```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes

# For production, use certificates from trusted CA
# Let's Encrypt example:
certbot certonly --standalone -d your-domain.com
```

#### 3. Firewall Configuration
```bash
# Linux iptables - restrictive rules
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Allow only required ports from specific networks
sudo iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 10740 -j ACCEPT
sudo iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 9281 -j ACCEPT
# ... repeat for other ports

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
```

### Authentication and Authorization

#### 1. User Authentication System
```python
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta

class AuthenticationManager:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_database()
        self.active_sessions = {}
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return password_hash.hex(), salt
    
    def create_user(self, username, password):
        password_hash, salt = self.hash_password(password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
                (username, password_hash, salt)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if account is locked
        cursor.execute(
            'SELECT password_hash, salt, failed_attempts, locked_until FROM users WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "Invalid username or password"
        
        password_hash, salt, failed_attempts, locked_until = result
        
        # Check if account is locked
        if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
            conn.close()
            return False, "Account temporarily locked"
        
        # Verify password
        input_hash, _ = self.hash_password(password, salt)
        
        if input_hash == password_hash:
            # Reset failed attempts and update last login
            cursor.execute(
                'UPDATE users SET failed_attempts = 0, last_login = CURRENT_TIMESTAMP WHERE username = ?',
                (username,)
            )
            conn.commit()
            conn.close()
            
            # Create session token
            session_token = secrets.token_hex(32)
            self.active_sessions[session_token] = {
                'username': username,
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
            
            return True, session_token
        else:
            # Increment failed attempts
            failed_attempts += 1
            locked_until = None
            
            if failed_attempts >= 5:
                locked_until = datetime.now() + timedelta(minutes=15)
            
            cursor.execute(
                'UPDATE users SET failed_attempts = ?, locked_until = ? WHERE username = ?',
                (failed_attempts, locked_until, username)
            )
            conn.commit()
            conn.close()
            
            return False, "Invalid username or password"
    
    def validate_session(self, session_token):
        if session_token not in self.active_sessions:
            return False, None
        
        session = self.active_sessions[session_token]
        
        # Check session timeout (24 hours)
        if datetime.now() - session['created_at'] > timedelta(hours=24):
            del self.active_sessions[session_token]
            return False, None
        
        # Update last activity
        session['last_activity'] = datetime.now()
        return True, session['username']
```

#### 2. Session Management
```python
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(hours=2)
    
    def create_session(self, username, client_ip):
        session_id = secrets.token_hex(32)
        self.sessions[session_id] = {
            'username': username,
            'client_ip': client_ip,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return session_id
    
    def validate_session(self, session_id, client_ip):
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Check IP address
        if session['client_ip'] != client_ip:
            return False
        
        # Check timeout
        if datetime.now() - session['last_activity'] > self.session_timeout:
            del self.sessions[session_id]
            return False
        
        # Update activity
        session['last_activity'] = datetime.now()
        return True
    
    def cleanup_expired_sessions(self):
        expired = []
        for session_id, session in self.sessions.items():
            if datetime.now() - session['last_activity'] > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
```

### Input Validation and Sanitization

#### 1. Message Sanitization
```python
import re
import html

class MessageValidator:
    def __init__(self):
        self.max_message_length = 1000
        self.max_username_length = 50
        self.forbidden_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript URLs
            r'on\w+\s*=',               # Event handlers
            r'<iframe.*?>.*?</iframe>',  # Iframes
        ]
    
    def sanitize_message(self, message):
        if not isinstance(message, str):
            raise ValueError("Message must be a string")
        
        # Length check
        if len(message) > self.max_message_length:
            raise ValueError(f"Message too long (max {self.max_message_length} characters)")
        
        # Remove forbidden patterns
        for pattern in self.forbidden_patterns:
            message = re.sub(pattern, '', message, flags=re.IGNORECASE)
        
        # HTML escape
        message = html.escape(message)
        
        # Remove control characters except newlines and tabs
        message = ''.join(char for char in message if ord(char) >= 32 or char in '\n\t')
        
        return message
    
    def validate_username(self, username):
        if not isinstance(username, str):
            raise ValueError("Username must be a string")
        
        if len(username) > self.max_username_length:
            raise ValueError(f"Username too long (max {self.max_username_length} characters)")
        
        # Only allow alphanumeric, underscore, and hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValueError("Username contains invalid characters")
        
        return username
    
    def validate_message_format(self, message_record):
        """Validate database message format"""
        parts = message_record.split(';')
        
        if len(parts) != 4:
            raise ValueError("Invalid message format")
        
        # Validate ID
        try:
            msg_id = int(parts[0])
            if msg_id <= 0:
                raise ValueError("Invalid message ID")
        except ValueError:
            raise ValueError("Message ID must be a positive integer")
        
        # Validate timestamp
        try:
            timestamp = float(parts[1])
            if timestamp <= 0:
                raise ValueError("Invalid timestamp")
        except ValueError:
            raise ValueError("Timestamp must be a valid number")
        
        # Validate username
        self.validate_username(parts[2])
        
        # Validate message content
        self.sanitize_message(parts[3])
        
        return True
```

#### 2. C Library Security
```c
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// Secure version with bounds checking
char* encode_B_secure(const char* in, size_t in_len) {
    if (in == NULL || in_len == 0) {
        return NULL;
    }
    
    // Allocate output buffer with null terminator
    char* out = calloc(3, sizeof(char));
    if (out == NULL) {
        return NULL;  // Allocation failed
    }
    
    // Bounds check
    if (in_len < 1) {
        free(out);
        return NULL;
    }
    
    out[0] = (in[0] & 0x0F) + 'A';
    out[1] = ((in[0] & 0xF0) >> 4) + 'A';
    out[2] = '\0';
    
    return out;
}

char* decode_B_secure(const char* in, size_t in_len) {
    if (in == NULL || in_len < 2) {
        return NULL;
    }
    
    char* out = calloc(2, sizeof(char));
    if (out == NULL) {
        return NULL;
    }
    
    // Validate input characters
    if (in[0] < 'A' || in[0] > 'P' || in[1] < 'A' || in[1] > 'P') {
        free(out);
        return NULL;
    }
    
    out[0] = (in[0] - 'A') + ((in[1] - 'A') << 4);
    out[1] = '\0';
    
    return out;
}
```

### Rate Limiting and DoS Protection

#### 1. Connection Rate Limiting
```python
import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_connections_per_ip=10, time_window=60):
        self.max_connections = max_connections_per_ip
        self.time_window = time_window
        self.connections = defaultdict(deque)
    
    def allow_connection(self, client_ip):
        now = time.time()
        
        # Clean old entries
        while (self.connections[client_ip] and 
               now - self.connections[client_ip][0] > self.time_window):
            self.connections[client_ip].popleft()
        
        # Check rate limit
        if len(self.connections[client_ip]) >= self.max_connections:
            return False
        
        # Add new connection
        self.connections[client_ip].append(now)
        return True

class MessageRateLimiter:
    def __init__(self, max_messages_per_user=30, time_window=60):
        self.max_messages = max_messages_per_user
        self.time_window = time_window
        self.user_messages = defaultdict(deque)
    
    def allow_message(self, username):
        now = time.time()
        
        # Clean old entries
        while (self.user_messages[username] and 
               now - self.user_messages[username][0] > self.time_window):
            self.user_messages[username].popleft()
        
        # Check rate limit
        if len(self.user_messages[username]) >= self.max_messages:
            return False
        
        # Add new message
        self.user_messages[username].append(now)
        return True
```

### Logging and Monitoring

#### 1. Security Event Logging
```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self, log_file='security.log'):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_authentication_attempt(self, username, client_ip, success, reason=None):
        event = {
            'event_type': 'authentication_attempt',
            'username': username,
            'client_ip': client_ip,
            'success': success,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, json.dumps(event))
    
    def log_rate_limit_exceeded(self, client_ip, limit_type):
        event = {
            'event_type': 'rate_limit_exceeded',
            'client_ip': client_ip,
            'limit_type': limit_type,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.warning(json.dumps(event))
    
    def log_suspicious_activity(self, client_ip, activity_type, details):
        event = {
            'event_type': 'suspicious_activity',
            'client_ip': client_ip,
            'activity_type': activity_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.error(json.dumps(event))
```

#### 2. Intrusion Detection
```python
class IntrusionDetector:
    def __init__(self):
        self.failed_attempts = defaultdict(int)
        self.suspicious_patterns = [
            r'<script.*?>',
            r'union.*select',
            r'drop.*table',
            r'exec.*\(',
        ]
    
    def analyze_message(self, message, client_ip):
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                self.log_suspicious_activity(
                    client_ip, 
                    'malicious_pattern', 
                    f'Pattern: {pattern}'
                )
                return False
        
        return True
    
    def track_failed_authentication(self, client_ip):
        self.failed_attempts[client_ip] += 1
        
        if self.failed_attempts[client_ip] > 5:
            self.log_suspicious_activity(
                client_ip,
                'brute_force_attempt',
                f'Failed attempts: {self.failed_attempts[client_ip]}'
            )
            return True  # Suspicious
        
        return False
```

## Security Best Practices

### Development Practices
1. **Secure Coding**
   - Always validate input
   - Use parameterized queries
   - Implement proper error handling
   - Avoid hardcoded secrets

2. **Code Review**
   - Review all security-related code
   - Use static analysis tools
   - Test security features thoroughly

3. **Dependency Management**
   - Keep dependencies updated
   - Use vulnerability scanners
   - Minimize external dependencies

### Deployment Practices
1. **Environment Security**
   - Use separate environments (dev/staging/prod)
   - Implement proper access controls
   - Regular security updates

2. **Configuration Management**
   - Store secrets securely
   - Use environment variables
   - Implement configuration validation

3. **Monitoring and Alerting**
   - Monitor security events
   - Set up automated alerts
   - Regular security audits

### Operational Security
1. **Access Control**
   - Principle of least privilege
   - Regular access reviews
   - Multi-factor authentication

2. **Backup and Recovery**
   - Encrypted backups
   - Regular restore testing
   - Incident response plan

3. **Network Security**
   - Network segmentation
   - Regular penetration testing
   - Traffic monitoring

## Security Checklist

### Pre-Deployment
- [ ] Implement user authentication
- [ ] Enable TLS/SSL encryption
- [ ] Add input validation
- [ ] Configure rate limiting
- [ ] Set up security logging
- [ ] Review firewall rules
- [ ] Test security features

### Post-Deployment
- [ ] Monitor security logs
- [ ] Regular security updates
- [ ] Periodic security audits
- [ ] Backup verification
- [ ] Incident response testing
- [ ] User access reviews

### Ongoing Maintenance
- [ ] Security patch management
- [ ] Log analysis and alerting
- [ ] Performance monitoring
- [ ] Vulnerability assessments
- [ ] Security training for developers
- [ ] Documentation updates

This security guide provides a comprehensive framework for securing the General Communications system. Implementation should be prioritized based on your specific threat model and deployment environment.