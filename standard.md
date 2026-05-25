# Standards de développement

## Nommage

- Les noms de variables, fonctions et méthodes doivent être **explicites** : le nom doit exprimer clairement le rôle ou le contenu (`chemin_destination`, `contenu_japonais`, `_on_telecharger_texte`).
- Éviter les abréviations et les noms génériques (`data`, `tmp`, `val`, `res`).

## Commentaires

- Les commentaires sont à éviter : si un commentaire est nécessaire pour comprendre le code, c'est que le nommage n'est pas assez explicite.
- Préférer extraire une fonction bien nommée plutôt qu'expliquer ce qu'elle fait avec un commentaire.
- Exception tolérée : une contrainte non évidente, un contournement de bug externe, ou un comportement surprenant qui ne peut pas s'exprimer par le nommage seul. Dans ce cas, le commenter précédé de `@devnote`.

## Tests

### Nommage des tests

Les noms de tests suivent le format :

```
test_lorsque_<condition>_alors_<résultat_attendu>
```

Exemples :
- `test_lorsque_texte_japonais_alors_encodage_utf8_preserve`
- `test_lorsque_fichier_existant_alors_contenu_remplace`
- `test_lorsque_contenu_vide_alors_fichier_cree_vide`

### Docstring des tests

Chaque test porte une docstring qui suit la même convention `lorsque / alors` que son nom :

```python
def test_lorsque_xxx_alors_yyy():
    """Lorsque <condition>, alors <résultat attendu>."""
```

Exemples :
- `"""Lorsque le texte est vide, alors une chaîne vide est retournée."""`
- `"""Lorsque du texte japonais est exporté, alors l'encodage UTF-8 est préservé."""`

### Structure des tests

Chaque test est structuré en trois blocs commentés :

```python
def test_lorsque_xxx_alors_yyy():
    """Lorsque <condition>, alors <résultat attendu>."""
    # Given
    ...
    # When
    ...
    # Then
    assert ...
```

### TDD

Le développement suit le cycle **Red → Green → Refactor** :

1. **Red** — écrire un test qui échoue avant d'écrire le code de production.
2. **Green** — écrire le minimum de code pour faire passer le test.
3. **Refactor** — améliorer le code sans changer son comportement (les tests doivent toujours passer).

Toute nouvelle fonctionnalité ou correction de bug commence par un test.

## Documentation

Toute nouvelle fonctionnalité doit être reflétée dans les fichiers de documentation concernés avant de considérer la tâche terminée :

- **`AGENTS.md`** — si l'architecture, les contraintes non-évidentes ou le workflow changent.
- **`doc/formattage_kara.md`** — si le pipeline de romanisation ou ses modules évoluent.
