"""
Système de cache pour éviter les requêtes répétées à Ollama.
"""
import hashlib
import json
from functools import wraps
from typing import Any, Callable
from diskcache import Cache

from .config import Config
from .logger import setup_logger

logger = setup_logger(__name__)

# Initialiser le cache disque
cache = Cache(str(Config.CACHE_DIR / 'ollama_cache'))

def cache_result(ttl: int = None) -> Callable:
    """
    Décorateur pour mettre en cache les résultats de fonction.
    
    Args:
        ttl: Durée de vie du cache en secondes (None = utiliser Config.CACHE_TTL)
    
    Usage:
        @cache_result(ttl=3600)
        def ask_ollama(prompt: str) -> str:
            ...
    """
    if ttl is None:
        ttl = Config.CACHE_TTL
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not Config.CACHE_ENABLED:
                return func(*args, **kwargs)
            
            # Créer une clé de cache basée sur les arguments
            cache_key = _create_cache_key(func.__name__, args, kwargs)
            
            # Vérifier le cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Exécuter la fonction
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            
            # Mettre en cache
            cache.set(cache_key, result, expire=ttl)
            
            return result
        
        return wrapper
    return decorator

def _create_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Crée une clé de cache unique."""
    # Combiner le nom de fonction et les arguments
    key_data = {
        'function': func_name,
        'args': args,
        'kwargs': kwargs
    }
    
    # Sérialiser et hasher
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"{func_name}:{key_hash}"

def get_cache_stats() -> dict:
    """Récupère les statistiques du cache."""
    try:
        stats = {
            'size': len(cache),
            'volume': cache.volume(),
            'enabled': Config.CACHE_ENABLED,
            'ttl': Config.CACHE_TTL,
        }
        
        # Calculer le hit rate (approximatif)
        # Note: diskcache ne track pas directement les hits/misses
        # On peut ajouter un compteur custom si nécessaire
        
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {}

def clear_cache() -> bool:
    """Vide le cache."""
    try:
        cache.clear()
        logger.info("Cache cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return False

def cache_invalidate(pattern: str = None):
    """
    Invalide les entrées du cache.
    
    Args:
        pattern: Pattern pour filtrer les clés (None = tout vider)
    """
    try:
        if pattern is None:
            clear_cache()
        else:
            # Filtrer et supprimer
            keys_to_delete = [k for k in cache.iterkeys() if pattern in k]
            for key in keys_to_delete:
                cache.delete(key)
            logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching '{pattern}'")
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")