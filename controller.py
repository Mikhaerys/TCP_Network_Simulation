import time
import json
import socket
import threading
import networkx as nx
from network import Network
from cryptography.fernet import Fernet


class Controller:
    """
    A class to represent a controller for network routing.
    """

    def __init__(self, host, port):
        """
        Constructs all the necessary attributes for the controller object.

        Parameters
        ----------
            host : str
                The host address of the controller.
            port : int
                The port number of the controller.
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.the_json = []
        self.nsfnet = Network()
        self.routers_ports = {
            "node1": 9001, "node2": 9002, "node3": 9003, "node4": 9004
        }

        key = b'HcEnve-04K7wN5sgrz1JgKufDMIYBbbTXr0Wueg3v7I='
        self.fernet = Fernet(key)

    def start(self):
        """
        Starts the controller and listens for incoming connections.
        """
        # Create a TCP server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the address and port
        self.server_socket.bind((self.host, self.port))
        # Listen for incoming connections
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}...")
        clients_number = 0

        while True:
            # Accept a new connection
            self.server_socket.accept()

            if clients_number < 4:
                clients_number += 1
                node_name = f'node{clients_number}'
                self.nsfnet.add_node(clients_number, node_name)

            if clients_number == 4:
                self.nsfnet.add_link(1, 2, 1/3)
                self.nsfnet.add_link(2, 3, 1/1)
                self.nsfnet.add_link(3, 4, 1/1)
                self.nsfnet.add_link(4, 1, 1/2)
                self.nsfnet.add_link(2, 4, 1/3)

                node_ports = self.routers_ports.values()
                json_to_send = self.compute_all_shortest_paths(self.nsfnet)

                for port in node_ports:
                    path_thread = threading.Thread(
                        target=self.send_shortest_paths, args=(port, json_to_send))
                    path_thread.start()

                print("Starting node status checking")
                ack_thread = threading.Thread(target=self.check_nodes_status)
                ack_thread.start()

    def compute_all_shortest_paths(self, network, algorithm='dijkstra'):
        """
        Computes all shortest paths in the network and stores them in JSON format.

        Parameters
        ----------
        network : NetworkX graph
            The network graph.
        algorithm : str, optional
            The algorithm to use for computing shortest paths.
            Options: 'dijkstra' or 'bellman_ford'. Default is 'dijkstra'.

        Returns
        -------
        json_to_send : str
            A JSON string representing all shortest paths in the network.
        """
        self.the_json = []
        if algorithm == 'dijkstra':
            all_paths = dict(nx.all_pairs_dijkstra_path(network.graph))
        elif algorithm == 'bellman_ford':
            all_paths = dict(nx.all_pairs_bellman_ford_path(network.graph))
        else:
            raise ValueError(
                "Invalid algorithm specified. Use 'dijkstra' or 'bellman_ford'.")

        for source, destinations in all_paths.items():
            for destination, path in destinations.items():
                self.the_json.append(
                    {
                        "source": source,
                        "destination": destination,
                        "path": path
                    }
                )
        json_to_send = json.dumps(self.the_json)
        return json_to_send

    def send_shortest_paths(self, port, json_to_send):
        """
        Sends the shortest paths information to a router at the specified port.

        Parameters
        ----------
        port : int
            The port number of the router to which the shortest paths information
            will be sent.

        json_to_send : str
            The JSON-formatted string containing the shortest paths information
            to be sent.
        """
        router_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        router_socket.connect(("localhost", port))
        router_socket.sendall("New Path".encode())
        router_socket.sendall(self.fernet.encrypt(json_to_send.encode()))
        router_socket.close()
        print("Paths sended")

    def send_to_server(self, server_host, server_port, message):
        """
        Sends a message to the server and returns the response.

        Parameters
        ----------
            server_host : str
                The host address of the server.
            server_port : int
                The port number of the server.
            message : str
                The message to be sent to the server.

        Returns
        -------
            server_response : str
                The response from the server.
        """
        try:
            # Create a TCP client socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the server
            server_socket.connect((server_host, server_port))
            # Send the message to the server
            server_socket.sendall(message.encode())
            # Receive a response from the server
            server_response = server_socket.recv(1024).decode()
            server_socket.close()
            return server_response
        except ConnectionRefusedError:
            server_socket.close()
            return "no response"
        finally:
            # Close the client socket
            server_socket.close()

    def check_nodes_status(self):
        """
        Checks the status of all nodes in the network and updates the shortest paths if a node is down.
        """
        while True:
            time.sleep(10)
            node_ports = list(self.routers_ports.values())
            for port in node_ports:
                status = self.send_to_server(
                    "localhost", port, "ACK")
                if status == "no response":
                    node_id = node_ports.index(port) + 1
                    self.nsfnet.remove_node(node_id)
                    json_to_send = self.compute_all_shortest_paths(self.nsfnet)

                    for good_port in node_ports:
                        if good_port != port:
                            path_thread = threading.Thread(
                                target=self.send_shortest_paths, args=(good_port, json_to_send))
                            path_thread.start()

            print("check completed")


if __name__ == "__main__":
    controller = Controller("localhost", 8888)
    controller.start()
