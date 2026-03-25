import asyncio
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

class NodeState(Enum):
    FOLLOWER = 'FOLLOWER'
    CANDIDATE = 'CANDIDATE'
    LEADER = 'LEADER'

@dataclass
class NodeConfig:
    node_id: str
    peers: Set[str]
    heartbeat_timeout: float = 0.5
    election_timeout_min: float = 1.0
    election_timeout_max: float = 2.0

class SwarmNode:
    def __init__(self, config: NodeConfig):
        self.config = config
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.leader_id: Optional[str] = None
        self.votes_received: Set[str] = set()
        self.last_heartbeat = time.time()
        self.election_timeout = self._random_election_timeout()

    def _random_election_timeout(self) -> float:
        return random.uniform(
            self.config.election_timeout_min,
            self.config.election_timeout_max
        )

    async def run(self):
        while True:
            if self.state == NodeState.FOLLOWER:
                await self._run_follower()
            elif self.state == NodeState.CANDIDATE:
                await self._run_candidate()
            elif self.state == NodeState.LEADER:
                await self._run_leader()

    async def _run_follower(self):
        if time.time() - self.last_heartbeat > self.election_timeout:
            self.state = NodeState.CANDIDATE
            self.current_term += 1
            self.voted_for = self.config.node_id
            self.votes_received = {self.config.node_id}
            await self._request_votes()
        else:
            await asyncio.sleep(0.1)

    async def _run_candidate(self):
        if len(self.votes_received) > len(self.config.peers) / 2:
            self.state = NodeState.LEADER
            self.leader_id = self.config.node_id
            print(f"Node {self.config.node_id} became leader for term {self.current_term}")
        elif time.time() - self.last_heartbeat > self.election_timeout:
            self.current_term += 1
            self.votes_received = {self.config.node_id}
            await self._request_votes()
        else:
            await asyncio.sleep(0.1)

    async def _run_leader(self):
        await self._send_heartbeat()
        await asyncio.sleep(self.config.heartbeat_timeout)

    async def _request_votes(self):
        # Simulate vote requests to peers
        for peer in self.config.peers:
            if random.random() > 0.3:  # 70% chance of successful vote
                self.votes_received.add(peer)

    async def _send_heartbeat(self):
        self.last_heartbeat = time.time()
        # Simulate sending heartbeat to all peers

    async def receive_heartbeat(self, leader_id: str, term: int):
        if term > self.current_term:
            self.current_term = term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
        
        if self.state != NodeState.LEADER:
            self.last_heartbeat = time.time()
            self.leader_id = leader_id

    async def receive_vote_request(self, candidate_id: str, term: int) -> bool:
        if term > self.current_term:
            self.current_term = term
            self.state = NodeState.FOLLOWER
            self.voted_for = None

        if (term == self.current_term and 
            (self.voted_for is None or self.voted_for == candidate_id)):
            self.voted_for = candidate_id
            return True
        return False
