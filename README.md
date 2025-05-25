# playlist-youtube-dowload

## Introduction

**YouTube Music Downloader** est un outil en Python permettant de télécharger des playlists depuis YouTube Music. Grâce à une interface graphique intuitive et à l'utilisation de `ytmusicapi` et de `yt-dlp`, ce script récupère les métadonnées des playlists et télécharge les pistes en simultané tout en offrant la possibilité de mettre en pause ou d'arrêter le processus en cours.

Ce projet est destiné aux utilisateurs souhaitant sauvegarder des playlists en local et aux développeurs désireux d'explorer ou d'améliorer le processus de téléchargement et de conversion audio.

---

## Installation et Configuration

### Prérequis

- **Python** : Version 3.x est nécessaire.
- **Bibliothèques Python** :  
  - `ytmusicapi`  
  - `ttkbootstrap`  
  - `tkinter` (généralement inclus avec Python)
  - Autres dépendances éventuelles (vous pouvez tous les lister dans un fichier `requirements.txt`)

### Installation

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/djvetbo/playlist-youtube-dowload.git
   cd playlist-youtube-dowload
   
2. **Installer les dépendances :**

    ```bash
    pip install -r requirements.txt

### Utilisation

    ```bash
    python playlist-youtube-dowload.py

### Fonctionnalités principales

Saisie des playlists : Collez ou saisissez les liens/IDs de playlists (un par ligne).
Sélection du dossier de destination : Choisissez l'emplacement de stockage à l'aide du bouton « Parcourir ».
Choix du format et du débit : Sélectionnez le format audio (ex. mp3, vorbis, flac, etc.) et le débit souhaité (ex. 320k, 192k).
Contrôle du téléchargement : Utilisez les boutons Télécharger, Pause, Reprendre et Stop pour gérer le processus. Le suivi du téléchargement est assuré par des barres de progression et une zone de log affichant l'état d'avancement.

### Architecture et Fonctionnement

Multithreading : Chaque piste de musique est téléchargée dans un thread séparé. Cela permet de maintenir une interface graphique réactive même lors de nombreux téléchargements simultanés. Des événements (stop_flag et pause_flag) permettent de mettre en pause ou d'interrompre le processus.
Téléchargement via yt-dlp : Pour chaque chanson, le script lance un sous-processus qui appelle yt-dlp avec les paramètres nécessaires pour télécharger, convertir l'audio, et intégrer les métadonnées ainsi que les miniatures.
Gestion intelligente des fichiers : Le script s'assure que le nom de chaque fichier est sécurisé pour le système d'exploitation et évite les duplications en vérifiant l'existence du fichier avant téléchargement.

### Contribution

Les contributions sont les bienvenues !
Pensez à respecter les conventions de codage et à documenter vos changements.


### FAQ et Dépannage

Problème d'authentification ? Assurez-vous que le fichier headers_auth.json est correctement configuré.
Erreur lors du téléchargement ? Vérifiez que yt-dlp est installé et que le fichier de cookies (ytmusic_cookies.txt) est valide.

### Remerciements
Merci aux auteurs des bibliothèques ytmusicapi et yt-dlp pour leur excellent travail, ainsi qu'à toutes les personnes contribuant à l'amélioration de ce projet.
