"""
Prompts optimisés multi-langage pour l'agent Ollama.
"""

class PromptTemplates:
    """Templates de prompts pour différentes tâches et langages."""
    
    # ========================================================================
    # PROMPTS PAR LANGAGE
    # ========================================================================
    
    PYTHON_FIX_PROMPT = """You are a SENIOR Python developer doing CRITICAL code review.

⚠️ MANDATORY CHECKS:

1. ✓ Variables initialized BEFORE use
2. ✓ Division by zero checked (if len(x) > 0)
3. ✓ No list modification during iteration (use [:] or list comprehension)
4. ✓ Index within bounds
5. ✓ 'is None' not '== None'
6. ✓ Files closed with 'with' statement
7. ✓ 'if __name__ == "__main__"' for main()

Code to fix:
```python
{code}
```

Return ONLY corrected code, no explanations."""

    JAVASCRIPT_FIX_PROMPT = """You are a SENIOR JavaScript developer doing CRITICAL code review.

⚠️ MANDATORY CHECKS:

1. ✓ Use const/let, NEVER var
2. ✓ Check null/undefined with optional chaining (?.)
3. ✓ Async/await properly handled
4. ✓ No unhandled promise rejections
5. ✓ Variables declared before use
6. ✓ No accidental globals

Code to fix:
```javascript
{code}
```

Return ONLY corrected code, no explanations."""

    REACT_FIX_PROMPT = """You are a SENIOR React developer doing CRITICAL code review.

⚠️ MANDATORY CHECKS:

1. ✓ Rules of Hooks: No hooks in conditions/loops
2. ✓ NEVER mutate state directly (use setState)
3. ✓ All list items have unique 'key' prop
4. ✓ useEffect dependencies complete
5. ✓ Event listeners cleaned up (return cleanup function)
6. ✓ No infinite render loops

Code to fix:
```javascript
{code}
```

Return ONLY corrected code, no explanations."""

    # ========================================================================
    # PROMPT SYSTÈME POUR REACT
    # ========================================================================
    
    @staticmethod
    def get_language_prompt(language: str, code: str, task: str = "fix") -> str:
        """
        Retourne le prompt adapté au langage et à la tâche.
        
        Args:
            language: 'python', 'javascript', 'react', 'typescript', etc.
            code: Code à traiter
            task: 'fix', 'review', 'optimize', 'explain'
        """
        
        language_prompts = {
            'python': PromptTemplates.PYTHON_FIX_PROMPT,
            'javascript': PromptTemplates.JAVASCRIPT_FIX_PROMPT,
            'react': PromptTemplates.REACT_FIX_PROMPT,
            'typescript': PromptTemplates.JAVASCRIPT_FIX_PROMPT,
            'react-typescript': PromptTemplates.REACT_FIX_PROMPT,
        }
        
        # Récupérer le prompt de base
        base_prompt = language_prompts.get(
            language,
            f"""You are a SENIOR {language} developer.
Fix ALL bugs in this code following best practices.

Code to fix:
```{language}
{{code}}
```

Return ONLY corrected code, no explanations."""
        )
        
        # Adapter selon la tâche
        if task == "review":
            instruction = "Perform expert code review. List issues with severity."
        elif task == "optimize":
            instruction = "Optimize for performance and readability."
        elif task == "explain":
            instruction = "Explain what this code does step-by-step."
        else:  # fix
            instruction = base_prompt.split('\n')[0]
        
        return base_prompt.format(code=code) if '{code}' in base_prompt else base_prompt + f"\n\n{code}"
    
    # ========================================================================
    # PROMPT POUR ANALYSE DE PROJET
    # ========================================================================
    
    PROJECT_ANALYSIS_PROMPT = """Analyze this project structure and provide insights:

Project has {file_count} files
Languages: {languages}
Main directories: {directories}

Files sample:
{files_sample}

Provide a concise analysis (3-4 sentences):
- Project type (web app, API, CLI, library, etc.)
- Architecture pattern (if identifiable)
- Main technologies
- Potential improvements

Keep it brief and actionable."""