import time
import random
from swarm_node import SwarmNode

class SwarmCoordinator:
    def __init__(self, num_nodes):
        self.nodes = [SwarmNode() for _ in range(num_nodes)]
        self.leader = random.choice(self.nodes)

    def coordinate_swarm(self):
        while True:
            for node in self.nodes:
                if node == self.leader:
                    self.leader.broadcast_instructions(self.nodes)
                else:
                    node.execute_instructions(self.leader.instructions)
            time.sleep(1)

if __name__ == '__main__':
    coordinator = SwarmCoordinator(10)
    coordinator.coordinate_swarm()