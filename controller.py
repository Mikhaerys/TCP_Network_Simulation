import time
import json
import socket
import threading
import networkx as nx
from cryptography.fernet import Fernet
from network import Network


class Controller:
    """
    A class to represent a controller for network routing.
    """

    def __init__(self, port):
        """
        Constructs all the necessary attributes for the controller object.

        Parameters
        ----------
            host : str
                The host address of the controller.
            port : int
                The port number of the controller.
        """
        self.port = port
        self.the_json = []
        self.nsfnet = Network()
        self.network = self.read_json("Json/network.json")
        key = b'HcEnve-04K7wN5sgrz1JgKufDMIYBbbTXr0Wueg3v7I='
        self.fernet = Fernet(key)
        self.routers_quantity = 0

    def start(self):
        """
        Starts the controller and listens for incoming connections.
        """
        # Create a TCP server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the address and port
        server_socket.bind(("localhost", self.port))
        # Listen for incoming connections
        server_socket.listen(5)
        print(f"Server listening on localhost: {self.port}...")
        total_routers = len(self.network["Ports"])

        while True:
            # Accept a new connection
            router_socket, _ = server_socket.accept()

            if self.routers_quantity < total_routers:
                router_name = self.fernet.decrypt(
                    router_socket.recv(1024).decode())
                node_id = self.network["Nodes"][router_name]
                self.nsfnet.add_node(node_id, router_name)
                self.routers_quantity += 1

            if self.routers_quantity == total_routers:
                for link in self.network["Links"]:
                    from_node = link["from"]
                    to_node = link["to"]
                    distance = link["distance"]
                    self.nsfnet.add_link(from_node, to_node, distance)

                node_ports = self.network["Ports"].values()
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
        router_socket.sendall(self.fernet.encrypt("New Path".encode()))
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
            server_socket.sendall(self.fernet.encrypt(message.encode()))
            # Receive a response from the server
            server_response = self.fernet.decrypt(
                server_socket.recv(1024).decode())
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
        Checks the status of all nodes in the network and updates the shortest paths 
        if a node is down.
        """
        while True:
            time.sleep(10)
            node_ports = list(self.network["Ports"].values())
            for port in node_ports:
                status = self.send_to_server(
                    "localhost", port, "ACK")
                if status == "no response":
                    node_id = node_ports.index(port) + 1
                    self.nsfnet.remove_node(node_id)
                    self.routers_quantity -= 1
                    json_to_send = self.compute_all_shortest_paths(self.nsfnet)

                    for good_port in node_ports:
                        if good_port != port:
                            path_thread = threading.Thread(
                                target=self.send_shortest_paths, args=(good_port, json_to_send))
                            path_thread.start()

            print("check completed")

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


if __name__ == "__main__":
    controller = Controller(8888)
    controller.start()
