import os
import time
import random
import subprocess
from src.governance import GovernanceNode

class MainNode:
    def __init__(self):
        self.governance_node = GovernanceNode()
        self.swarm_nodes = []
        self.running = True

    def start(self):
        print("Main node starting...")
        self.governance_node.start()

        while self.running:
            # Manage swarm nodes
            self.manage_swarm()
            time.sleep(10)

    def manage_swarm(self):
        # Check swarm node status
        for node in self.swarm_nodes:
            if not node.is_alive():
                self.swarm_nodes.remove(node)
                print(f"Swarm node {node.id} has stopped. Removing from swarm.")

        # Spawn new swarm nodes if needed
        while len(self.swarm_nodes) < 10:
            new_node = SwarmNode(len(self.swarm_nodes))
            new_node.start()
            self.swarm_nodes.append(new_node)
            print(f"New swarm node {new_node.id} has been added to the swarm.")

class SwarmNode:
    def __init__(self, node_id):
        self.id = node_id
        self.running = True

    def start(self):
        print(f"Swarm node {self.id} starting...")
        subprocess.Popen(["python\