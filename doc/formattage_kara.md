# Formattage Kara

Conversion d'un texte japonais (hiragana, katakana, kanji) en romaji formaté pour le karaoké.

**Entrée :** texte japonais brut  
**Sortie :** romaji nettoyé, prêt à être utilisé comme texte de karaoké

---

## Pipeline de traitement

```
Texte japonais
      │
      ▼
[1] Détection des emprunts katakana
      │  Sépare les mots d'origine étrangère des mots japonais adaptés
      ▼
[2] Protection du texte latin existant
      │  Remplace temporairement les séquences latines par des marqueurs __L0__, __L1__…
      ▼
[3] Romanisation (cutlet)
      │  Convertit hiragana / katakana / kanji → romaji
      ▼
[4] Restauration du texte latin
      │  Réinjecte le texte original en MAJUSCULES
      ▼
[5] Correction des particules
      │  Corrige la particule へ romanisée "e" → "he"
      ▼
[6] Post-traitement
      │  Rattache les n isolés au mot précédent et suivant
      │  Remplace les ra onomatopéiques par la
      │  Extrait les parenthèses sur de nouvelles lignes
      │  Supprime la ponctuation (sauf apostrophes)
      ▼
Romaji formaté
```

---

## Modules

### `romaniseur.py` — Orchestrateur principal

Point d'entrée : `romaniser_texte(texte_japonais: str) → str`

Traite le texte ligne par ligne en appelant les autres modules dans l'ordre du pipeline.

---

### `detecteur_emprunts.py` — Détection des emprunts

Point d'entrée : `remplacer_emprunts_katakana(texte: str) → str`

Pour chaque séquence katakana détectée, compare deux romanisations :

- **forme phonétique** — romanisation japonaise standard
- **forme étrangère** — romanisation avec règles d'emprunt

Deux règles de décision, appliquées dans l'ordre :

| Règle | Condition | Résultat |
|-------|-----------|----------|
| Pas d'équivalent étranger | Les deux formes sont identiques | Conservé en katakana |
| Translittération directe | `len(phonétique) / len(étrangère) ≥ 0.7` | Remplacé par la forme étrangère en MAJUSCULES |
| Abréviation japonaise | Ratio < 0.7 | Conservé en katakana |

**Exemples :**

| Katakana | Phonétique | Étrangère | Ratio | Résultat |
|----------|-----------|-----------|-------|----------|
| サッカー | sakkaa (6) | soccer (6) | 1.0 | `SOCCER` |
| テレビ | terebi (6) | television (10) | 0.6 | `テレビ` (conservé) |
| カラオケ | karaoke | karaoke | — (identiques) | `カラオケ` (conservé) |

Le seuil est configurable via `_SEUIL_RATIO_LONGUEUR = 0.7`.

---

### `post_traitement.py` — Nettoyage final

Point d'entrée : `post_traiter(texte: str) → str`

Quatre transformations successives :

1. **Rattachement des n isolés** — un `n` seul entre deux mots est fusionné sans espace (`omoeta n da` → `omoetanda`)
2. **Correction ra → la** — les `ra` isolés ou en séquences pures sont remplacés par `la` pour refléter la prononciation chantée ; les `ra` dans de vrais mots (`sakura`, `naraba`) et les majuscules (`RARARA`) ne sont pas touchés
3. **Extraction des parenthèses** — le contenu entre `()` ou `（）` est déplacé sur une nouvelle ligne
4. **Suppression de la ponctuation** — tout sauf les caractères de mot, les espaces, les apostrophes et les sauts de ligne

**Sous-fonctions de `_corriger_ra_en_la` :**

| Fonction | Forme ciblée | Exemple | Résultat |
|----------|-------------|---------|----------|
| `_remplacer_ra_repetes_en_la` | Mot composé uniquement de `ra` répétés | `rarara` | `lalala` |
| `_remplacer_ra_isole_en_la` | `ra` seul entre espaces | `ra` | `la` |
| `_corriger_ra_titre_en_la` | `Ra` titre (artefact cutlet après ponctuation) | `Ra`, `Rara` | `la`, `lala` |
| `_fusionner_la_adjacents` | Groupes `la` séparés par espace seul (artefact cutlet sur longues séquences) | `lalala lala` | `lalalalala` |

Les `ra` dans de vrais mots (`sakura`, `naraba`) et en majuscules (`RARARA`) ne sont pas touchés.

**Exemple :**
```
"toki、ga（ii no ni）tomareba!"
→ "toki ga\nii no ni\ntomareba"
```

---

## Exemple complet

```
Entrée : "サッカーとテレビを見る（ii ne）"

[1] Emprunts : "SOCCERとテレビを見る（ii ne）"
[2] Protection latin : "SOCCERとテレビを見る（__L0__）"  ← "ii ne" protégé
[3] Romanisation : "SOCCER to terebi wo miru （__L0__）"
[4] Restauration : "SOCCER to terebi wo miru （II NE）"
[5] Particules : (aucune particule へ ici)
[6] Post-traitement :
    → parenthèses extraites : "SOCCER to terebi wo miru\nII NE"
    → ponctuation supprimée : "SOCCER to terebi wo miru\nII NE"

Sortie :
SOCCER to terebi wo miru
II NE
```

---

## Tests

| Fichier | Ce qui est testé |
|---------|-----------------|
| `tests/formattage_kara/test_romaniseur.py` | Romanisation hiragana, kanji, katakana ; préservation du latin ; particules ; multi-lignes |
| `tests/formattage_kara/test_detecteur_emprunts.py` | Translittération directe, abréviations, formes identiques, texte sans katakana |
| `tests/formattage_kara/test_post_traitement.py` | Suppression de ponctuation, apostrophes, parenthèses ASCII et japonaises, rattachement des n isolés, correction ra → la |

Les tests sont lancés automatiquement avant chaque commit via le hook `pre-commit`.

### Conventions

**Nommage des fonctions** — pattern `test_lorsque_<condition>_alors_<comportement_attendu>` :

```python
def test_lorsque_katakana_translitteration_directe_alors_mot_etranger_retourne():
```

**Docstring** — suit la même convention que le nom de la fonction (`Lorsque … alors …`), affichée par pytest en mode verbeux (`-v`) :

```python
def test_lorsque_katakana_translitteration_directe_alors_mot_etranger_retourne():
    """Lorsque le katakana est une translittération directe (ratio ≥ 0.7), alors le mot étranger est retourné."""
```

**Structure** — pattern Given / When / Then :

```python
def test_lorsque_hiragana_saisi_alors_romaji_retourne():
    """Lorsque du texte en hiragana est saisi, alors le romaji correspondant est retourné."""
    # Given
    texte = "ようこそ"
    # When
    resultat = romaniser_texte(texte)
    # Then
    assert resultat == "you koso"
```

---

## Dépendances

| Bibliothèque | Rôle |
|---|---|
| `cutlet` | Romanisation japonaise (Hepburn) |
| `fugashi[unidic-lite]` | Analyseur morphologique utilisé par cutlet |
