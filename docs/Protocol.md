# PROTOCOLS
## HEARTBEATS
A heartbeat is a protocol used by the General Coms software.
The default port for said protocol is 10740.
### How it works
This protocol involves the server sending a packet to the client and awaiting a response.
The response typically is the time of the clients previous heartbeat.
Said time will be used later for sending new messages.
If the client doesnt connect or takes to long said client will be KICKED.
## MESSAGE SENDING(SERVER)
A message send protocol is a protocol used by the General Coms software.
The default port for said protocol is 6090.
### How it works
This protocol involves the server sending huge packets containing all the new messages from the database of messages.
## MESSAGE SENDING(CLIENT)
A message receive protocol is a protocol used by the General Coms software.
The default port for said protocol is 9980
## How it works
This protocol involves the client sending a message to the server.
Once said message is sent the server typically adds it to its database