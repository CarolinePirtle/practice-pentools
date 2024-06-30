import socket
import threading

IP = '0.0.0.0'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #tell server what to listen too
    server.bind((IP, PORT))
    #maximum connections set to 5
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, address = server.accept()
        #When a client connects, client socket stored in client
        #remote connection details in address function
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        #create a new thread to handle client connection
        client_handler = threading.Thread(target=handle_client, arge=(client))
        client_handler.start()

#Performs recieving and sends simple message backs
def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Recieved: {request.decode("utf-8")}')
        sock.send(b'ACK')
if __name__ == '__main__':
    main()