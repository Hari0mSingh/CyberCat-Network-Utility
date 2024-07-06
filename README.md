# CyberCat

CyberCat is a Python-based command-line network utility for various network operations, including listening on ports, executing remote commands, uploading files, and providing an interactive command shell access to remote systems.

## Features

- **Listening Mode**: Listen on [host]:[port] for incoming connections.
- **Execute Command**: Execute a specified file upon receiving a connection.
- **Upload File**: Upload a file to a specified destination upon receiving a connection.
- **Interactive Shell**: Provide an interactive command shell access to remote systems.

## Usage

```bash
./cybercat.py -t <target_host> -p <port> [-l | -c | -e <file_to_run> | -u <destination>] 
# Listen on 192.168.0.1:5555 and enter command shell mode
./cybercat.py -t 192.168.0.1 -p 5555 -l -c

# Listen on 192.168.0.1:5555 and upload a file to c:\target.exe
./cybercat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe

# Listen on 192.168.0.1:5555 and execute a command (e.g., cat /etc/passwd)
./cybercat.py -t 192.168.0.1 -p 5555 -l -e="cat /etc/passwd"

# Connect to www.google.com on port 80 and send a simple HTTP GET request
echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | ./cybercat.py -t www.google.com -p 80

 ```
## Contributing

Contributions are welcome! If you find any issues or have suggestions, please feel free to open an issue or create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
