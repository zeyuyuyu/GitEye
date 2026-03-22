import os
from typing import List, Dict
from transformers import AutoModelForSequenceClassification
from git import Repo
from pathlib import Path

class GitEye:
    def __init__(self, repo_path: str):
        self.repo = Repo(repo_path)
        self.model = AutoModelForSequenceClassification.from_pretrained('giteye/code-analyzer-v1')
        
    def analyze_diff(self, commit_hash: str) -> Dict:
        """Analyzes a git diff using the AI model"""
        diff = self.repo.git.diff(commit_hash)
        return self._process_diff(diff)
    
    def _process_diff(self, diff: str) -> Dict:
        """Processes diff content using transformer model"""
        predictions = self.model(diff)
        return {
            'technical_debt_score': predictions.debt_score,
            'security_issues': predictions.security_findings,
            'refactoring_suggestions': predictions.refactor_hints
        }

def main():
    eye = GitEye(os.getcwd())
    results = eye.analyze_diff('HEAD')
    print(f'Analysis complete: {results}')

if __name__ == '__main__':
    main()