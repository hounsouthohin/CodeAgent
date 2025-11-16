"""
Outils pour opérations Git.
Analyse les diffs, l'historique, et aide à comprendre les changements.
"""
import subprocess
from pathlib import Path
from typing import Dict, Any
from git import Repo, GitCommandError

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class GitDiffTool:
    """Voir les différences entre commits."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "git_diff",
            "description": "Show changes between commits, branches, or working directory. Useful to understand what changed and why code might have broken.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "What to diff (e.g., 'HEAD', 'HEAD~1', 'main', or file path)",
                        "default": "HEAD"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Specific file to diff (optional)"
                    }
                },
                "required": []
            }
        }
    
    @staticmethod
    def execute(target: str = "HEAD", file_path: str = None) -> str:
        """Affiche le diff Git."""
        try:
            repo = Repo(Config.APP_PATH)
            
            if repo.is_dirty(untracked_files=True):
                # Changements non committés
                if file_path:
                    diff = repo.git.diff(file_path)
                else:
                    diff = repo.git.diff()
                
                if not diff:
                    return "✅ No changes in working directory"
                
                return f"📝 Changes in working directory:\n\n{diff[:1000]}"
            
            # Diff entre commits
            if file_path:
                diff = repo.git.diff(target, file_path)
            else:
                diff = repo.git.diff(target)
            
            if not diff:
                return f"✅ No differences found for {target}"
            
            return f"📝 Diff for {target}:\n\n{diff[:1000]}"
            
        except GitCommandError as e:
            return f"❌ Git error: {str(e)}"
        except Exception as e:
            logger.error(f"Git diff error: {e}")
            return f"❌ Error: {str(e)}"


class GitHistoryTool:
    """Voir l'historique des commits."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "git_history",
            "description": "View commit history for a file or project. Helps understand when bugs were introduced or how code evolved.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File to get history for (optional, shows all if not provided)"
                    },
                    "max_count": {
                        "type": "integer",
                        "description": "Number of commits to show",
                        "default": 10
                    }
                },
                "required": []
            }
        }
    
    @staticmethod
    def execute(file_path: str = None, max_count: int = 10) -> str:
        """Affiche l'historique Git."""
        try:
            repo = Repo(Config.APP_PATH)
            
            # Récupérer les commits
            if file_path:
                commits = list(repo.iter_commits(paths=file_path, max_count=max_count))
            else:
                commits = list(repo.iter_commits(max_count=max_count))
            
            if not commits:
                return "📝 No commits found"
            
            output = f"📜 Last {len(commits)} commits"
            if file_path:
                output += f" for {file_path}"
            output += ":\n\n"
            
            for i, commit in enumerate(commits, 1):
                output += f"{i}. [{commit.hexsha[:7]}] {commit.summary}\n"
                output += f"   Author: {commit.author.name}\n"
                output += f"   Date: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            return output
            
        except GitCommandError as e:
            return f"❌ Git error: {str(e)}"
        except Exception as e:
            logger.error(f"Git history error: {e}")
            return f"❌ Error: {str(e)}"


class GitStatusTool:
    """Voir le statut du repo."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "git_status",
            "description": "Check repository status: modified files, untracked files, current branch. Use before committing changes.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    
    @staticmethod
    def execute() -> str:
        """Affiche le statut Git."""
        try:
            repo = Repo(Config.APP_PATH)
            
            output = f"🌿 Current branch: {repo.active_branch.name}\n\n"
            
            # Fichiers modifiés
            if repo.is_dirty():
                modified = [item.a_path for item in repo.index.diff(None)]
                if modified:
                    output += "📝 Modified files:\n"
                    for f in modified:
                        output += f"  - {f}\n"
                    output += "\n"
            
            # Fichiers staged
            staged = [item.a_path for item in repo.index.diff("HEAD")]
            if staged:
                output += "✅ Staged files:\n"
                for f in staged:
                    output += f"  - {f}\n"
                output += "\n"
            
            # Fichiers non trackés
            untracked = repo.untracked_files
            if untracked:
                output += "❓ Untracked files:\n"
                for f in untracked[:10]:  # Limiter à 10
                    output += f"  - {f}\n"
                if len(untracked) > 10:
                    output += f"  ... and {len(untracked) - 10} more\n"
                output += "\n"
            
            if not repo.is_dirty() and not staged and not untracked:
                output += "✅ Working directory clean\n"
            
            return output
            
        except Exception as e:
            logger.error(f"Git status error: {e}")
            return f"❌ Error: {str(e)}"