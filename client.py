import json
import socket
import threading


class TCPClient:
    def __init__(self, server_host):
        self.server_host = server_host
        self.server_port = int(
            input("write the port of the router to connect to: "))
        self.client_socket = None
        self.client_port = int(input("Write the client port: "))

    def connect(self):

        client_reception_thread = threading.Thread(
            target=self.client_reception)
        client_reception_thread.start()

        self.send_to_server(self.server_host, self.server_port,
                            f"New Client-{self.client_port}")

        while True:
            destiny = input("Enter the destiny port: ")
            message = input("Enter the message: ")
            clients_directory = self.read_json("clients_directory.json")
            destiny_router = self.destination_router(
                destiny, clients_directory)
            data = "-".join([destiny, destiny_router, message])

            if message == "audio(°_°)":
                with open("audio_to_send.wav", "rb") as file:
                    audio_data = file.read()
                    self.send_to_server(
                        self.server_host, self.server_port, data, audio_data)
            else:
                self.send_to_server(self.server_host, self.server_port, data)

    def client_reception(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind((self.server_host, self.client_port))
        self.client_socket.listen(5)
        while True:
            new_socket, _ = self.client_socket.accept()
            message = new_socket.recv(1024).decode()
            print("\n   New message: " + message)
            if message == "audio(°_°)":
                new_socket.sendall("send it".encode())
                with open("audio_copia.wav", "wb") as file:
                    while True:
                        audio_data = new_socket.recv(32768)
                        if not audio_data:
                            break
                        file.write(audio_data)

    def close(self):
        # Close the client socket
        self.client_socket.close()

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
        for router, clients in json_data.items():
            if port in clients:
                return router
        return "the"

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
    server_client = TCPClient("localhost")
    server_client.connect()
