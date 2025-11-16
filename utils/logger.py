"""
Système de logging structuré et coloré.
"""
import logging
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console
from .config import Config

console = Console()

def setup_logger(name: str) -> logging.Logger:
    """
    Configure un logger avec Rich pour un affichage coloré.
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Handler console avec Rich
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=True
    )
    console_handler.setFormatter(
        logging.Formatter("%(message)s", datefmt="[%X]")
    )
    logger.addHandler(console_handler)
    
    # Handler fichier
    file_handler = logging.FileHandler(
        Config.LOG_DIR / f"{name}.log"
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(file_handler)
    
    return logger