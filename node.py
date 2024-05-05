class Node:
    def __init__(self, node_id, name, node_type='router'):
        self.node_id = node_id
        self.name = name
        self.node_type = node_type

    def __repr__(self):
        return f"Node({self.name}, ID={self.node_id}, Type={self.node_type})"
