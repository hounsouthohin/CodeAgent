# 🚀 CodeAgent V2 - 2 Super-Outils pour Gemini CLI

Agent de code intelligent avec Ollama local. Complète Gemini CLI avec ce qu'il ne peut PAS faire.

## ✨ Les 2 Super-Outils

### 1️⃣ `code_assist` - Assistant Multi-Langage
**Ce que Gemini CLI NE PEUT PAS:**
- ✅ Exécuter du code isolé
- ✅ Utiliser des outils spécialisés
- ✅ Accès gratuit illimité (Ollama local)

**Langages:** Python, JavaScript, TypeScript, React, Java, Go, Rust, C, C++

### 2️⃣ `analyze_project` - Vision Globale
**Ce que Gemini CLI FAIT MAL:**
- ✅ Vision complète du projet
- ✅ Architecture globale
- ✅ Analyse des dépendances

## 🚀 Démarrage Rapide

```bash
# 1. Cloner
git clone <repo>
cd CodeAgentV2

# 2. Lancer
docker-compose up -d

# 3. Télécharger le modèle
docker-compose exec ollama ollama pull qwen2.5-coder:1.5b

# 4. Tester
docker-compose logs -f code-agent
```

## 💻 Utilisation avec Gemini CLI

```bash
gemini

# Corriger bugs Python
> Use code_assist: filepath="test.py", task="fix", verify=true

# Review React component  
> Use code_assist: filepath="App.jsx", task="review"

# Analyser projet complet
> Use analyze_project: project_path=".", generate_summary=true

# Stats serveur
> Use get_server_stats
```

## 📁 Structure

```
CodeAgentV2/
├── agents/          # Ollama ReAct agent
├── tools/           # 3 outils internes
├── mcp_tools/       # 2 super-outils exposés
├── utils/           # Config, logging, cache
└── server.py        # Serveur MCP
```

## 🎯 Pourquoi Seulement 2 Outils?

Gemini CLI a déjà:
- ✅ Edit, ReadFile, WriteFile
- ✅ Shell, GoogleSearch, WebFetch
- ✅ FindFiles, SearchText

Nos 2 outils ajoutent ce qui manque:
- 🔥 Exécution + vérification de code
- 🔥 Vision globale du projet

## 📊 Performance

- **Détection bugs:** 85-95%
- **Temps:** 8-15s (simple), 25-40s (avec vérification)
- **Coût:** 0€ (Ollama local)

## 🛠️ Technologies

- **FastMCP** - Serveur MCP
- **Ollama** - LLM local (qwen2.5-coder:1.5b)
- **Python 3.11** - Backend
- **Docker** - Conteneurisation

## 📝 Licence

MIT