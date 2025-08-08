# Encryption & Hashes
We have port(12090), This sends over hashes of passwords from the data, server to client(with the first 4 bytes being a header to ideftify what it is for)
We will have another port(4556). for the client to server, which will send over the passwords to be hashed(or hashed passwords) to the server, which will authenticate the user.