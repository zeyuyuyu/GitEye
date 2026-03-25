import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import random
import time

@dataclass
class NodeState:
    node_id: str
    peers: Dict[str, 'SwarmNode']
    leader: Optional[str] = None
    term: int = 0
    heartbeat_timeout: float = 5.0
    last_heartbeat: float = 0.0

class SwarmNode:
    def __init__(self, node_id: str):
        self.state = NodeState(
            node_id=node_id,
            peers={},
        )
        self.is_active = False

    async def start(self):
        """Start the node's main loop"""
        self.is_active = True
        await asyncio.gather(
            self.heartbeat_loop(),
            self.election_loop()
        )

    async def stop(self):
        """Stop the node"""
        self.is_active = False

    def add_peer(self, peer: 'SwarmNode'):
        """Add a peer node to the swarm"""
        self.state.peers[peer.state.node_id] = peer

    async def heartbeat_loop(self):
        """Maintain leadership through periodic heartbeats"""
        while self.is_active:
            if self.state.leader == self.state.node_id:
                await self.broadcast_heartbeat()
            await asyncio.sleep(1.0)

    async def election_loop(self):
        """Monitor leader health and trigger elections"""
        while self.is_active:
            now = time.time()
            if (self.state.leader and 
                now - self.state.last_heartbeat > self.state.heartbeat_timeout):
                await self.start_election()
            await asyncio.sleep(1.0)

    async def broadcast_heartbeat(self):
        """Send heartbeat to all peers"""
        for peer in self.state.peers.values():
            await peer.receive_heartbeat(
                from_node=self.state.node_id,
                term=self.state.term
            )

    async def receive_heartbeat(self, from_node: str, term: int):
        """Process incoming heartbeat"""
        if term >= self.state.term:
            self.state.leader = from_node
            self.state.term = term
            self.state.last_heartbeat = time.time()

    async def start_election(self):
        """Begin leader election process"""
        self.state.term += 1
        self.state.leader = None
        votes = 1  # Vote for self

        # Request votes from peers
        for peer in self.state.peers.values():
            if await peer.request_vote(
                candidate_id=self.state.node_id,
                term=self.state.term
            ):
                votes += 1

        # Become leader if majority
        if votes > (len(self.state.peers) + 1) / 2:
            self.state.leader = self.state.node_id
            await self.broadcast_heartbeat()

    async def request_vote(self, candidate_id: str, term: int) -> bool:
        """Process vote request from peer"""
        if term > self.state.term and not self.state.leader:
            self.state.term = term
            self.state.leader = None
            return True
        return False

    def get_status(self) -> Dict:
        """Return current node status"""
        return {
            'node_id': self.state.node_id,
            'leader': self.state.leader,
            'term': self.state.term,
            'peer_count': len(self.state.peers)
        }