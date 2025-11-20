"""
Outil d'exécution de code multi-langage.
"""
import subprocess
import tempfile
from pathlib import Path
from typing import Dict
from .base_tool import BaseTool
import sys
sys.path.append('/app')
from utils import setup_logger, Config

logger = setup_logger(__name__)

class CodeExecutionTool(BaseTool):
    """Exécute du code dans différents langages."""
    
    EXECUTORS = {
        'python': 'python',
        'javascript': 'node',
        'typescript': 'ts-node',
        'java': 'java',
        'go': 'go run',
    }
    
    EXTENSIONS = {
        'python': '.py',
        'javascript': '.js',
        'typescript': '.ts',
        'java': '.java',
        'go': '.go',
    }
    
    @staticmethod
    def get_tool_definition() -> Dict:
        return {
            'name': 'run_code',
            'description': 'Execute code in Python, JavaScript, TypeScript, Java, or Go',
            'parameters': {
                'code': 'Code to execute',
                'language': 'Language (python/javascript/typescript/java/go)'
            }
        }
    
    @staticmethod
    def execute(code: str, language: str = 'python') -> str:
        """
        Exécute du code dans le langage spécifié.
        
        Args:
            code: Code à exécuter
            language: Langage de programmation
            
        Returns:
            Résultat de l'exécution
        """
        if not Config.CODE_EXECUTION_ENABLED:
            return "❌ Code execution is disabled"
        
        if language not in CodeExecutionTool.EXECUTORS:
            return f"❌ Language '{language}' not supported. Available: {list(CodeExecutionTool.EXECUTORS.keys())}"
        
        try:
            logger.info(f"🚀 Executing {language} code...")
            
            # Créer un fichier temporaire
            ext = CodeExecutionTool.EXTENSIONS[language]
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=ext,
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                temp_path = f.name
            
            # Exécuter
            executor = CodeExecutionTool.EXECUTORS[language]
            result = subprocess.run(
                f"{executor} {temp_path}".split(),
                capture_output=True,
                text=True,
                timeout=Config.EXECUTION_TIMEOUT
            )
            
            # Nettoyer
            Path(temp_path).unlink(missing_ok=True)
            
            if result.returncode == 0:
                return f"✅ Execution successful:\n{result.stdout}"
            else:
                return f"❌ Execution failed:\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"⏱️ Timeout after {Config.EXECUTION_TIMEOUT}s"
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"❌ Error: {str(e)}"


class SyntaxCheckTool(BaseTool):
    """Vérifie la syntaxe du code."""
    
    @staticmethod
    def get_tool_definition() -> Dict:
        return {
            'name': 'check_syntax',
            'description': 'Check if code has valid syntax',
            'parameters': {
                'code': 'Code to check',
                'language': 'Language (python/javascript/etc.)'
            }
        }
    
    @staticmethod
    def execute(code: str, language: str = 'python') -> str:
        """Vérifie la syntaxe."""
        if language == 'python':
            import ast
            try:
                ast.parse(code)
                return "✅ Python syntax is valid"
            except SyntaxError as e:
                return f"❌ Syntax error: {e}"
        
        elif language in ['javascript', 'typescript']:
            # Utiliser Node.js --check
            try:
                ext = '.js' if language == 'javascript' else '.ts'
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix=ext,
                    delete=False
                ) as f:
                    f.write(code)
                    temp_path = f.name
                
                result = subprocess.run(
                    ['node', '--check', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                Path(temp_path).unlink(missing_ok=True)
                
                if result.returncode == 0:
                    return f"✅ {language} syntax is valid"
                else:
                    return f"❌ Syntax error:\n{result.stderr}"
            except:
                return "⚠️ Node.js not available for syntax check"
        
        return f"⚠️ Syntax check not available for {language}"