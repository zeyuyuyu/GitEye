#!/usr/bin/env python3

import os
import sys
import subprocess
from typing import Dict, List, Tuple
from dataclasses import dataclass
from colorama import init, Fore, Style

@dataclass
class GitStatus:
    staged: List[str]
    modified: List[str] 
    untracked: List[str]
    current_branch: str
    ahead_behind: Tuple[int, int]

def get_git_status() -> GitStatus:
    """Get comprehensive git repository status"""
    try:
        # Get current branch
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Get staged, modified and untracked files
        status = subprocess.check_output(['git', 'status', '--porcelain']).decode()
        staged, modified, untracked = [], [], []
        
        for line in status.split('\n'):
            if not line: continue
            state, file = line[:2], line[3:]
            if state[0] != ' ': staged.append(file)
            if state[1] != ' ': modified.append(file)
            if state == '??': untracked.append(file)

        # Get ahead/behind counts
        ahead = behind = 0
        try:
            counts = subprocess.check_output(
                ['git', 'rev-list', '--left-right', '--count', f'{branch}...origin/{branch}'],
                stderr=subprocess.DEVNULL
            ).decode()
            ahead, behind = map(int, counts.split())
        except:
            pass

        return GitStatus(
            staged=staged,
            modified=modified,
            untracked=untracked,
            current_branch=branch,
            ahead_behind=(ahead, behind)
        )

    except subprocess.CalledProcessError:
        print(f"{Fore.RED}Not a git repository!{Style.RESET_ALL}")
        sys.exit(1)

def display_status(status: GitStatus) -> None:
    """Display formatted git status"""
    print(f"\n{Fore.CYAN}Current branch:{Style.RESET_ALL} {status.current_branch}")
    
    ahead, behind = status.ahead_behind
    if ahead or behind:
        print(f"{Fore.YELLOW}Branch status:{Style.RESET_ALL}")
        if ahead: print(f"  ↑ {ahead} commit(s) ahead of origin")
        if behind: print(f"  ↓ {behind} commit(s) behind origin")

    if status.staged:
        print(f"\n{Fore.GREEN}Staged changes:{Style.RESET_ALL}")
        for f in status.staged:
            print(f"  + {f}")

    if status.modified:
        print(f"\n{Fore.RED}Modified files:{Style.RESET_ALL}")
        for f in status.modified:
            print(f"  * {f}")

    if status.untracked:
        print(f"\n{Fore.MAGENTA}Untracked files:{Style.RESET_ALL}")
        for f in status.untracked:
            print(f"  ? {f}")

def main():
    init()  # Initialize colorama
    status = get_git_status()
    display_status(status)

if __name__ == '__main__':
    main()