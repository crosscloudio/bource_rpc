# Protocol:
This library enables communication between a client and a server using JSONRPC 
and different transport layers (such as NamedPipes or Unix Domain Sockets) over
streams. 

The protocol of between server and client determines the size of a message to read
from the other side by sending 4 bytes of length before the actual message. 

- So an example of a message would look like: [size of following message M (4 bytes)] [M]

The other end can simply read the first 4 byte of the stream to determine the 
length and then read length byte from the stream to receive the message. 