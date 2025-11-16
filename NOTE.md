1. VOUS tapez:
   > "Can you review test.py?"

2. GEMINI CLI analyse:
   - Comprend que vous voulez une code review
   - Cherche dans les outils disponibles
   - Trouve "expert_review" dans le MCP server
   - Décide d'utiliser cet outil

3. GEMINI CLI → MCP SERVER:
   POST http://localhost:8080/tools/expert_review
   Body: {"fichier": "test.py"}

4. MCP SERVER (server.py):
   def expert_review(fichier: str):
       # Lit le fichier test.py
       code = path.read_text()
       
       # Prépare un prompt pour Ollama
       prompt = "Code review - Be concise..."
       
       # Appelle Ollama ↓

5. MCP SERVER → OLLAMA:
   POST http://ollama:11434/api/generate
   Body: {
       "model": "qwen2.5-coder:1.5b",
       "prompt": "Review this code...",
       "stream": True
   }

6. OLLAMA:
   - Charge le modèle qwen2.5-coder:1.5b
   - Génère l'analyse du code
   - Renvoie la réponse en streaming

7. OLLAMA → MCP SERVER:
   Response: {
       "response": "1. Critical bugs? None\n2. Security..."
   }

8. MCP SERVER → GEMINI CLI:
   Response: {
       "analyse": "1. Critical bugs? None...",
       "status": "✅ Analyse terminée"
   }

9. GEMINI CLI → VOUS:
   Affiche l'analyse de manière formatée dans le terminal