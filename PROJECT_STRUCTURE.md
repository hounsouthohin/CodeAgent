# Structure du Projet Recommandée

```
CodeAgent/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── server.py                 # Point d'entrée principal
│
├── tools/                    # Outils disponibles pour Ollama
│   ├── __init__.py
│   ├── code_execution.py    # Exécution et test de code
│   ├── code_analysis.py     # Analyse statique (AST, linting)
│   ├── documentation.py     # Recherche docs, StackOverflow
│   ├── web_search.py        # Recherche web avancée
│   ├── git_operations.py    # Opérations Git
│   └── performance.py       # Profiling et optimisation
│
├── agents/                   # Logique des agents
│   ├── __init__.py
│   ├── ollama_agent.py      # Agent Ollama avec ReAct
│   ├── prompts.py           # Prompts système optimisés
│   └── tool_executor.py     # Exécuteur d'outils
│
├── mcp_tools/               # Outils exposés via MCP
│   ├── __init__.py
│   ├── analyze_fix.py       # analyze_and_fix
│   ├── review.py            # expert_review
│   ├── test_gen.py          # generate_tests
│   └── explain.py           # quick_explain
│
└── utils/                   # Utilitaires
    ├── __init__.py
    ├── config.py            # Configuration centralisée
    ├── logger.py            # Logging structuré
    └── cache.py             # Cache pour réponses
```

## 🎯 Librairies Recommandées

### Analyse de Code (Gratuites & Puissantes)
- **ast** (built-in) - Analyse syntaxique avancée
- **astroid** - AST amélioré, utilisé par pylint
- **radon** - Complexité cyclomatique, maintenabilité
- **vulture** - Détecte le code mort
- **bandit** - Analyse de sécurité
- **pyflakes** - Détection d'erreurs rapide
- **mypy** - Type checking statique

### Exécution Sécurisée
- **RestrictedPython** - Exécution sandboxée
- **subprocess** (built-in) - Avec timeout et isolation
- **pytest** - Framework de test complet

### Recherche & Documentation
- **duckduckgo-search** - API gratuite sans limite
- **beautifulsoup4** - Parsing HTML
- **requests-cache** - Cache HTTP intelligent
- **whoosh** - Recherche full-text locale

### Performance & Profiling
- **py-spy** - Profiler sans overhead
- **memory-profiler** - Analyse mémoire
- **line-profiler** - Profiling ligne par ligne

### IA & Prompting
- **langchain** - Framework pour agents (optionnel)
- **guidance** - Structured prompting pour LLMs
- **instructor** - Validation de sorties LLM

### Git & Versioning
- **GitPython** - Opérations Git avancées
- **pygit2** - Binding libgit2 (plus rapide)

### Cache & Performance
- **diskcache** - Cache persistant sur disque
- **cachetools** - Cache en mémoire avec TTL