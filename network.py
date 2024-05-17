import networkx as nx
import matplotlib.pyplot as plt
from node import Node
from link import Link


class Network:
    """
    A class to represent a network.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the network object.
        """
        self.nodes = {}
        self.links = []
        self.graph = nx.Graph()

    def add_node(self, node_id, name, node_type='router'):
        """
        Adds a node to the network.

        Parameters
        ----------
        node_id : str
            The ID of the node.
        name : str
            The name of the node.
        node_type : str, optional
            The type of the node (default is 'router').
        """

        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, name, node_type)
            self.graph.add_node(name, node_type=node_type)

    def add_link(self, source_id, destination_id, bandwidth):
        """
        Adds a link between two nodes in the network.

        Parameters
        ----------
        source_id : str
            The ID of the source node.
        destination_id : str
            The ID of the destination node.
        bandwidth : int
            The bandwidth of the link.
        """
        if source_id in self.nodes and destination_id in self.nodes:
            self.links.append(
                Link(self.nodes[source_id], self.nodes[destination_id], bandwidth))
            self.graph.add_edge(
                self.nodes[source_id].name, self.nodes[destination_id].name, weight=bandwidth)
        else:
            print("Error: One or both nodes not found in the network.")

    def remove_node(self, node_id):
        """
        Removes a node and its associated links from the network.

        Parameters
        ----------
        node_id : str
            The ID of the node to be removed.
        """
        if node_id in self.nodes:
            node_name = self.nodes[node_id].name
            self.graph.remove_node(node_name)
            del self.nodes[node_id]

            # Remove any links associated with this node
            self.links = [link for link in self.links if
                          link.source.node_id != node_id and link.destination.node_id != node_id]
            print(
                f"Node {node_name} and its associated links have been removed from the network.")
        else:
            print(f"Node ID {node_id} not found in the network.")

    def display_network(self):
        """
        Prints the nodes and links in the network.
        """
        print("Nodes in the network:")
        for node in self.nodes.values():
            print(node)
        print("\nLinks in the network:")
        for link in self.links:
            print(link)

    def visualize_network(self):
        """
        Visualizes the network using matplotlib.
        """
        pos = nx.spring_layout(self.graph)  # positions for all nodes
        nx.draw(self.graph, pos, with_labels=True, node_size=7000,
                node_color="skyblue", font_size=15, font_weight="bold")
        labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels)
        plt.show()

    def visualize_path(self, path):
        """
        Visualizes a specific path in the network.

        Parameters
        ----------
        path : list
            A list of node IDs representing the path.
        """
        pos = nx.spring_layout(self.graph)
        nx.draw(
            self.graph, pos, with_labels=True, node_color='lightblue',
            node_size=500, font_size=10, font_weight='bold'
        )
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_nodes(
            self.graph, pos, nodelist=path, node_color='red')
        nx.draw_networkx_edges(
            self.graph, pos, edgelist=path_edges, edge_color='red', width=2)
        plt.show()
