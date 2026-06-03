# KaraTool
Un petit outil pour aider à la création de karaokés japonais : téléchargement audio depuis YouTube et romanisation du texte japonais avec export `.ass` pour Aegisub.

## Télécharger l'application

Les exécutables Windows sont disponibles dans l'onglet [Releases](../../releases) du dépôt. Télécharger le fichier `KaraTool_vX.Y.Z.exe` et le lancer directement, sans installation.

## Développement

### Prérequis

```
pip install -r requirements.txt
```

### Lancer l'application

```
python src/main.py
```

### Tests et lint

```
python -m pytest tests/ -q
ruff check .
ruff format --check .
```

Les hooks pre-commit exécutent automatiquement le lint et les tests avant chaque commit :

```
pre-commit install
```

## Générer l'exécutable

### En local (Docker)

Nécessite Docker. Génère `dist/KaraTool_vX.Y.Z.exe` :

```
docker compose up
```

### Via GitHub Actions

Pousser un tag `vX.Y.Z` pour déclencher le build et la publication automatique d'une release :

```
git tag v1.0.0
git push origin v1.0.0
```
