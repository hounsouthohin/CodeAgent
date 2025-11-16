"""
Outils d'exécution de code sécurisée.
Utilise RestrictedPython pour le sandboxing et subprocess pour l'isolation.
"""
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CodeExecutionTool:
    """Outil d'exécution de code sécurisée."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        """Définition de l'outil pour Ollama."""
        return {
            "name": "run_python_code",
            "description": "Execute Python code safely in a sandboxed environment. Returns stdout, stderr, and exit code. Use this to TEST if your code corrections actually work!",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 5)",
                        "default": Config.EXECUTION_TIMEOUT
                    }
                },
                "required": ["code"]
            }
        }
    
    @staticmethod
    def execute(code: str, timeout: int = None) -> str:
        """
        Exécute du code Python de manière sécurisée.
        
        Args:
            code: Code Python à exécuter
            timeout: Timeout en secondes
            
        Returns:
            Résultat de l'exécution (stdout/stderr)
        """
        if not Config.CODE_EXECUTION_ENABLED:
            return "❌ Code execution is disabled in configuration"
        
        if timeout is None:
            timeout = Config.EXECUTION_TIMEOUT
        
        logger.info(f"Executing code (timeout: {timeout}s)")
        
        try:
            # Méthode 1: RestrictedPython (pour code simple)
            if Config.SANDBOX_ENABLED and len(code) < 500:
                return CodeExecutionTool._execute_restricted(code)
            
            # Méthode 2: Subprocess (pour code complexe)
            return CodeExecutionTool._execute_subprocess(code, timeout)
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"❌ Execution error: {str(e)}"
    
    @staticmethod
    def _execute_restricted(code: str) -> str:
        """Exécution avec RestrictedPython (sandboxing)."""
        try:
            # Compiler le code en mode restreint
            byte_code = compile_restricted(
                code,
                filename='<inline>',
                mode='exec'
            )
            
            if byte_code.errors:
                return f"❌ Compilation errors:\n" + "\n".join(byte_code.errors)
            
            # Environnement restreint
            restricted_globals = {
                '__builtins__': safe_builtins,
                '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
                '_getiter_': iter,
            }
            
            # Capturer stdout
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                exec(byte_code.code, restricted_globals)
                output = captured_output.getvalue()
                return f"✅ Execution successful:\n{output}" if output else "✅ Execution successful (no output)"
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            return f"❌ Runtime error: {str(e)}"
    
    @staticmethod
    def _execute_subprocess(code: str, timeout: int) -> str:
        """Exécution avec subprocess (isolation processus)."""
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                temp_file = Path(f.name)
            
            try:
                # Exécuter dans un processus isolé
                result = subprocess.run(
                    ['python3', str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd='/tmp',  # Exécuter dans /tmp pour isolation
                )
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    return f"✅ Execution successful:\n{output}" if output else "✅ Execution successful (no output)"
                else:
                    return f"❌ Execution failed (exit code {result.returncode}):\n{result.stderr}"
                    
            finally:
                # Nettoyer le fichier temporaire
                temp_file.unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            return f"⏱️ Execution timed out after {timeout}s"
        except Exception as e:
            return f"❌ Subprocess error: {str(e)}"


class SyntaxCheckTool:
    """Outil de vérification de syntaxe."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "check_syntax",
            "description": "Check if Python code has valid syntax WITHOUT executing it. Fast and safe way to validate code structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to check"
                    }
                },
                "required": ["code"]
            }
        }
    
    @staticmethod
    def execute(code: str) -> str:
        """Vérifie la syntaxe du code."""
        try:
            compile(code, '<string>', 'exec')
            return "✅ Syntax is valid"
        except SyntaxError as e:
            return f"❌ Syntax error at line {e.lineno}, column {e.offset}:\n{e.msg}\n{e.text}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"


class TestRunnerTool:
    """Outil d'exécution de tests pytest."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "run_tests",
            "description": "Run pytest tests on a file or directory. Returns test results, coverage, and failures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to test file or directory"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Show detailed output",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        }
    
    @staticmethod
    def execute(path: str, verbose: bool = False) -> str:
        """Exécute les tests pytest."""
        try:
            test_path = Config.APP_PATH / path
            
            if not test_path.exists():
                return f"❌ Test path not found: {path}"
            
            # Construire la commande pytest
            cmd = ['pytest', str(test_path), '--tb=short']
            if verbose:
                cmd.append('-v')
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=Config.TOOL_TIMEOUT,
                cwd=str(Config.APP_PATH)
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                return f"✅ All tests passed:\n{output}"
            else:
                return f"❌ Some tests failed:\n{output}"
                
        except subprocess.TimeoutExpired:
            return f"⏱️ Tests timed out after {Config.TOOL_TIMEOUT}s"
        except Exception as e:
            return f"❌ Test execution error: {str(e)}"