from colorama import init, Fore
import pickle
import socket
import sys
init(autoreset=True) # Autoreset line color style

#############################################################################################
# DESCRIPTION
#############################################################################################

#

#############################################################################################
# CONNECTION PARAMETERS
#############################################################################################

# Server-client connection setup
IP = socket.gethostname() # To use with localhost address
#IP = '192.168.242.119' # Local server computer IP
PORT = 12345 # Server PORT
FORMAT = 'utf-8' # Data format for bytes encoding and decoding
N_BYTES = 2000 # Maximun number of bytes to expect from connection
TIMEOUT = 500 # Maximum number of seconds of innactivity

#############################################################################################
# CONNECT TWO COMPUTERS TO SEND AND RECEIVE PICKLED DATA FROM/TO THE EXPERIMENTAL SOFTWARE
#############################################################################################

# Just accept one-one connection client-server

class Connection():

    # Class object attributes
    IP = IP
    PORT = PORT
    FORMAT = FORMAT
    N_BYTES = N_BYTES

    # Set a timeout (when client/server do not send/receive any data for this timeframe, then close connection)
    socket.setdefaulttimeout(TIMEOUT)

    # Start TCP/IP socket
    server = socket.socket(socket.AF_INET, # IPV4 
                           socket.SOCK_STREAM) # TCP

    client = socket.socket(socket.AF_INET, # IPV4 
                           socket.SOCK_STREAM) # TCP

    # To be able to create a new server on IP and PORT after closing actual server terminal
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start_server(self):
        # Try to bind server to IP and PORT
        try:
            print(Fore.YELLOW + '[STARTING] Server is starting...')
            self.server.bind((self.IP, # Get IP address to be the server address
                              self.PORT)) # Stablish a port to connect (usually above 1000))
        except socket.error:
            print(Fore.RED + f'[ERROR] Server connection to {self.IP} on port {self.PORT} has failed.')
            print(Fore.YELLOW + '[CLOSING] Closing server...')
            sys.exit() # To close server script in case connection to specified IP and PORT fails

        # Waiting for connections
        self.server.listen() # Listen for new connections
        print(Fore.YELLOW + f'[WAITING] Waiting for connection with the experimental software on {self.IP} and port {self.PORT}')
        while True: # Loop awaiting for a connection
            self.client, self.client_address = self.server.accept() # When connection to client occurs assigns client data to client_address (IP:PORT) and stablish a client_socket.
            if self.client:
                break
        print(Fore.GREEN + f'[CONNECTED] Connection with {self.client_address} has been established.')

    def start_client(self):
        try:
            print(Fore.YELLOW + '[STARTING] Client is starting...')
            self.client.connect((self.IP, # To connect to the server side
                                 self.PORT)) # Stablish a port to connect (usually above 1000))
            print(Fore.GREEN + f'[CONNECTED] You are now connected to {self.IP} on port {self.PORT}.')
        except socket.error:
            print(Fore.RED + f'[ERROR] Connection to server {self.IP} on port {self.PORT} has failed.')
            print(Fore.YELLOW + '[CLOSING] Closing client...')
            sys.exit() # To close the client script in case connection to specified IP and PORT fails

    def listen(self):
        print(Fore.YELLOW + '[WAITING] Waiting for messages...')
        message = self.client.recv(self.N_BYTES) # Receive information
        message = pickle.loads(message) # Unpickle the message
        print(Fore.GREEN + f'[RECEIVED] Message "{message}" received from server.')
        return message

    def send(self, message):
        print(Fore.YELLOW + f'[SENDING] Sending "{message}"...')
        message = pickle.dumps(message) # Pickle the message
        self.client.send(message)

if __name__ == '__main__':
    connection = Connection() # Create an object call connection to be used in interactive mode 