import socket
import serial
import sys
import threading


def recv_msg():
    while True:
        recv_msg = conn.recv(1024)
        if not recv_msg:
            sys.exit(0)
        # recv_msg = recv_msg.decode()
        # print(recv_msg)
        s.write(recv_msg)


def send_msg():
    while True:
        send_msg = s.read_all()
        # send_msg = raw_input()
        send_msg = send_msg.encode()
        conn.send(send_msg)
        # print("message sent")


# get my PC IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
s_my_ip = s.getsockname()[0]
s.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (s_my_ip, 60000)
print(sys.stderr, 'starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

print('Start')
s = serial.Serial('COM25', 57600, timeout=5)
s.close()
s.open()
conn, addr = sock.accept()

# thread has to start before other loop
t = threading.Thread(target=recv_msg)
t.start()

send_msg()

# while True:
#     # Wait for a connection
#     print >> sys.stderr, 'waiting for a connection'
#     connection, client_address = sock.accept()
#
#     try:
#         print >> sys.stderr, 'connection from', client_address
#
#         # Receive the data in small chunks and retransmit it
#         while True:
#             data = connection.recv(16)
#             print >> sys.stderr, 'received "%s"' % data
#             if data:
#                 print >> sys.stderr, 'sending data back to the client'
#                 connection.sendall(data)
#             else:
#                 print >> sys.stderr, 'no more data from', client_address
#                 break
#
#     finally:
#         # Clean up the connection
#         connection.close()
