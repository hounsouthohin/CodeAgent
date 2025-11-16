"""
Outils de profiling et optimisation de performance.
"""
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ProfilerTool:
    """Profile l'exécution du code pour trouver les bottlenecks."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "profile_code",
            "description": "Profile code execution to find performance bottlenecks. Shows which functions take the most time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to profile"
                    }
                },
                "required": ["code"]
            }
        }
    
    @staticmethod
    def execute(code: str) -> str:
        """Profile le code avec cProfile."""
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                temp_file = Path(f.name)
            
            try:
                # Exécuter avec cProfile
                result = subprocess.run(
                    ['python3', '-m', 'cProfile', '-s', 'cumulative', str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=Config.TOOL_TIMEOUT
                )
                
                if result.returncode != 0:
                    return f"❌ Profiling failed:\n{result.stderr}"
                
                # Parser les résultats pour garder les plus importantes
                lines = result.stdout.split('\n')
                
                # Garder l'en-tête et les 15 premières fonctions
                header_lines = [l for l in lines[:10] if l.strip()]
                function_lines = [l for l in lines[10:25] if l.strip()]
                
                output = "⚡ Performance Profile:\n\n"
                output += "Top functions by cumulative time:\n"
                output += "\n".join(header_lines[:5]) + "\n"
                output += "\n".join(function_lines[:10])
                
                return output
                
            finally:
                temp_file.unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            return f"⏱️ Profiling timed out after {Config.TOOL_TIMEOUT}s"
        except Exception as e:
            logger.error(f"Profiling error: {e}")
            return f"❌ Profiling error: {str(e)}"


class MemoryProfilerTool:
    """Profile l'utilisation mémoire."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "profile_memory",
            "description": "Profile memory usage to find memory leaks or high memory consumption. Shows memory used per line.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to profile for memory"
                    }
                },
                "required": ["code"]
            }
        }
    
    @staticmethod
    def execute(code: str) -> str:
        """Profile la mémoire avec memory_profiler."""
        try:
            # Ajouter le décorateur @profile si nécessaire
            if '@profile' not in code:
                # Trouver la première fonction et ajouter @profile
                lines = code.split('\n')
                modified_lines = []
                added_decorator = False
                
                for line in lines:
                    if line.strip().startswith('def ') and not added_decorator:
                        modified_lines.append('@profile')
                        added_decorator = True
                    modified_lines.append(line)
                
                code = '\n'.join(modified_lines)
            
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                temp_file = Path(f.name)
            
            try:
                result = subprocess.run(
                    ['python3', '-m', 'memory_profiler', str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=Config.TOOL_TIMEOUT
                )
                
                if result.returncode != 0:
                    return f"❌ Memory profiling failed:\n{result.stderr}"
                
                output = "💾 Memory Profile:\n\n"
                output += result.stdout[:1000]  # Limiter la sortie
                
                # Analyse rapide
                if 'MiB' in result.stdout:
                    lines = result.stdout.split('\n')
                    memory_lines = [l for l in lines if 'MiB' in l]
                    if memory_lines:
                        output += "\n\n📊 High memory lines:\n"
                        # Trier par usage mémoire (approximatif)
                        sorted_lines = sorted(memory_lines, key=lambda x: x, reverse=True)[:5]
                        output += "\n".join(sorted_lines)
                
                return output
                
            finally:
                temp_file.unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            return f"⏱️ Memory profiling timed out after {Config.TOOL_TIMEOUT}s"
        except Exception as e:
            logger.error(f"Memory profiling error: {e}")
            return f"❌ Memory profiling error: {str(e)}"