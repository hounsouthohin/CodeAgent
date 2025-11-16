"""
Configuration centralisée de l'application.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration globale."""
    

    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    OLLAMA_BASE_URL = OLLAMA_HOST  # ← Ajouter cette ligne
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
    
    # Timeouts
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "90"))
    TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "30"))
    
    # Limites
    MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "10000"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "3000"))
    MAX_TOOL_ITERATIONS = int(os.getenv("MAX_TOOL_ITERATIONS", "5"))
    
    # Chemins
    APP_PATH = Path("/app")
    CACHE_DIR = Path("/tmp/mcp_cache")
    LOG_DIR = Path("/tmp/mcp_logs")
    
    # Cache
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 heure
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Code Execution
    CODE_EXECUTION_ENABLED = os.getenv("CODE_EXECUTION_ENABLED", "true").lower() == "true"
    EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", "5"))
    
    # Web Search
    WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "true").lower() == "true"
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    
    # Security
    SANDBOX_ENABLED = os.getenv("SANDBOX_ENABLED", "true").lower() == "true"
    
    @classmethod
    def setup_directories(cls):
        """Créer les répertoires nécessaires."""
        cls.CACHE_DIR.mkdir(exist_ok=True, parents=True)
        cls.LOG_DIR.mkdir(exist_ok=True, parents=True)

# Initialiser les répertoires au démarrage
Config.setup_directories()