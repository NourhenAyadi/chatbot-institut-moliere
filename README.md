# Chatbot RAG - Institut Molière

Ce projet est le backend d'un chatbot basé sur le RAG (Retrieval-Augmented Generation) conçu pour gérer les communications de l'Institut Molière.
Il est développé avec **FastAPI**, **LangChain**, et peut utiliser soit le modèle ultra-rapide hébergé par **Groq** (Llama 3), soit un modèle local via **Ollama**.

## 🚀 Fonctionnalités
- RAG (Retrieval-Augmented Generation) basé sur les documents PDF dans le dossier `doc/`.
- Base de données vectorielle locale avec **ChromaDB**.
- API ultra-rapide propulsée par **FastAPI** (avec swagger interactif).
- Interface web intuitive desservie par Jinja2 et du HTML/CSS/JS "Vanilla" (`templates/index.html`).

## 🛠️ Prérequis
- [Python 3.10+](https://www.python.org/)
- (Optionnel) [Docker](https://www.docker.com/) pour le déploiement.

## ⚙️ Installation Rapide (Environnement Local)

1. **Cloner ou récupérer le dépôt :**
   ```bash
   git clone <URL_DU_DEPOT>
   cd chatbot_moliere
   ```

2. **Créer un environnement virtuel :**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement :**
   - Copiez le fichier `.env.example` en `.env` :
     ```bash
     cp .env.example .env
     ```
   - Éditez `.env` pour y ajouter votre `GROQ_API_KEY`. (Si la clé n'est pas fournie, le code essaiera d'utiliser un modèle Ollama local, ce qui sera beaucoup plus lent).

## 🏃‍♀️ Lancement

### Lancer l'application localement
```bash
uvicorn main:app --reload --port 8001
```

L'application sera accessible sur :
- Interface de chat : [http://localhost:8001/](http://localhost:8001/)
- Documentation Interactive (Swagger) : [http://localhost:8001/docs](http://localhost:8001/docs)

### Lancer via Docker
L'équipe d'infrastructure peut facilement déployer l'application grâce au Dockerfile inclus.

```bash
docker build -t chatbot-moliere .
docker run -d -p 8001:8001 --env-file .env chatbot-moliere
```

## 📚 Intégration pour la plateforme
Toute la logique de réponse de l'IA est accessible via l'API, ce qui est idéal pour intégrer le chatbot à une autre application front-end.
Consultez directement le swagger de l'API sur `http://localhost:8001/docs`. 

La route d'inférence principale est :
`POST /ask`
Body attendu :
```json
{
  "question": "Où est situé l'Institut ?"
}
```
Réponse :
```json
{
  "response": "L'Institut Molière est situé à Tunis...",
  "type": "RAG"
}
```

## 📁 Structure du Projet
- `main.py` : Logique de l'application FastAPI, le routeur et la chaîne RAG.
- `doc/` : Placez-y vos fichiers PDF contenant la connaissance pour l'Institut.
- `static/` : Fichiers statiques (images, css).
- `templates/` : Fichiers HTML.
- `db/` : Base de données Chroma (créée automatiquement au premier lancement, ignorée dans git).
