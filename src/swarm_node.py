import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Set

class SwarmNode:
    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        self.host = host
        self.port = port
        self.node_id = str(uuid.uuid4())
        self.peers: Dict[str, dict] = {}
        self.active_nodes: Set[str] = set()
        self.last_heartbeat = {}
        self.is_running = False

    async def start(self):
        """Start the SwarmNode and begin peer discovery"""
        self.is_running = True
        self.server = await asyncio.start_server(
            self.handle_connection, self.host, self.port
        )
        asyncio.create_task(self.heartbeat_monitor())
        print(f'SwarmNode {self.node_id} listening on {self.host}:{self.port}')

    async def handle_connection(self, reader, writer):
        """Handle incoming peer connections"""
        data = await reader.read(1024)
        message = json.loads(data.decode())
        
        if message['type'] == 'discovery':
            await self.handle_discovery(message, writer)
        elif message['type'] == 'heartbeat':
            await self.handle_heartbeat(message)

        writer.close()
        await writer.wait_closed()

    async def handle_discovery(self, message: dict, writer):
        """Process new peer discovery requests"""
        peer_id = message['node_id']
        peer_addr = message['address']
        
        if peer_id not in self.peers:
            self.peers[peer_id] = {
                'address': peer_addr,
                'last_seen': datetime.now().isoformat()
            }
            print(f'New peer discovered: {peer_id}')

        response = {
            'type': 'discovery_ack',
            'node_id': self.node_id,
            'peers': self.peers
        }
        writer.write(json.dumps(response).encode())
        await writer.drain()

    async def handle_heartbeat(self, message: dict):
        """Update peer last seen timestamp"""
        peer_id = message['node_id']
        self.last_heartbeat[peer_id] = datetime.now().isoformat()
        self.active_nodes.add(peer_id)

    async def send_heartbeat(self):
        """Send heartbeat to all known peers"""
        message = {
            'type': 'heartbeat',
            'node_id': self.node_id,
            'timestamp': datetime.now().isoformat()
        }

        for peer_id, peer_info in self.peers.items():
            try:
                reader, writer = await asyncio.open_connection(
                    *peer_info['address'].split(':')
                )
                writer.write(json.dumps(message).encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f'Failed to send heartbeat to {peer_id}: {e}')

    async def heartbeat_monitor(self):
        """Monitor peer heartbeats and remove inactive nodes"""
        while self.is_running:
            await self.send_heartbeat()
            
            # Remove peers that haven't sent a heartbeat in 30 seconds
            now = datetime.now()
            inactive = set()
            
            for peer_id, last_seen in self.last_heartbeat.items():
                last_seen_time = datetime.fromisoformat(last_seen)
                if (now - last_seen_time).seconds > 30:
                    inactive.add(peer_id)

            for peer_id in inactive:
                self.active_nodes.remove(peer_id)
                del self.last_heartbeat[peer_id]
                del self.peers[peer_id]
                print(f'Peer {peer_id} removed due to inactivity')

            await asyncio.sleep(5)

    async def stop(self):
        """Stop the SwarmNode"""
        self.is_running = False
        self.server.close()
        await self.server.wait_closed()