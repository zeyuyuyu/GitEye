from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class ProposalState(Enum):
    DRAFT = 'draft'
    ACTIVE = 'active' 
    VOTING = 'voting'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    EXECUTED = 'executed'

class Proposal:
    def __init__(self, id: str, title: str, description: str, creator: str):
        self.id = id
        self.title = title
        self.description = description
        self.creator = creator
        self.state = ProposalState.DRAFT
        self.created_at = datetime.now()
        self.votes_for = 0
        self.votes_against = 0
        self.voters: List[str] = []
        self.execution_deadline: Optional[datetime] = None
        
    def activate(self) -> bool:
        if self.state == ProposalState.DRAFT:
            self.state = ProposalState.ACTIVE
            return True
        return False
    
    def start_voting(self, voting_period_days: int = 7) -> bool:
        if self.state == ProposalState.ACTIVE:
            self.state = ProposalState.VOTING
            self.execution_deadline = datetime.now() + timedelta(days=voting_period_days)
            return True
        return False

    def cast_vote(self, voter: str, support: bool) -> bool:
        if self.state != ProposalState.VOTING or voter in self.voters:
            return False
        
        if support:
            self.votes_for += 1
        else:
            self.votes_against += 1
            
        self.voters.append(voter)
        return True
    
    def finalize_voting(self) -> bool:
        if self.state != ProposalState.VOTING:
            return False
            
        if datetime.now() < self.execution_deadline:
            return False
            
        if self.votes_for > self.votes_against:
            self.state = ProposalState.APPROVED
        else:
            self.state = ProposalState.REJECTED
        return True

    def execute(self) -> bool:
        if self.state == ProposalState.APPROVED:
            self.state = ProposalState.EXECUTED
            return True
        return False

class GovernanceSystem:
    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self._next_id = 1
        
    def create_proposal(self, title: str, description: str, creator: str) -> Proposal:
        proposal_id = f'PROP-{self._next_id}'
        self._next_id += 1
        
        proposal = Proposal(proposal_id, title, description, creator)
        self.proposals[proposal_id] = proposal
        return proposal
        
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        return self.proposals.get(proposal_id)
        
    def get_active_proposals(self) -> List[Proposal]:
        return [p for p in self.proposals.values() 
                if p.state in (ProposalState.ACTIVE, ProposalState.VOTING)]
    
    def process_expired_proposals(self) -> int:
        processed = 0
        for proposal in self.proposals.values():
            if (proposal.state == ProposalState.VOTING and 
                proposal.execution_deadline and 
                datetime.now() > proposal.execution_deadline):
                if proposal.finalize_voting():
                    processed += 1
        return processed