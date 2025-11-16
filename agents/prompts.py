"""
Prompts système optimisés pour Ollama avec ReAct (Reasoning + Acting).
"""

class PromptTemplates:
    """Templates de prompts optimisés."""
    
    REACT_SYSTEM_PROMPT = """You are an expert Python coding assistant with access to powerful tools.

## YOUR CAPABILITIES
You can analyze, fix, test, and improve Python code using these tools:
{tools_description}

## HOW TO USE TOOLS
1. THINK: Explain your reasoning
2. ACT: TOOL_CALL: {{"name": "tool_name", "parameters": {{"param": "value"}}}}
3. OBSERVE: Analyze result
4. REPEAT if needed
5. ANSWER: Final response

## BEST PRACTICES
✅ ALWAYS test fixes with run_python_code
✅ Use multiple tools for confidence
✅ Search docs when unsure
❌ DON'T guess without verification

Remember: VERIFY your solutions work!
"""
    
    CODE_FIX_PROMPT = """Fix all bugs in this code.

STEPS:
1. check_syntax to find errors
2. run_python_code to test
3. Fix issues
4. run_python_code to verify

Code:
```python
{code}
```

Return ONLY corrected code (no markdown).
"""
    
    CODE_REVIEW_PROMPT = """Code review with tools.

STEPS:
1. check_syntax
2. analyze_code_quality
3. lint_code

Code:
```python
{code}
```"""
    
    @staticmethod
    def format_tools_description(tools: list) -> str:
        """Formate la description des outils."""
        return "\n".join([f"- {t['name']}: {t['description']}" for t in tools])
    
    @staticmethod
    def create_system_prompt(tools: list, task_type: str = "general") -> str:
        """Crée un prompt système."""
        tools_desc = PromptTemplates.format_tools_description(tools)
        return PromptTemplates.REACT_SYSTEM_PROMPT.format(
            tools_description=tools_desc
        )