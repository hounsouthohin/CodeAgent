# Code Assist MCP pour Gemini CLI

## Setup
1. Clone ce repo dans ton projet Git : `git clone <url> .`
2. Installe deps : `uv pip install -r requirements.txt`
3. Lance serveur : `uv run server.py` (ou `docker compose up`)
4. Configure Gemini : Copie settings.json
5. Dans Gemini CLI : `/mcp list` pour vérifier.

## Utilisation
- Outils : "Fais une code_review sur app.py"
- Slash : `/revue_code_complete app.py`
- Pour push : `/deploy_propre "Améliorations linting"`

## Extension
- Ajoute Ollama pour LLM : Dans server.py, intègre requests à http://ollama:11434 pour suggestions avancées.
- Sécurité : Jamais de push auto ; toujours générer commandes.

## Troubleshooting
- Erreur connexion : Vérifie port 8080 libre.
- Pas de Git : Init repo d'abord.