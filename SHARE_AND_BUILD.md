# Guide: Partager et Construire votre Chatbot

Ce guide contient les instructions pour envoyer votre chatbot au client (l'enseignant) pour test.

## 1. Partage Instantané (Recommandé)
Le moyen le plus simple permet à votre client d'accéder au chatbot via un lien web, sans rien installer de son côté.

### Option A : Ngrok (Standard)
1. Téléchargez Ngrok : [ngrok.com/download](https://ngrok.com/download)
2. Créez un compte gratuit et récupérez votre "AuthToken".
3. Dans votre terminal, lancez :
   ```bash
   ngrok config add-authtoken VOTRE_TOKEN
   ngrok http 8001
   ```
4. Envoyez le lien `https://...ngrok-free.app` à votre client.

### Option B : Localtunnel (Très simple)
Si vous avez Node.js installé :
```bash
npx localtunnel --port 8001
```

---

## 2. Création d'un Exécutable (.exe)
Si vous voulez envoyer un fichier autonome.

### Préparation
Installez PyInstaller dans votre environnement :
```bash
source venv/bin/activate
pip install pyinstaller
```

### Script de Build
J'ai créé un script `build_exe.py` pour automatiser cela. Lancez-le ainsi :
```bash
python3 build_exe.py
```
Le résultat sera dans le dossier `dist/`.

---

## ⚠️ Notes Importantes pour le Client
- **Base de données** : Le dossier `db/` est inclus dans le build.
- **LLM** : Si vous utilisez **Groq**, le client a juste besoin d'une connexion internet. Si vous utilisez **Ollama**, le client **doit installer Ollama** sur sa machine.
