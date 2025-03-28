# Déploiement Continu (CD) pour l'Application Météo

Ce document explique le processus de déploiement continu (CD) mis en place pour l'application météo. Le CD permet de déployer automatiquement les nouvelles versions de l'application à chaque fusion (merge) dans la branche principale.

## Pipeline CI/CD

Notre pipeline CI/CD est configurée avec GitHub Actions et comprend trois étapes principales :

1. **Test (CI)** : Exécution des tests pour vérifier que le code fonctionne correctement.
2. **Build & Push (CI)** : Construction de l'image Docker et publication sur Docker Hub.
3. **Deploy (CD)** : Déploiement automatique de la nouvelle version sur l'environnement de production.

## Fichiers clés

- `.github/workflows/main.yml` : Configuration de la pipeline CI/CD avec GitHub Actions.
- `deploy.sh` : Script de déploiement utilisé pour déployer l'application sur le serveur.

## Comment fonctionne le déploiement continu

Le processus de déploiement continu se déclenche automatiquement après les étapes suivantes :

1. Un développeur crée une Pull Request (PR) vers la branche principale (main ou master).
2. Les tests automatiques sont exécutés pour vérifier la qualité du code.
3. Après revue et approbation, la PR est fusionnée dans la branche principale.
4. Le workflow CI/CD détecte le push sur la branche principale et exécute les étapes :
   - Exécution des tests
   - Construction et publication de l'image Docker
   - Déploiement automatique sur l'environnement de production

## Configuration requise

Pour que le déploiement continu fonctionne correctement, les secrets suivants doivent être configurés dans les paramètres du dépôt GitHub :

- `DOCKERHUB_USERNAME` : Nom d'utilisateur Docker Hub pour publier l'image.
- `DOCKERHUB_TOKEN` : Token d'accès Docker Hub.
- `OPENWEATHER_API_KEY` : Clé API OpenWeatherMap pour accéder aux données météo.

Pour un déploiement sur un serveur distant via SSH, ajoutez également :
- `SSH_PRIVATE_KEY` : Clé SSH privée pour l'accès au serveur.
- `SSH_USER` : Nom d'utilisateur SSH.
- `SSH_HOST` : Adresse du serveur hôte.

## Activer le déploiement réel

Le workflow actuel simule le déploiement pour des raisons de sécurité. Pour activer un déploiement réel sur un serveur :

1. Décommentez les sections relatives au déploiement SSH dans `.github/workflows/main.yml`.
2. Configurez les secrets nécessaires dans les paramètres du dépôt GitHub.
3. Assurez-vous que le serveur cible a Docker installé et les permissions nécessaires.

## Surveillance du déploiement

Après chaque déploiement, vous pouvez :

1. Consulter les journaux de déploiement dans l'onglet "Actions" de GitHub.
2. Vérifier que l'application fonctionne correctement en accédant à l'URL du serveur.
3. Examiner les logs de l'application sur le serveur pour détecter d'éventuels problèmes.

## Rollback en cas de problème

Si un déploiement cause des problèmes :

1. Vous pouvez revenir à la version précédente en modifiant le tag de l'image dans le script de déploiement.
2. Exécutez manuellement le script avec la version précédente : `./deploy.sh <version_précédente>`.
3. Alternativement, déclenchez un nouveau déploiement après avoir corrigé le problème dans le code source. 