# Performance Guide

This guide provides comprehensive information on optimizing the General Communications system for better performance, scalability, and resource efficiency.

## Performance Overview

### Current Performance Characteristics

#### Baseline Performance
- **Concurrent Clients**: ~50-100 clients (default configuration)
- **Message Throughput**: ~100-500 messages/second
- **Memory Usage**: ~10-50 MB per 100 clients
- **CPU Usage**: ~5-15% on modern hardware
- **Network Bandwidth**: ~1-10 Mbps depending on message frequency

#### Performance Bottlenecks
1. **Threading Model**: One thread per client limits scalability
2. **Database I/O**: Synchronous file operations block message processing
3. **Network I/O**: Multiple socket connections per client
4. **Memory Management**: No message cleanup or caching strategies
5. **C Library**: Memory allocation/deallocation overhead

## Server Performance Optimization

### Threading and Concurrency

#### 1. Thread Pool Implementation
```python
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

class OptimizedServer:
    def __init__(self, max_workers=100):
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.client_queue = queue.Queue()
        self.active_clients = {}
        self.message_queue = queue.Queue()
        
    def handle_client_connection(self, client_socket, client_addr):
        """Handle client in thread pool instead of creating new thread"""
        try:
            self.authenticate_client(client_socket, client_addr)
            self.active_clients[client_addr[0]] = {
                'socket': client_socket,
                'last_heartbeat': time.time(),
                'message_count': 0
            }
        except Exception as e:
            logging.error(f"Client handling error: {e}")
        finally:
            client_socket.close()
    
    def accept_connections(self):
        """Main connection acceptance loop"""
        while not self.exiting:
            try:
                client_socket, client_addr = self.server_socket.accept()
                # Submit to thread pool instead of creating new thread
                self.thread_pool.submit(
                    self.handle_client_connection, 
                    client_socket, 
                    client_addr
                )
            except Exception as e:
                logging.error(f"Connection acceptance error: {e}")
```

#### 2. Asynchronous I/O with asyncio
```python
import asyncio
import aiofiles

class AsyncServer:
    def __init__(self):
        self.clients = {}
        self.message_queue = asyncio.Queue()
        
    async def handle_client(self, reader, writer):
        """Handle client connection asynchronously"""
        client_addr = writer.get_extra_info('peername')
        
        try:
            # Authentication
            await self.authenticate_client_async(reader, writer)
            
            # Add to active clients
            self.clients[client_addr[0]] = {
                'reader': reader,
                'writer': writer,
                'last_heartbeat': time.time()
            }
            
            # Handle client messages
            await self.handle_client_messages(reader, writer, client_addr[0])
            
        except Exception as e:
            logging.error(f"Async client error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            self.clients.pop(client_addr[0], None)
    
    async def start_server(self, host='127.0.0.1', port=10740):
        """Start async server"""
        server = await asyncio.start_server(
            self.handle_client, host, port
        )
        
        async with server:
            await server.serve_forever()
    
    async def broadcast_message(self, message):
        """Broadcast message to all clients asynchronously"""
        if not self.clients:
            return
            
        tasks = []
        for client_ip, client_info in self.clients.items():
            task = self.send_message_to_client(client_info['writer'], message)
            tasks.append(task)
        
        # Send to all clients concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
```

### Database Optimization

#### 1. Asynchronous Database Operations
```python
import aiofiles
import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor

class AsyncDatabase:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for better performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create optimized table structure
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON messages(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON messages(created_at)')
        
        # Enable WAL mode for better concurrent access
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA cache_size=10000')
        cursor.execute('PRAGMA temp_store=MEMORY')
        
        conn.commit()
        conn.close()
    
    async def add_message_async(self, timestamp, username, message):
        """Add message asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._add_message_sync,
            timestamp, username, message
        )
    
    def _add_message_sync(self, timestamp, username, message):
        """Synchronous message addition"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO messages (timestamp, username, message) VALUES (?, ?, ?)',
            (timestamp, username, message)
        )
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return message_id
    
    async def get_messages_since_async(self, timestamp):
        """Get messages since timestamp asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._get_messages_since_sync,
            timestamp
        )
    
    def _get_messages_since_sync(self, timestamp):
        """Synchronous message retrieval"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, timestamp, username, message FROM messages WHERE timestamp > ? ORDER BY timestamp',
            (timestamp,)
        )
        
        messages = cursor.fetchall()
        conn.close()
        
        return messages
```

#### 2. Message Caching Strategy
```python
import time
from collections import OrderedDict
import threading

class MessageCache:
    def __init__(self, max_size=10000, ttl=3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.last_cleanup = time.time()
    
    def add_message(self, message_id, timestamp, username, message):
        """Add message to cache"""
        with self.lock:
            # Cleanup old entries periodically
            if time.time() - self.last_cleanup > 300:  # 5 minutes
                self._cleanup_expired()
            
            # Add new message
            self.cache[message_id] = {
                'timestamp': timestamp,
                'username': username,
                'message': message,
                'cached_at': time.time()
            }
            
            # Remove oldest if cache is full
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
    
    def get_messages_since(self, timestamp):
        """Get cached messages since timestamp"""
        with self.lock:
            messages = []
            for msg_id, msg_data in self.cache.items():
                if msg_data['timestamp'] > timestamp:
                    messages.append((
                        msg_id,
                        msg_data['timestamp'],
                        msg_data['username'],
                        msg_data['message']
                    ))
            return messages
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for msg_id, msg_data in self.cache.items():
            if current_time - msg_data['cached_at'] > self.ttl:
                expired_keys.append(msg_id)
        
        for key in expired_keys:
            self.cache.pop(key, None)
        
        self.last_cleanup = current_time
```

### Network Optimization

#### 1. Connection Pooling
```python
import socket
import queue
import threading
import time

class ConnectionPool:
    def __init__(self, max_connections=50):
        self.max_connections = max_connections
        self.available_connections = queue.Queue()
        self.active_connections = {}
        self.lock = threading.Lock()
    
    def get_connection(self, client_ip, port):
        """Get or create connection to client"""
        connection_key = f"{client_ip}:{port}"
        
        with self.lock:
            if connection_key in self.active_connections:
                return self.active_connections[connection_key]
        
        try:
            # Try to get from pool
            if not self.available_connections.empty():
                conn = self.available_connections.get_nowait()
                if self._is_connection_valid(conn):
                    with self.lock:
                        self.active_connections[connection_key] = conn
                    return conn
            
            # Create new connection
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(5.0)
            conn.connect((client_ip, port))
            
            with self.lock:
                self.active_connections[connection_key] = conn
            
            return conn
            
        except Exception as e:
            logging.error(f"Connection pool error: {e}")
            return None
    
    def return_connection(self, connection_key, conn):
        """Return connection to pool"""
        with self.lock:
            self.active_connections.pop(connection_key, None)
        
        if self._is_connection_valid(conn) and self.available_connections.qsize() < self.max_connections:
            self.available_connections.put(conn)
        else:
            try:
                conn.close()
            except:
                pass
    
    def _is_connection_valid(self, conn):
        """Check if connection is still valid"""
        try:
            # Send a small test packet
            conn.send(b'')
            return True
        except:
            return False
```

#### 2. Message Batching
```python
import time
import threading
from collections import defaultdict

class MessageBatcher:
    def __init__(self, batch_size=10, batch_timeout=0.1):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_messages = defaultdict(list)
        self.last_batch_time = defaultdict(float)
        self.lock = threading.Lock()
        
        # Start batch processor
        self.batch_thread = threading.Thread(target=self._process_batches, daemon=True)
        self.batch_thread.start()
    
    def add_message(self, client_ip, message):
        """Add message to batch for client"""
        with self.lock:
            self.pending_messages[client_ip].append(message)
            
            if not self.last_batch_time[client_ip]:
                self.last_batch_time[client_ip] = time.time()
            
            # Send immediately if batch is full
            if len(self.pending_messages[client_ip]) >= self.batch_size:
                self._send_batch(client_ip)
    
    def _process_batches(self):
        """Process pending batches periodically"""
        while True:
            time.sleep(0.05)  # Check every 50ms
            
            with self.lock:
                current_time = time.time()
                clients_to_process = []
                
                for client_ip, last_time in self.last_batch_time.items():
                    if (current_time - last_time >= self.batch_timeout and 
                        self.pending_messages[client_ip]):
                        clients_to_process.append(client_ip)
                
                for client_ip in clients_to_process:
                    self._send_batch(client_ip)
    
    def _send_batch(self, client_ip):
        """Send batched messages to client"""
        if not self.pending_messages[client_ip]:
            return
        
        messages = self.pending_messages[client_ip].copy()
        self.pending_messages[client_ip].clear()
        self.last_batch_time[client_ip] = 0
        
        # Send batch (implement actual sending logic)
        self._deliver_batch_to_client(client_ip, messages)
    
    def _deliver_batch_to_client(self, client_ip, messages):
        """Deliver batch of messages to client"""
        try:
            # Combine messages into single transmission
            batch_data = '\n'.join(messages)
            
            # Send to client (implement based on your protocol)
            # self.send_to_client(client_ip, batch_data)
            
        except Exception as e:
            logging.error(f"Batch delivery error: {e}")
```

## Client Performance Optimization

### Connection Management

#### 1. Connection Reuse
```python
import socket
import time
import threading

class OptimizedClient:
    def __init__(self):
        self.connections = {}
        self.connection_lock = threading.Lock()
        self.last_heartbeat = 0
        
    def get_connection(self, host, port, reuse=True):
        """Get or create connection with reuse"""
        connection_key = f"{host}:{port}"
        
        if reuse:
            with self.connection_lock:
                if connection_key in self.connections:
                    conn = self.connections[connection_key]
                    if self._is_connection_alive(conn):
                        return conn
                    else:
                        # Remove dead connection
                        self.connections.pop(connection_key, None)
        
        # Create new connection
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(10.0)
            conn.connect((host, port))
            
            if reuse:
                with self.connection_lock:
                    self.connections[connection_key] = conn
            
            return conn
            
        except Exception as e:
            logging.error(f"Connection creation failed: {e}")
            return None
    
    def _is_connection_alive(self, conn):
        """Check if connection is still alive"""
        try:
            # Use SO_ERROR to check connection status
            error = conn.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            return error == 0
        except:
            return False
    
    def close_all_connections(self):
        """Close all cached connections"""
        with self.connection_lock:
            for conn in self.connections.values():
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()
```

#### 2. Optimized Message Display
```python
import threading
import queue
import time
from collections import deque

class MessageDisplayManager:
    def __init__(self, max_display_messages=1000):
        self.max_display_messages = max_display_messages
        self.message_queue = queue.Queue()
        self.display_buffer = deque(maxlen=max_display_messages)
        self.display_lock = threading.Lock()
        
        # Start display thread
        self.display_thread = threading.Thread(target=self._display_worker, daemon=True)
        self.display_thread.start()
    
    def add_message(self, username, message):
        """Add message to display queue"""
        self.message_queue.put((username, message, time.time()))
    
    def _display_worker(self):
        """Worker thread for displaying messages"""
        batch = []
        last_display = time.time()
        
        while True:
            try:
                # Collect messages for batch display
                timeout = 0.1  # 100ms batch timeout
                
                try:
                    while len(batch) < 10:  # Max 10 messages per batch
                        username, message, timestamp = self.message_queue.get(timeout=timeout)
                        batch.append((username, message, timestamp))
                        timeout = 0.01  # Shorter timeout for subsequent messages
                except queue.Empty:
                    pass
                
                # Display batch if we have messages or timeout reached
                if batch and (len(batch) >= 10 or time.time() - last_display > 0.1):
                    self._display_batch(batch)
                    batch.clear()
                    last_display = time.time()
                    
            except Exception as e:
                logging.error(f"Display worker error: {e}")
    
    def _display_batch(self, messages):
        """Display batch of messages efficiently"""
        with self.display_lock:
            for username, message, timestamp in messages:
                formatted_message = f"{username}: {message}"
                self.display_buffer.append(formatted_message)
                print(formatted_message)  # Or use more efficient display method
```

## Memory Optimization

### Memory Management

#### 1. Object Pooling
```python
import threading
import queue

class ObjectPool:
    def __init__(self, create_func, reset_func=None, max_size=100):
        self.create_func = create_func
        self.reset_func = reset_func
        self.max_size = max_size
        self.pool = queue.Queue(maxsize=max_size)
        self.lock = threading.Lock()
    
    def get_object(self):
        """Get object from pool or create new one"""
        try:
            obj = self.pool.get_nowait()
            return obj
        except queue.Empty:
            return self.create_func()
    
    def return_object(self, obj):
        """Return object to pool"""
        if self.reset_func:
            self.reset_func(obj)
        
        try:
            self.pool.put_nowait(obj)
        except queue.Full:
            # Pool is full, let object be garbage collected
            pass

# Example usage for socket objects
def create_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def reset_socket(sock):
    # Reset socket state if needed
    pass

socket_pool = ObjectPool(create_socket, reset_socket, max_size=50)
```

#### 2. Memory Monitoring
```python
import psutil
import threading
import time
import logging

class MemoryMonitor:
    def __init__(self, check_interval=60, memory_threshold=500):  # 500MB threshold
        self.check_interval = check_interval
        self.memory_threshold = memory_threshold * 1024 * 1024  # Convert to bytes
        self.monitoring = True
        
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_memory(self):
        """Monitor memory usage and trigger cleanup if needed"""
        while self.monitoring:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                
                if memory_info.rss > self.memory_threshold:
                    logging.warning(f"High memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
                    self._trigger_cleanup()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logging.error(f"Memory monitoring error: {e}")
    
    def _trigger_cleanup(self):
        """Trigger memory cleanup procedures"""
        # Implement cleanup logic
        # - Clear message caches
        # - Close unused connections
        # - Garbage collect
        import gc
        gc.collect()
```

## C Library Optimization

### Optimized C Functions

#### 1. Memory-Efficient Encoding
```c
#include <stdlib.h>
#include <string.h>

// Pre-allocated buffer pool for encoding operations
static char* buffer_pool[100];
static int pool_size = 0;
static int pool_index = 0;

char* get_buffer() {
    if (pool_size == 0) {
        // Initialize buffer pool
        for (int i = 0; i < 100; i++) {
            buffer_pool[i] = malloc(3);
        }
        pool_size = 100;
    }
    
    char* buffer = buffer_pool[pool_index];
    pool_index = (pool_index + 1) % pool_size;
    return buffer;
}

char* encode_B_optimized(char* in) {
    if (in == NULL) return NULL;
    
    char* out = get_buffer();  // Use pooled buffer
    out[0] = (in[0] & 0x0F) + 'A';
    out[1] = ((in[0] & 0xF0) >> 4) + 'A';
    out[2] = '\0';
    
    return out;
}

// Batch encoding for multiple characters
void encode_batch(char* input, int input_len, char* output) {
    for (int i = 0; i < input_len; i++) {
        output[i * 2] = (input[i] & 0x0F) + 'A';
        output[i * 2 + 1] = ((input[i] & 0xF0) >> 4) + 'A';
    }
    output[input_len * 2] = '\0';
}
```

#### 2. SIMD Optimization (Advanced)
```c
#include <immintrin.h>  // For AVX2 instructions

// SIMD-optimized encoding for large data
void encode_simd(const char* input, char* output, size_t length) {
    size_t simd_length = length & ~31;  // Process 32 bytes at a time
    
    for (size_t i = 0; i < simd_length; i += 32) {
        __m256i data = _mm256_loadu_si256((__m256i*)(input + i));
        
        // Split into low and high nibbles
        __m256i low_nibbles = _mm256_and_si256(data, _mm256_set1_epi8(0x0F));
        __m256i high_nibbles = _mm256_and_si256(_mm256_srli_epi16(data, 4), _mm256_set1_epi8(0x0F));
        
        // Add 'A' offset
        low_nibbles = _mm256_add_epi8(low_nibbles, _mm256_set1_epi8('A'));
        high_nibbles = _mm256_add_epi8(high_nibbles, _mm256_set1_epi8('A'));
        
        // Interleave and store
        __m256i result_low = _mm256_unpacklo_epi8(low_nibbles, high_nibbles);
        __m256i result_high = _mm256_unpackhi_epi8(low_nibbles, high_nibbles);
        
        _mm256_storeu_si256((__m256i*)(output + i * 2), result_low);
        _mm256_storeu_si256((__m256i*)(output + i * 2 + 32), result_high);
    }
    
    // Handle remaining bytes
    for (size_t i = simd_length; i < length; i++) {
        output[i * 2] = (input[i] & 0x0F) + 'A';
        output[i * 2 + 1] = ((input[i] & 0xF0) >> 4) + 'A';
    }
}
```

## Performance Monitoring

### Metrics Collection

#### 1. Performance Metrics
```python
import time
import threading
from collections import defaultdict, deque

class PerformanceMetrics:
    def __init__(self):
        self.metrics = defaultdict(deque)
        self.counters = defaultdict(int)
        self.timers = {}
        self.lock = threading.Lock()
    
    def start_timer(self, name):
        """Start timing an operation"""
        self.timers[name] = time.time()
    
    def end_timer(self, name):
        """End timing and record duration"""
        if name in self.timers:
            duration = time.time() - self.timers[name]
            with self.lock:
                self.metrics[f"{name}_duration"].append(duration)
                # Keep only last 1000 measurements
                if len(self.metrics[f"{name}_duration"]) > 1000:
                    self.metrics[f"{name}_duration"].popleft()
            del self.timers[name]
            return duration
        return 0
    
    def increment_counter(self, name, value=1):
        """Increment a counter"""
        with self.lock:
            self.counters[name] += value
    
    def record_value(self, name, value):
        """Record a value"""
        with self.lock:
            self.metrics[name].append(value)
            if len(self.metrics[name]) > 1000:
                self.metrics[name].popleft()
    
    def get_stats(self):
        """Get performance statistics"""
        with self.lock:
            stats = {}
            
            # Counter stats
            for name, value in self.counters.items():
                stats[name] = value
            
            # Metric stats
            for name, values in self.metrics.items():
                if values:
                    stats[f"{name}_avg"] = sum(values) / len(values)
                    stats[f"{name}_min"] = min(values)
                    stats[f"{name}_max"] = max(values)
                    stats[f"{name}_count"] = len(values)
            
            return stats

# Global metrics instance
metrics = PerformanceMetrics()
```

#### 2. Performance Dashboard
```python
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            stats = metrics.get_stats()
            self.wfile.write(json.dumps(stats, indent=2).encode())
        
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Performance Dashboard</title>
                <script>
                    function updateMetrics() {
                        fetch('/metrics')
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('metrics').innerHTML = 
                                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                            });
                    }
                    setInterval(updateMetrics, 5000);
                    updateMetrics();
                </script>
            </head>
            <body>
                <h1>Performance Dashboard</h1>
                <div id="metrics"></div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

def start_metrics_server(port=8080):
    """Start metrics HTTP server"""
    server = HTTPServer(('localhost', port), MetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
```

## Benchmarking and Testing

### Load Testing

#### 1. Client Load Generator
```python
import threading
import time
import socket
import random

class LoadTester:
    def __init__(self, server_host='127.0.0.1', num_clients=50):
        self.server_host = server_host
        self.num_clients = num_clients
        self.results = []
        self.active_clients = 0
        self.lock = threading.Lock()
    
    def simulate_client(self, client_id):
        """Simulate a single client"""
        try:
            start_time = time.time()
            
            # Connect and authenticate
            auth_time = self._authenticate_client(client_id)
            
            # Send messages
            message_times = []
            for i in range(10):  # Send 10 messages per client
                msg_time = self._send_message(client_id, f"Message {i} from client {client_id}")
                message_times.append(msg_time)
                time.sleep(random.uniform(0.1, 1.0))  # Random delay
            
            total_time = time.time() - start_time
            
            with self.lock:
                self.results.append({
                    'client_id': client_id,
                    'total_time': total_time,
                    'auth_time': auth_time,
                    'message_times': message_times,
                    'avg_message_time': sum(message_times) / len(message_times)
                })
                self.active_clients -= 1
                
        except Exception as e:
            print(f"Client {client_id} error: {e}")
            with self.lock:
                self.active_clients -= 1
    
    def run_load_test(self):
        """Run load test with multiple clients"""
        print(f"Starting load test with {self.num_clients} clients...")
        
        start_time = time.time()
        threads = []
        
        for i in range(self.num_clients):
            thread = threading.Thread(target=self.simulate_client, args=(i,))
            threads.append(thread)
            
            with self.lock:
                self.active_clients += 1
            
            thread.start()
            time.sleep(0.1)  # Stagger client starts
        
        # Wait for all clients to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Generate report
        self._generate_report(total_time)
    
    def _generate_report(self, total_time):
        """Generate load test report"""
        if not self.results:
            print("No results to report")
            return
        
        successful_clients = len(self.results)
        failed_clients = self.num_clients - successful_clients
        
        avg_total_time = sum(r['total_time'] for r in self.results) / successful_clients
        avg_auth_time = sum(r['auth_time'] for r in self.results) / successful_clients
        avg_message_time = sum(r['avg_message_time'] for r in self.results) / successful_clients
        
        print(f"\n=== Load Test Report ===")
        print(f"Total test time: {total_time:.2f}s")
        print(f"Successful clients: {successful_clients}/{self.num_clients}")
        print(f"Failed clients: {failed_clients}")
        print(f"Average client total time: {avg_total_time:.2f}s")
        print(f"Average authentication time: {avg_auth_time:.2f}s")
        print(f"Average message send time: {avg_message_time:.2f}s")
        print(f"Messages per second: {(successful_clients * 10) / total_time:.2f}")
```

## Configuration Tuning

### System-Level Optimization

#### 1. Operating System Tuning
```bash
# Linux network tuning
echo 'net.core.somaxconn = 1024' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 1024' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_fin_timeout = 30' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_keepalive_time = 120' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_keepalive_intvl = 30' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_keepalive_probes = 3' >> /etc/sysctl.conf
sysctl -p

# Increase file descriptor limits
echo '* soft nofile 65536' >> /etc/security/limits.conf
echo '* hard nofile 65536' >> /etc/security/limits.conf
```

#### 2. Python Optimization
```python
# Optimize Python settings
import sys
import gc

# Disable garbage collection during critical sections
gc.disable()

# Optimize string interning for usernames
sys.intern('username')

# Use slots for memory efficiency
class OptimizedClient:
    __slots__ = ['ip', 'socket', 'last_heartbeat', 'message_count']
    
    def __init__(self, ip, socket):
        self.ip = ip
        self.socket = socket
        self.last_heartbeat = time.time()
        self.message_count = 0
```

This performance guide provides comprehensive strategies for optimizing the General Communications system. Implementation should be done incrementally, with careful testing and monitoring to ensure improvements don't introduce new issues.