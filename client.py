import json
import pickle
import socket
import threading
from cryptography.fernet import Fernet


class TCPClient:
    """
    A class to work as a client in the network.
    """

    def __init__(self):
        self.router_name = input(
            "write the name of the router to connect to: ")
        self.client_socket = None
        self.client_name = input("Enter your name: ")
        self.client_port = int(input("Enter the client port: "))
        key = b'HcEnve-04K7wN5sgrz1JgKufDMIYBbbTXr0Wueg3v7I='
        self.fernet = Fernet(key)
        self.nsfnet = None

    def connect(self):
        """
        Connect the client to the router and send the messages
        """

        client_reception_thread = threading.Thread(
            target=self.client_reception)
        client_reception_thread.start()

        network = self.read_json("Json/network.json")
        server_port = network["Ports"][self.router_name]
        self.send_to_server("localhost", server_port,
                            f"New Client-{self.client_port}")

        while True:
            destiny = input("Enter the destiny port: ")
            message = input("Enter the message: ")
            clients_directory = self.read_json("Json/clients_directory.json")
            destiny_router = self.destination_router(
                destiny, clients_directory)
            data = "-".join(
                [self.client_name, self.router_name,
                    destiny, destiny_router, message]
            )

            if message == "audio(°_°)":
                audio_name = input(
                    "Enter the name of the audio you want to send: ")
                try:
                    with open(f"Audios to send/{audio_name}", "rb") as file:
                        audio_data = file.read()
                        self.send_to_server(
                            "localhost", server_port, data, audio_data)
                except FileNotFoundError:
                    print("File not found.")
            elif message == "Shutdown":
                self.send_to_server("localhost", server_port, message)
            else:
                self.send_to_server("localhost", server_port, data)

    def client_reception(self):
        """
        It is responsible for receiving all messages that reach the client
        and showing the path the message followed.
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind(("localhost", self.client_port))
        self.client_socket.listen(5)
        while True:
            new_socket, _ = self.client_socket.accept()
            data = self.fernet.decrypt(new_socket.recv(1024)).decode()
            source, source_router, _, _, message = data.split("-")
            print(f"\n{source}: {message}")

            json_paths = self.read_json("Json/paths.json")
            for paths in json_paths:
                if paths["source"] == source_router and paths["destination"] == self.router_name:
                    path = paths["path"]

            if message == "audio(°_°)":
                new_socket.sendall(self.fernet.encrypt("send it".encode()))

                with open("Audios received/audio_copia.wav", "wb") as file:
                    while True:
                        audio_data = new_socket.recv(32768)
                        if not audio_data:
                            break
                        file.write(audio_data)
                print("Received audio")

            self.get_nsfnet()
            self.nsfnet.visualize_path(path)

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

    def destination_router(self, port, json_data):
        """
        Find which router a certain client is connected to

        Parameters
        ----------
            port : int
                the client port to which a message is to be sent

            json_data: dict
                the json dictionary containing the client directory

        Returns
        -------
            router: str
                name of the router to which that client is connected
        """

        for router, clients in json_data.items():
            if port in clients:
                return router
        return "None"

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
            server_socket.sendall(self.fernet.encrypt(message.encode()))

            if audio is not None:
                server_socket.recv(1024)
                server_socket.sendall(audio)
        finally:
            # Close the client socket
            server_socket.close()

    def get_nsfnet(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(("localhost", 8888))
        server_socket.sendall(self.fernet.encrypt("nsfnet".encode()))
        self.nsfnet = pickle.loads(server_socket.recv(32768))
        server_socket.close()


# Example usage
if __name__ == "__main__":
    server_client = TCPClient()
    server_client.connect()
