import json
import socket
import threading
from cryptography.fernet import Fernet


class Router:
    """
    A class used to represent a Router
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the router object.
        """
        self.router_name = input("Write the node name: ")
        self.running = True
        self.json_routes = []
        self.server_socket = None
        self.network = self.read_json("Json/network.json")
        self.clients = []
        key = b'HcEnve-04K7wN5sgrz1JgKufDMIYBbbTXr0Wueg3v7I='
        self.fernet = Fernet(key)

    def start(self):
        """
        Starts the router.
        """

        self.connect_to_controller("localhost", 8888)
        # Create a TCP server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the address and port
        port = self.network["Ports"][self.router_name]
        self.server_socket.bind(("localhost", port))
        # Listen for incoming connections
        self.server_socket.listen(5)

        while self.running:
            # Accept a new connection
            client_socket, client_address = self.server_socket.accept()
            print(
                f"Connection between {self.router_name} and {client_address}")
            # Start a new thread to handle the client
            client_handler_thread = threading.Thread(
                target=self.handle_connection, args=(client_socket,))
            client_handler_thread.start()

    def handle_connection(self, client_socket):
        """
        Handles a connection.

        Parameters
        ----------
            client_socket : socket
                the client's socket
        """

        # Receive data from the client
        data = client_socket.recv(1024).decode()
        if not data or data == "shutdown-the-router":
            self.running = False

        elif data == "ACK":
            ack_answer = "I am chill bro"
            client_socket.sendall(ack_answer.encode())

        elif data == "New Path":
            self.json_routes = json.loads(
                self.fernet.decrypt(client_socket.recv(4096)).decode())
            print(f"The path reached {self.router_name}")
            self.write_json(self.json_routes)

        elif data.startswith("New Client"):
            _, new_client = data.split("-")
            self.clients.append(new_client)
            clients_json = self.read_json("Json/clients_directory.json")
            clients_json[self.router_name] = self.clients
            self.write_json(clients_json, "Json/clients_directory.json")

        else:
            self.handle_client(data, client_socket)

    def handle_client(self, data, client_socket):
        """
        Handles a client connection.

        Parameters
        ----------
            data : str
                data sent by the client
            client_socket : socket
                the client's socket
        """
        destiny, destiny_router, message = data.split("-")
        if destiny_router == self.router_name:
            print(message)
            if message == "audio(°_°)":
                client_socket.sendall("send it".encode())
                new_data = client_socket.recv(32768)
                audio_data = new_data
                while True:
                    new_data = client_socket.recv(32768)
                    if not new_data:
                        break
                    audio_data += new_data

                self.send_to_server("localhost", int(
                    destiny), message, audio_data)
            else:
                self.send_to_server("localhost", int(destiny), message)

        else:
            next_router = self.next_router(destiny_router)
            next_port = self.network["Ports"][next_router]
            print(f"data forwarded to {next_router}")
            if message == "audio(°_°)":
                client_socket.sendall("send it".encode())
                new_data = client_socket.recv(32768)
                audio_data = new_data
                while True:
                    new_data = client_socket.recv(32768)
                    if not new_data:
                        break
                    audio_data += new_data
                self.send_to_server(
                    "localhost", next_port, data, audio_data)
            else:
                self.send_to_server("localhost", next_port, data)

    def next_router(self, destination):
        """
        Determines the next router for a given destination.

        Parameters
        ----------
            destination : str
                the destination router

        Returns
        -------
            next_router : str
                the next router on the path to the destination
        """

        source = self.router_name

        for dictionary in self.json_routes:
            if dictionary["source"] == source and dictionary["destination"] == destination:
                path = dictionary["path"]
                next_router = path[path.index(source) + 1]
                return next_router
        return None

    def write_json(self, data, filename="Json/paths.json"):
        """
        Writes data to a JSON file.

        Parameters
        ----------
            data : dict
                the data to be written to the file
            filename : str, optional
                the name of the file (default is "paths.json")
        """

        with open(filename, 'w', encoding='utf-8-sig') as file:
            # Convert Python dictionary to JSON and write to file
            json.dump(data, file, indent=4)

    def read_json(self, filename):
        """
        Reads a JSON file and loads the data into a dictionary.

        Parameters
        ----------
            filename : str
                the name of the file

        Returns
        -------
            data: dict
                the json in a dictionary form
        """

        with open(filename, 'r', encoding='utf-8-sig') as file:
            data = json.load(file)
        return data

    def connect_to_controller(self, server_host, server_port):
        """
        Connects to the controller.

        Parameters
        ----------
            server_host : str
                the host address of the server
            server_port : int
                the port number of the server
        """

        # Create a TCP client socket
        controller_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        controller_socket.connect((server_host, server_port))
        controller_socket.sendall(self.router_name.encode())
        print(f"{self.router_name} Waiting for the paths")
        controller_socket.close()

    def send_to_server(self, server_host, server_port, message, audio=None):
        """
        Sends a message to the server.

        Parameters
        ----------
            server_host : str
                the host address of the server
            server_port : int
                the port number of the server
            message : str
                the message to be sent
            audio : Any
                the audio to be sent
        """

        try:
            # Create a TCP client socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the server
            server_socket.connect((server_host, server_port))
            # Send the message to the server
            server_socket.sendall(message.encode())

            if audio is not None:
                server_socket.recv(1024)
                server_socket.sendall(audio)
        finally:
            # Close the client socket
            server_socket.close()


# Example usage
if __name__ == "__main__":
    router = Router()
    router.start()
