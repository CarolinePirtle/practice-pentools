import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    #runs a command on local machiene and returns the output
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)

    return output.decode()
#Note the newline character to make it NetCat friendly
class NetCat:
    #Intialize with arguments from the command line and the buffer
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        #create a socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #entry point for managing the NetCat
    def run(self):
        #If we are setting up a listner, call this
        if self.args.listen:
            self.listen()
        #otherwise call this one!
        else:
            self.send()
    def send(self):
        #connect to the target and port
        self.socket.connect((self.args.target, self.args.port))
        #If we havea buffer, send it to the target first
        if self.buffer:
            self.socket.send(self.buffer)
        
        #Lets you close manually with CTRL C
        try:
            #Loop to recieve data
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                    #Print response and pause to get interactive input to send
                    if response:
                        print(response)
                        buffer = input('> ')
                        buffer += '\n'
                        self.socket.send(buffer.encode())
        #Close the socket 
        except KeyboardInterrupt:
            print('User Terminated')
            self.socket.close()
            sys.exit()

    def listen(self):
        #Binds to target and port
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        #Starts listening in a loop
        while True:
            client_socket, _ = self.socket.accept()
            #Passing connected socket to the handle method
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()
    #Executes the task cooresponding to the command line argument it recieves
    def handle(self, client_socket):
        #If a command is executed, passes command to the exeute function and sends output back on the socket
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        #If a file should be uploaded, set up a loop to listen for content on listening socket until no more comes in then write to it
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
                message = f'Saved file {self.args.upload}'
                client_socket.send (message.encode())
        #If a shell is created, set up a prompt, take input, and send to execute()
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    #Create a command line interface
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        #Provide examples for --help + how we want it to behave
        epilog=textwrap.dedent('''Example:
                               netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
                               netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # Upload to a file
                               netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # Execute a command
                               echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
                               netcat.py -t 192.168.1.108 -p 5555 # Connect to a server
                               '''))
    #set up interactive shell
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    #executes one specific command
    parser.add_argument('-e', '--execute', help='execute specified command')
    #sets up a listener
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    #Specifies port to communicate on
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    #Specifies target IP
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    #Specifies name of file to upload
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    #set up listener with empty buffer string
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode())
    nc.run()

    
    
