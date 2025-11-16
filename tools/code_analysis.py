"""
Outils d'analyse statique de code.
Utilise AST, radon, vulture, bandit pour analyse approfondie.
"""
import ast
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from radon.complexity import cc_visit
from radon.metrics import mi_visit

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CodeAnalysisTool:
    """Analyse statique approfondie."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "analyze_code_quality",
            "description": "Perform deep static analysis: complexity, maintainability, security issues, dead code, type errors. Much more thorough than simple linting!",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to analyze"
                    },
                    "check_security": {
                        "type": "boolean",
                        "description": "Run security analysis with Bandit",
                        "default": True
                    }
                },
                "required": ["code"]
            }
        }
    
    @staticmethod
    def execute(code: str, check_security: bool = True) -> str:
        """Analyse complète du code."""
        results = []
        
        # 1. Analyse AST
        ast_result = CodeAnalysisTool._analyze_ast(code)
        if ast_result:
            results.append(f"🔍 AST Analysis:\n{ast_result}")
        
        # 2. Complexité cyclomatique
        complexity = CodeAnalysisTool._analyze_complexity(code)
        if complexity:
            results.append(f"📊 Complexity:\n{complexity}")
        
        # 3. Maintenabilité
        maintainability = CodeAnalysisTool._analyze_maintainability(code)
        if maintainability:
            results.append(f"🔧 Maintainability:\n{maintainability}")
        
        # 4. Sécurité
        if check_security:
            security = CodeAnalysisTool._analyze_security(code)
            if security:
                results.append(f"🔒 Security:\n{security}")
        
        # 5. Code mort
        dead_code = CodeAnalysisTool._find_dead_code(code)
        if dead_code:
            results.append(f"💀 Dead Code:\n{dead_code}")
        
        return "\n\n".join(results) if results else "✅ No issues found"
    
    @staticmethod
    def _analyze_ast(code: str) -> str:
        """Analyse l'AST pour trouver des patterns problématiques."""
        try:
            tree = ast.parse(code)
            issues = []
            
            for node in ast.walk(tree):
                # Détection de variables globales
                if isinstance(node, ast.Global):
                    issues.append(f"⚠️ Global variable usage: {', '.join(node.names)}")
                
                # Détection d'imports wildcard
                if isinstance(node, ast.ImportFrom):
                    if any(alias.name == '*' for alias in node.names):
                        issues.append(f"⚠️ Wildcard import from {node.module}")
                
                # Détection de nested functions trop profondes
                if isinstance(node, ast.FunctionDef):
                    depth = CodeAnalysisTool._get_nesting_depth(node)
                    if depth > 3:
                        issues.append(f"⚠️ Deep nesting in function '{node.name}': {depth} levels")
            
            return "\n".join(issues) if issues else None
            
        except SyntaxError:
            return "❌ Cannot parse code (syntax errors)"
        except Exception as e:
            logger.error(f"AST analysis error: {e}")
            return None
    
    @staticmethod
    def _get_nesting_depth(node: ast.AST, current_depth: int = 0) -> int:
        """Calcule la profondeur d'imbrication."""
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.If, ast.With)):
                child_depth = CodeAnalysisTool._get_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth
    
    @staticmethod
    def _analyze_complexity(code: str) -> str:
        """Analyse la complexité cyclomatique avec radon."""
        try:
            complexity_list = cc_visit(code)
            
            if not complexity_list:
                return None
            
            issues = []
            for item in complexity_list:
                if item.complexity > 10:
                    issues.append(f"❌ High complexity in '{item.name}': {item.complexity} (should be < 10)")
                elif item.complexity > 5:
                    issues.append(f"⚠️ Medium complexity in '{item.name}': {item.complexity}")
            
            return "\n".join(issues) if issues else "✅ All functions have good complexity"
            
        except Exception as e:
            logger.error(f"Complexity analysis error: {e}")
            return None
    
    @staticmethod
    def _analyze_maintainability(code: str) -> str:
        """Analyse l'index de maintenabilité."""
        try:
            mi_score = mi_visit(code, multi=True)
            
            if not mi_score:
                return None
            
            # Moyenne des scores
            avg_score = sum(mi_score) / len(mi_score)
            
            if avg_score < 10:
                return f"❌ Very low maintainability: {avg_score:.1f}/100"
            elif avg_score < 20:
                return f"⚠️ Low maintainability: {avg_score:.1f}/100"
            elif avg_score > 80:
                return f"✅ Excellent maintainability: {avg_score:.1f}/100"
            else:
                return f"✅ Good maintainability: {avg_score:.1f}/100"
                
        except Exception as e:
            logger.error(f"Maintainability analysis error: {e}")
            return None
    
    @staticmethod
    def _analyze_security(code: str) -> str:
        """Analyse de sécurité avec Bandit."""
        try:
            import tempfile
            from pathlib import Path
            
            # Créer fichier temporaire
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                temp_file = Path(f.name)
            
            try:
                # Exécuter Bandit
                result = subprocess.run(
                    ['bandit', '-f', 'txt', str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                output = result.stdout
                
                # Parser les résultats
                if 'No issues identified' in output:
                    return "✅ No security issues found"
                elif 'Issue:' in output:
                    # Extraire les lignes importantes
                    lines = [line for line in output.split('\n') if 'Issue:' in line or 'Severity:' in line]
                    return "\n".join(lines[:5])  # Top 5
                
                return None
                
            finally:
                temp_file.unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Security analysis error: {e}")
            return None
    
    @staticmethod
    def _find_dead_code(code: str) -> str:
        """Détecte le code mort avec vulture."""
        try:
            import tempfile
            from pathlib import Path
            
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
                    ['vulture', str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.stdout.strip():
                    lines = result.stdout.split('\n')[:5]  # Top 5
                    return "\n".join(lines)
                
                return None
                
            finally:
                temp_file.unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Dead code analysis error: {e}")
            return None


class LintingTool:
    """Linting rapide avec Ruff."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "lint_code",
            "description": "Fast linting with Ruff (replaces flake8, isort, etc). Finds style issues, imports problems, and common errors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to lint"
                    }
                },
                "required": ["code"]
            }
        }
    
    @staticmethod
    def execute(code: str) -> str:
        """Linting avec Ruff."""
        try:
            import tempfile
            from pathlib import Path
            
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
                    ['ruff', 'check', str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if not result.stdout.strip():
                    return "✅ No linting issues found"
                
                return f"Linting results:\n{result.stdout}"
                
            finally:
                temp_file.unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Linting error: {e}")
            return f"❌ Linting error: {str(e)}"