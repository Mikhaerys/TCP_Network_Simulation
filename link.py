class Link:
    def __init__(self, source, destination, bandwidth):
        self.source = source
        self.destination = destination
        self.bandwidth = bandwidth

    def __repr__(self):
        return f"Link({self.source} -> {self.destination}, Bandwidth={self.bandwidth} Gbps)"