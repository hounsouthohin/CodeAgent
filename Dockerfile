FROM python:3.11-slim

WORKDIR /app

# Installer Node.js pour support JavaScript
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Créer les dossiers
RUN mkdir -p /tmp/mcp_cache /tmp/mcp_logs

# Port MCP
EXPOSE 8080

# Lancer le serveur
CMD ["python", "server.py"]