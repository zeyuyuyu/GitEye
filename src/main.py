#!/usr/bin/env python3

import os
import subprocess
from typing import Dict, List, Optional

class GitEye:
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        if not os.path.exists(os.path.join(repo_path, '.git')):
            raise ValueError(f'Not a git repository: {repo_path}')

    def _run_git_command(self, command: List[str]) -> str:
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Git command failed: {e.stderr}')

    def get_repo_status(self) -> Dict[str, any]:
        """Get comprehensive repository status information."""
        status = {
            'current_branch': self.get_current_branch(),
            'all_branches': self.get_branches(),
            'modified_files': self.get_modified_files(),
            'untracked_files': self.get_untracked_files(),
            'ahead_behind': self.get_ahead_behind()
        }
        return status

    def get_current_branch(self) -> str:
        """Get name of current branch."""
        return self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])

    def get_branches(self) -> List[str]:
        """Get list of all branches."""
        branches = self._run_git_command(['branch', '--list'])
        return [b.strip('* ') for b in branches.split('\n') if b]

    def get_modified_files(self) -> List[str]:
        """Get list of modified files in working directory."""
        status = self._run_git_command(['status', '--porcelain'])
        modified = []
        for line in status.split('\n'):
            if line and line[1] == 'M':
                modified.append(line[3:])
        return modified

    def get_untracked_files(self) -> List[str]:
        """Get list of untracked files."""
        status = self._run_git_command(['status', '--porcelain'])
        untracked = []
        for line in status.split('\n'):
            if line.startswith('??'):
                untracked.append(line[3:])
        return untracked

    def get_ahead_behind(self) -> Dict[str, int]:
        """Get number of commits ahead/behind remote."""
        try:
            status = self._run_git_command(['rev-list', '--left-right', '--count', 'HEAD...@{upstream}'])
            ahead, behind = map(int, status.split())
            return {'ahead': ahead, 'behind': behind}
        except RuntimeError:
            return {'ahead': 0, 'behind': 0}

def main():
    try:
        repo = GitEye('.')
        status = repo.get_repo_status()
        print('Repository Status:')
        print(f"Current branch: {status['current_branch']}")
        print(f"All branches: {', '.join(status['all_branches'])}")
        print(f"Modified files: {', '.join(status['modified_files']) or 'None'}")
        print(f"Untracked files: {', '.join(status['untracked_files']) or 'None'}")
        print(f"Commits ahead: {status['ahead_behind']['ahead']}")
        print(f"Commits behind: {status['ahead_behind']['behind']}")
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == '__main__':
    main()
