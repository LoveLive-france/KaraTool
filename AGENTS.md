# KaraTool — Contexte pour agents IA

Outil de bureau Python (CustomTkinter) pour la création de karaokés japonais.  
Distribué sous forme d'un `.exe` Windows compilé avec PyInstaller, publié via GitHub Releases.  
Nom affiché dans l'UI : **LLFR Tools** (Love Live France).

## Stack

| Rôle | Outil |
|---|---|
| UI | CustomTkinter 5 |
| Romanisation | cutlet + fugashi + unidic-lite (MeCab) |
| Téléchargement | yt-dlp |
| Image | Pillow |
| Métadonnées audio | mutagen |
| Compilation | PyInstaller 6 |
| Tests | pytest 9 |
| Linting | ruff + pre-commit |

## Architecture

```
src/
├── main.py                              Point d'entrée → App().mainloop()
├── styles_disponibles.json              Styles ASS bundlés dans l'exe
├── ui/
│   ├── app.py                           Fenêtre principale (4 onglets)
│   ├── dialog_mise_a_jour.py            Dialog d'auto-update
│   └── tabs/
│       ├── tab_telechargeur.py          Téléchargement YouTube (audio MP3 ou vidéo MP4)
│       ├── tab_texte_japonais.py        Romanisation + export .ass
│       ├── tab_encodage.py              Réencodage vidéo via ffmpeg
│       └── tab_cover_audio.py           Ajout de cover image à un fichier audio
└── core/
    ├── download_manager.py              Wrapper yt-dlp threadé
    ├── ass_exporter.py                  Génération de fichiers .ass pour Aegisub
    ├── text_exporter.py                 Export texte brut
    ├── encoding_manager.py              Réencodage vidéo
    ├── auto_updater.py                  Vérif GitHub Releases + remplacement de l'exe
    ├── cover_manager.py                 Logique cover (Protocols ComposeurImage / EcriveurMetadonnees)
    ├── adaptateurs/
    │   ├── composeur_pillow.py          Implémentation Pillow du composeur
    │   └── ecriveur_mutagen.py          Implémentation mutagen pour les métadonnées
    └── formattage_kara/
        ├── romaniseur.py                Pipeline principal — point d'entrée : romaniser_texte()
        ├── detecteur_emprunts.py        Résolution katakana → mot étranger
        ├── dictionnaire_katakana.py     Dictionnaire manuel d'exceptions katakana
        └── post_traitement.py           Corrections post-romaji
```

## Standards de développement

Lire `standard.md` avant de modifier du code ou des tests. Résumé :

- **Nommage** : explicite, sans abréviations, en français (`chemin_destination`, `contenu_japonais`).
- **Commentaires** : uniquement pour les contraintes non-évidentes, préfixés `@devnote`. Pas de commentaires explicatifs.
- **Tests** : format `test_lorsque_<condition>_alors_<résultat>`, structure Given/When/Then, TDD (Red→Green→Refactor).
- **Documentation** : toute nouvelle fonctionnalité doit mettre à jour `AGENTS.md` et/ou `doc/formattage_kara.md` avant d'être considérée terminée.

## Pipeline de romanisation

Documenté en détail dans `doc/formattage_kara.md`. Résumé :

```
texte japonais
  → protection segments latins existants (sentinelles \x01…\x01)
  → remplacement emprunts katakana (dictionnaire > heuristique ratio)
  → protection emprunts résolus (sentinelles \x02…\x02)
  → romanisation cutlet
  → restauration sentinelles (latin original → MAJUSCULES, emprunt → MAJUSCULES ou Title)
  → séparation emprunts/romaji adjacent (espaces insérés)
  → correction particule へ → "he"
  → post-traitement : ra→la, n isolé, parenthèses→nouvelle ligne, ponctuation supprimée
```

### Règles de casse du texte latin

| Segment | Résultat |
|---|---|
| Latin ordinaire (ex: `love`) | `LOVE` |
| Latin tout-caps (ex: `LOVE`) | `LOVE` |
| Nom propre Title Case (ex: `Nike`) | `Nike` (préservé) |
| Emprunt katakana résolu | `SOCCER` (majuscules) |

### Détecteur d'emprunts katakana

Trois règles dans l'ordre, pour chaque séquence katakana :

1. **Dictionnaire** (`dictionnaire_katakana.py`) — prioritaire, court-circuite le reste.
2. **Formes identiques** (`phonétique == étrangère`) → conservé en katakana (ex: `カラオケ`).
3. **Ratio** `len(phonétique) / len(étrangère) ≥ 0.7` → mot étranger (ex: `サッカー` → `soccer`).  
   Sinon → conservé en katakana (ex: `アニメ`).

**Point ouvert** : cutlet peut associer un katakana à la mauvaise langue étrangère (ex: `マイン` → `mein` allemand au lieu de `mine` anglais). Le dictionnaire couvre les cas connus.

## Contraintes non-évidentes

- **Auto-updater Windows-only** : `lancer_remplacement()` dans `auto_updater.py` lance un `.bat` via `cmd.exe` pour remplacer l'exe en cours d'exécution (verrouillé sous Windows par le kernel). `creationflags=DETACHED_PROCESS` est Windows-only. Pas de chemin d'exécution sur Linux/macOS — l'app est distribuée uniquement en `.exe`.
- **Styles ASS** : bundlés dans l'exe via `sys._MEIPASS`, copiés à `%APPDATA%/KaraTool/` au premier lancement. L'utilisateur peut importer des styles depuis un `.ass` existant ; ils sont fusionnés sans écraser les styles existants.
- **`cutlet` supprime les espaces** entre tokens japonais et non-japonais adjacents → `_separer_emprunts_du_romaji_adjacent()` les réinsère par regex.
- **Particule へ** : cutlet romanise en `"e"` (Hepburn standard), corrigé en `"he"` en post-traitement uniquement quand c'est un mot isolé (`\be\b`).

## Tests

```
tests/
├── test_text_export.py
├── test_ass_exporter.py
├── formattage_kara/
│   ├── test_romaniseur.py         (29 tests)
│   ├── test_post_traitement.py
│   └── test_detecteur_emprunts.py
└── cover/
    └── test_cover_manager.py
```

Lancer les tests : `python -m pytest tests/ -q`  
Les hooks pre-commit exécutent lint et tests automatiquement avant chaque commit.

## Build et release

- **Local** : `docker compose up` → `dist/KaraTool.exe`
- **CI** : pousser un tag `vX.Y.Z` déclenche GitHub Actions → release publiée automatiquement avec `KaraTool_vX.Y.Z.exe`