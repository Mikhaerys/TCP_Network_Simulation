# TCP Network Simulation

## About
This project is a simulation of a TCP network implemented in Python. It features a dynamic system of Routers and Clients, along with a Controller that manages the network paths. The simulation is designed to handle message routing within a graph of connected routers, periodically check the routers status, and recalculate routes if any router goes offline. The recalculated paths are then distributed to the remaining routers for efficient message delivery.

## Features
- **Routing System**: Implements Dijkstra and Bellman Ford algorithms for pathfinding.
- **Message Transmission**: Supports sending audio packets and text messages between hosts connected to routers.
- **Fault Detection**: Monitors for node or link failures and recalculates routes accordingly.
- **Encrypted Communication**: Ensures secure communication between routers and the controller, as well as between endpoints in the network.
- **Network Topology**: Utilizes the NFSNET topology for network architecture.
- **Route Visualization**: Allows for the graphical representation of paths between two nodes.

## Installation

Follow these steps to set up the project on your local machine:

1. **Clone the repository**:
   ```sh
   git clone https://github.com/Mikhaerys/TCP_Network_Simulation.git
   cd TCP_Network_Simulation
   ```

2. **Set up a virtual environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the network simulation**:
   - Start the controller:
     ```sh
     python controller.py
     ```
   - Start the routers (in separate terminal windows):
     ```sh
     python router.py
     ```
   - Start the clients (in separate terminal windows):
     ```sh
     python client.py
     ```

## Usage

### Controller

The controller is responsible for:
- Calculating and distributing paths using Dijkstra and Bellman-Ford algorithms.
- Monitoring the status of routers and recalculating paths if a router goes offline.
- Create the network following the architecture specified in network.json
- Storing paths in `paths.json`.

### Routers

Routers handle:
- Managing client connections and storing their addresses in `clients_directory.json`.
- Receiving and forwarding messages based on the paths provided by the controller.

### Clients

Clients can:
- Connect to a specified router.
- Send text messages and audio files to other clients.
- Visualize the path taken by received messages using Matplotlib.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.
