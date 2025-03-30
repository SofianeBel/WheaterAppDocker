# Utiliser l'image Python 3.10 comme base
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier uniquement le fichier des dépendances et installer les dépendances
# Cette séparation permet de mettre en cache les dépendances si elles ne changent pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source de l'application
# Cette étape sera exécutée uniquement si les fichiers application changent
COPY . .

# Exposer le port sur lequel l'application s'exécute
EXPOSE 5000

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Commande pour démarrer l'application en production
CMD ["python", "app.py"] 