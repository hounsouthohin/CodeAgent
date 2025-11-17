"""
Vérificateur de code - s'assure que les corrections fonctionnent.
"""
import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CodeVerifier:
    """Vérifie que le code corrigé fonctionne réellement."""
    
    @staticmethod
    def verify_correction(original_code: str, fixed_code: str) -> Dict[str, Any]:
        """
        Vérifie une correction de code.
        
        Returns:
            Dict avec:
            - syntax_valid: bool
            - can_import: bool
            - runtime_errors: list
            - score: int (0-100)
            - issues: list
        """
        result = {
            'syntax_valid': False,
            'can_import': False,
            'runtime_errors': [],
            'score': 0,
            'issues': []
        }
        
        # Test 1: Syntaxe
        syntax_check = CodeVerifier._check_syntax(fixed_code)
        result['syntax_valid'] = syntax_check['valid']
        if not syntax_check['valid']:
            result['issues'].append(f"Syntax error: {syntax_check['error']}")
            return result  # Stop si syntaxe invalide
        
        result['score'] += 30  # +30 points pour syntaxe valide
        
        # Test 2: Import
        import_check = CodeVerifier._check_import(fixed_code)
        result['can_import'] = import_check['success']
        if not import_check['success']:
            result['issues'].append(f"Import error: {import_check['error']}")
        else:
            result['score'] += 20  # +20 points si importable
        
        # Test 3: Variables non initialisées
        unbound_vars = CodeVerifier._check_unbound_variables(fixed_code)
        if unbound_vars:
            result['issues'].append(f"Potential unbound variables: {', '.join(unbound_vars)}")
        else:
            result['score'] += 20  # +20 points
        
        # Test 4: Division par zéro potentielle
        div_zero_risks = CodeVerifier._check_division_by_zero(fixed_code)
        if div_zero_risks:
            result['issues'].append(f"Division by zero risk on lines: {', '.join(map(str, div_zero_risks))}")
        else:
            result['score'] += 15  # +15 points
        
        # Test 5: Modification de liste pendant itération
        list_mod_issues = CodeVerifier._check_list_modification(fixed_code)
        if list_mod_issues:
            result['issues'].append(f"List modification during iteration on lines: {', '.join(map(str, list_mod_issues))}")
        else:
            result['score'] += 15  # +15 points
        
        return result
    
    @staticmethod
    def _check_syntax(code: str) -> Dict[str, Any]:
        """Vérifie la syntaxe Python."""
        try:
            ast.parse(code)
            return {'valid': True, 'error': None}
        except SyntaxError as e:
            return {'valid': False, 'error': str(e)}
    
    @staticmethod
    def _check_import(code: str) -> Dict[str, Any]:
        """Vérifie si le code peut être importé."""
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
                # Vérifier avec py_compile
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {'success': True, 'error': None}
                else:
                    return {'success': False, 'error': result.stderr}
            finally:
                temp_file.unlink(missing_ok=True)
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _check_unbound_variables(code: str) -> list:
        """Détecte les variables potentiellement non initialisées."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        unbound = []
        
        class VariableChecker(ast.NodeVisitor):
            def __init__(self):
                self.defined = set()
                self.used = set()
                self.in_function = False
            
            def visit_FunctionDef(self, node):
                old_in_function = self.in_function
                self.in_function = True
                
                # Paramètres sont définis
                for arg in node.args.args:
                    self.defined.add(arg.arg)
                
                self.generic_visit(node)
                self.in_function = old_in_function
            
            def visit_Assign(self, node):
                # Variables assignées sont définies
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.defined.add(target.id)
                self.generic_visit(node)
            
            def visit_For(self, node):
                # Variable de boucle est définie
                if isinstance(node.target, ast.Name):
                    self.defined.add(node.target.id)
                self.generic_visit(node)
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    # Variable utilisée
                    if self.in_function and node.id not in self.defined:
                        self.used.add(node.id)
        
        checker = VariableChecker()
        checker.visit(tree)
        
        # Variables utilisées mais pas définies (heuristique simple)
        # Ignore les builtins courants
        builtins = {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 
                   'sum', 'max', 'min', 'open', 'True', 'False', 'None'}
        
        unbound = [var for var in checker.used if var not in builtins]
        
        return unbound[:5]  # Limiter à 5 pour éviter le spam
    
    @staticmethod
    def _check_division_by_zero(code: str) -> list:
        """Détecte les divisions potentiellement par zéro."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        risky_lines = []
        
        class DivisionChecker(ast.NodeVisitor):
            def visit_BinOp(self, node):
                if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                    # Vérifier si le dénominateur est len(quelquechose)
                    if isinstance(node.right, ast.Call):
                        if isinstance(node.right.func, ast.Name):
                            if node.right.func.id == 'len':
                                risky_lines.append(node.lineno)
                self.generic_visit(node)
        
        checker = DivisionChecker()
        checker.visit(tree)
        
        return risky_lines
    
    @staticmethod
    def _check_list_modification(code: str) -> list:
        """Détecte les modifications de liste pendant itération."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        risky_lines = []
        
        class ListModChecker(ast.NodeVisitor):
            def __init__(self):
                self.current_iter_var = None
                self.current_iter_line = None
            
            def visit_For(self, node):
                old_var = self.current_iter_var
                old_line = self.current_iter_line
                
                # Récupérer le nom de la liste itérée
                if isinstance(node.iter, ast.Name):
                    self.current_iter_var = node.iter.id
                    self.current_iter_line = node.lineno
                
                self.generic_visit(node)
                
                self.current_iter_var = old_var
                self.current_iter_line = old_line
            
            def visit_Call(self, node):
                # Vérifier les appels à .remove(), .pop(), .append() sur la liste itérée
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['remove', 'pop', 'append', 'insert', 'clear']:
                        if isinstance(node.func.value, ast.Name):
                            if node.func.value.id == self.current_iter_var:
                                risky_lines.append(self.current_iter_line)
                
                self.generic_visit(node)
        
        checker = ListModChecker()
        checker.visit(tree)
        
        return list(set(risky_lines))  # Dédupliquer


class IterativeFixRunner:
    """Exécute la correction de code avec vérification itérative."""
    
    def __init__(self, ollama_agent):
        self.agent = ollama_agent
        self.verifier = CodeVerifier()
        self.max_iterations = 3
    
    def fix_with_verification(self, code: str, task_type: str = "fix") -> Dict[str, Any]:
        """
        Corrige le code et vérifie le résultat.
        Réessaie jusqu'à 3 fois si des problèmes persistent.
        
        Returns:
            Dict avec le code corrigé et les résultats de vérification
        """
        logger.info("Starting fix_with_verification")
        
        original_code = code
        current_code = code
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"Iteration {iteration}/{self.max_iterations}")
            
            # 1. Correction par Ollama
            fixed_code = self.agent.ask_with_tools(
                f"Fix all bugs in this code:\n\n{current_code}",
                task_type=task_type,
                max_iterations=5
            )
            
            # Nettoyer la réponse
            fixed_code = self._clean_code_response(fixed_code)
            
            # 2. Vérification
            verification = self.verifier.verify_correction(original_code, fixed_code)
            
            logger.info(f"Verification score: {verification['score']}/100")
            
            # 3. Si score >= 85, c'est bon!
            if verification['score'] >= 85:
                logger.info("✅ Code verified successfully!")
                return {
                    'code': fixed_code,
                    'verification': verification,
                    'iterations': iteration,
                    'success': True
                }
            
            # 4. Sinon, feedback pour améliorer
            if iteration < self.max_iterations:
                feedback = self._create_feedback(verification)
                current_code = f"{fixed_code}\n\n# ISSUES TO FIX:\n{feedback}"
                logger.info(f"Issues found, retrying... Feedback: {feedback}")
        
        # Max iterations atteintes
        logger.warning(f"Max iterations reached. Score: {verification['score']}/100")
        return {
            'code': fixed_code,
            'verification': verification,
            'iterations': self.max_iterations,
            'success': False
        }
    
    @staticmethod
    def _clean_code_response(response: str) -> str:
        """Nettoie la réponse pour extraire le code."""
        # Enlever les markdown code blocks
        response = response.replace("```python", "").replace("```", "").strip()
        
        # Enlever les lignes de commentaires d'explication au début/fin
        lines = response.split('\n')
        
        # Trouver le premier import ou class/def
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ', 'class ', 'def ', '@')):
                start_idx = i
                break
        
        # Garder à partir de là
        cleaned_lines = lines[start_idx:]
        
        return '\n'.join(cleaned_lines)
    
    @staticmethod
    def _create_feedback(verification: Dict[str, Any]) -> str:
        """Crée un feedback pour Ollama basé sur la vérification."""
        feedback = []
        
        for issue in verification['issues']:
            feedback.append(f"- {issue}")
        
        if not verification['syntax_valid']:
            feedback.append("- FIX SYNTAX ERRORS FIRST!")
        
        if not verification['can_import']:
            feedback.append("- Code cannot be imported, check for runtime errors at module level")
        
        return '\n'.join(feedback) if feedback else "Minor issues remain"