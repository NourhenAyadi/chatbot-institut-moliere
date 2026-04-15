import os
import subprocess
import sys

def build():
    print("🚀 Début du build de l'exécutable...")
    
    # Définition des dossiers à inclure
    # Format: "chemin_source:chemin_destination" (sous Linux c'est :)
    # Pour Windows ce serait ;
    sep = ":" if os.name != "nt" else ";"
    
    add_data = [
        f"templates{sep}templates",
        f"static{sep}static",
        f"db{sep}db",
        f".env{sep}."
    ]
    
    data_args = []
    for d in add_data:
        data_args.extend(["--add-data", d])
        
    command = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--name", "AssistantMoliere",
    ] + data_args + ["main.py"]
    
    print(f"📦 Commande : {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
        print("\n✅ Build terminé avec succès !")
        print("📁 L'exécutable se trouve dans le dossier 'dist/'.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors du build : {e}")
    except FileNotFoundError:
        print("\n❌ Erreur : PyInstaller n'est pas installé. Lancez 'pip install pyinstaller'.")

if __name__ == "__main__":
    build()
