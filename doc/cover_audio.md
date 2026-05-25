# Cover Audio

Génération d'une cover 1920×1080 à partir d'une image source et intégration dans les métadonnées d'un fichier audio.

**Entrée :** image source (JPG, PNG, WEBP) + fichier audio (MP3, FLAC)  
**Sortie :** fichier audio avec la cover embeddée dans ses métadonnées

---

## Pipeline de traitement

```
Image source
      │
      ▼
[1] Fond flouté
      │  Redimensionne et recadre l'image pour couvrir 1920×1080
      │  Applique un flou gaussien (radius 30)
      ▼
[2] Composition de l'avant-plan
      │  Redimensionne l'image originale pour tenir dans facteur_hauteur × 1080
      │  La place à marge_gauche × 1920 depuis la gauche, centrée verticalement
      ▼
[3] Encodage JPEG
      │  Convertit en RGB si nécessaire
      │  Encode en JPEG qualité 95
      ▼
[4] Embedding dans l'audio
      │  MP3 : balise ID3 APIC (type 3 = cover front), remplace toute cover existante
      │  FLAC : Picture type 3, remplace toute cover existante
      ▼
Fichier audio mis à jour
```

---

## Modules

### `cover_manager.py` — Logique pure

Deux fonctions principales, indépendantes de Pillow et mutagen via des Protocols :

**`generer_cover(image, composeur, largeur, hauteur) → image_composee`**  
Orchestre les étapes 1 et 2. Appelle `composeur.couvrir_et_flouter` puis `composeur.placer_avant_plan`.

**`appliquer_cover(chemin_audio, image, composeur, ecriveur, largeur, hauteur)`**  
Appelle `generer_cover`, encode en JPEG via `composeur.vers_bytes_jpeg`, puis délègue l'écriture à `ecriveur.embedder_cover`.

**Protocols :**

| Protocol | Méthodes |
|---|---|
| `ComposeurImage` | `couvrir_et_flouter(image, largeur, hauteur)`, `placer_avant_plan(fond, image_originale)`, `vers_bytes_jpeg(image) → bytes` |
| `EcriveurMetadonnees` | `embedder_cover(chemin_audio, donnees_jpeg)` |

---

### `adaptateurs/composeur_pillow.py` — Implémentation image

**Paramètres (configurables par l'UI) :**

| Paramètre | Défaut | Plage UI | Effet |
|---|---|---|---|
| `facteur_hauteur` | 0.6 | 30%–100% | Hauteur max de l'avant-plan relative à la cover |
| `marge_gauche` | 0.0625 | 0%–30% | Décalage horizontal de l'avant-plan depuis la gauche (= 1/16 de la largeur, valeur CoverMagick) |

**`couvrir_et_flouter` :**
- `ImageOps.fit` — recadre et redimensionne l'image pour couvrir exactement les dimensions cibles (pas de bandes noires)
- `GaussianBlur(radius=6)` — sigma=6, équivalent du `-blur 30x6` d'ImageMagick (Pillow nomme ce paramètre `radius` mais c'est le sigma)
- `Image.blend(fond_noir, flou, alpha=0.5)` — mélange à 50% sur un canvas noir, ce qui assombrit le fond et réduit la saturation visuelle (même effet que `-compose Blend -define compose:args=50` d'ImageMagick)

**`placer_avant_plan` :**
- Calcule le ratio pour que l'avant-plan tienne dans `facteur_hauteur × hauteur` tout en respectant les proportions
- `Image.LANCZOS` pour le redimensionnement (qualité maximale)
- Centrage vertical : `y = (hauteur_fond - hauteur_avant_plan) // 2`

**`vers_bytes_jpeg` :**
- Conversion RGB forcée (gère les images PNG avec canal alpha)
- Qualité 95

---

### `adaptateurs/ecriveur_mutagen.py` — Embedding métadonnées

Dispatche selon l'extension du fichier audio :

**MP3** (`mutagen.id3`) :
- Charge les tags ID3 existants, ou crée un header vide si absent (`ID3NoHeaderError`)
- Supprime toutes les balises `APIC` existantes (`delall`)
- Ajoute `APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover")`

**FLAC** (`mutagen.flac`) :
- `clear_pictures()` puis `add_picture(Picture(type=3, mime="image/jpeg"))`

---

## Paramètres par défaut

| Constante | Valeur | Lieu |
|---|---|---|
| `LARGEUR_COVER_DEFAUT` | 1920 | `cover_manager.py` |
| `HAUTEUR_COVER_DEFAUT` | 1080 | `cover_manager.py` |
| `FACTEUR_HAUTEUR_DEFAUT` | 0.6 | `composeur_pillow.py` |
| `MARGE_GAUCHE_DEFAUT` | 0.0625 | `composeur_pillow.py` |

---

## Tests

| Fichier | Ce qui est testé |
|---|---|
| `tests/cover/test_cover_manager.py` | Orchestration (dimensions, composition, embedding) via `ComposeurFactice` et `EcriveurFactice` |

`ComposeurPillow` et `EcriveurMutagen` ne sont pas testés unitairement — ils dépendent de vrais fichiers image et audio.

### Conventions

Mêmes conventions que `doc/formattage_kara.md` : `test_lorsque_<condition>_alors_<résultat>`, Given/When/Then.

---

## Maintenance de la documentation

Toute modification du pipeline (nouveau format audio, nouveau paramètre de composition) doit être reflétée dans ce fichier avant de considérer la tâche terminée. Voir `standard.md` § Documentation.