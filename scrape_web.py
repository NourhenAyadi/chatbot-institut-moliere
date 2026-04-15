#!/usr/bin/env python3
"""
Script de collecte de données pédagogiques depuis le web.
Usage: python3 scrape_web.py

Le script télécharge le contenu de sites pédagogiques sélectionnés
et les sauvegarde sous forme de fichiers .txt dans le dossier doc/.
Ensuite, supprimez le dossier db/ et relancez le serveur pour re-indexer.
"""

import requests
from bs4 import BeautifulSoup
import os
import time

OUTPUT_DIR = "doc"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Délai entre les requêtes pour ne pas surcharger les serveurs
REQUEST_DELAY = 1

def fetch_page(url: str) -> str:
    """Télécharge et nettoie le texte d'une page web."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        # (connect_timeout, read_timeout) en secondes
        response = requests.get(url, headers=headers, timeout=(5, 10))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Supprimer les éléments inutiles (menus, pubs, scripts)
        for tag in soup(["script", "style", "nav", "header", "footer",
                         "aside", "form", "button", "iframe", "noscript"]):
            tag.decompose()

        # Extraire le texte propre
        text = soup.get_text(separator="\n")
        # Nettoyer les lignes vides multiples
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        print(f"    Erreur pour {url}: {e}")
        return ""


def save_doc(filename: str, content: str, source_url: str):
    """Sauvegarde le contenu dans un fichier .txt."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Source : {source_url}\n\n")
        f.write(content)
    print(f"   Sauvegardé : {filepath} ({len(content)} caractères)")




sources = [
    # Niveau CECRL — fiches officielles
    {
        "filename": "web_cecrl_niveaux_officiels.txt",
        "url": "https://www.bonjourdefrance.com/index/niveaux-cecrl.html",
        "description": "Niveaux CECRL officiels (A1 à C2) — bonjourdefrance.com",
    },
    # Conseils pour parents bilingues
    {
        "filename": "web_conseils_parents_bilingues.txt",
        "url": "https://www.grandir-bilingue.com/category/conseils-pratiques/",
        "description": "Conseils pratiques pour parents bilingues",
    },
    # Grammaire française niveau A1-A2
    {
        "filename": "web_grammaire_fle_a1_a2.txt",
        "url": "https://www.bonjourdefrance.com/exercices/t_grammaire.htm",
        "description": "Exercices de grammaire FLE A1-A2 — bonjourdefrance.com",
    },
    # Vocabulaire et thèmes
    {
        "filename": "web_vocabulaire_fle.txt",
        "url": "https://www.lepointdufle.net/vocabulaire.htm",
        "description": "Vocabulaire FLE par thème — lepointdufle.net",
    },
    # Activités pour apprendre
    {
        "filename": "web_activites_apprentissage.txt",
        "url": "https://www.lepointdufle.net/p/enfants.htm",
        "description": "Ressources FLE pour enfants — lepointdufle.net",
    },
    # Site officiel de l'Institut Molière
    {
        "filename": "web_institut_moliere_accueil.txt",
        "url": "https://institut-moliere.fr/",
        "description": "Page d'accueil officielle de l'Institut Molière (Infos administratives)",
    },
]


def main():
    print("=" * 60)
    print("   Collecte de Données Pédagogiques")
    print("=" * 60)
    print(f"  Dossier de sortie : {os.path.abspath(OUTPUT_DIR)}/\n")

    success_count = 0
    for source in sources:
        print(f" Téléchargement : {source['description']}")
        print(f"   URL : {source['url']}")
        content = fetch_page(source["url"])
        if content and len(content) > 200:
            save_doc(source["filename"], content, source["url"])
            success_count += 1
        else:
            print(f"   Contenu insuffisant ou inaccessible.")
        time.sleep(REQUEST_DELAY)

    print("\n" + "=" * 60)
    print(f"   {success_count}/{len(sources)} sources téléchargées avec succès.")
    print()
    print("    PROCHAINE ÉTAPE :")
    print("     1. Supprimez le dossier db/ :  rm -rf db/")
    print("     2. Relancez le serveur       :  uvicorn main:app --reload --port 8001")
    print("     Le chatbot utilisera maintenant les nouvelles données.")
    print("=" * 60)


if __name__ == "__main__":
    main()
