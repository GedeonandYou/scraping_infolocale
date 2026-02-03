# Guide Alembic - Migrations de Base de Données

## Pourquoi Alembic ?

**Avant (init.sql):**
- Écrase toute la base à chaque fois
- Pas de versioning
- Difficile de collaborer
- Pas de rollback possible

**Après (Alembic):**
- Migrations incrémentales versionnées
- Historique complet des changements
- Collaboration simple (merge de migrations)
- Rollback facile en cas de problème
- Auto-génération depuis les modèles SQLModel

---

## Configuration

Alembic est déjà configuré dans le projet :

```
backend/
├── alembic/                   # Dossier Alembic
│   ├── versions/              # Migrations versionnées
│   ├── env.py                 # Configuration (charge .env automatiquement)
│   └── script.py.mako         # Template pour nouvelles migrations
├── alembic.ini                # Configuration Alembic
└── main.py                    # Commande init-db utilise Alembic
```

---

## Commandes Essentielles

### 1. Initialiser la base de données

```bash
# Applique toutes les migrations
python main.py init-db
```

Équivalent à :
```bash
alembic upgrade head
```

---

### 2. Créer une nouvelle migration

Quand vous modifiez un modèle SQLModel :

```bash
# Auto-génère la migration depuis les changements de modèles
alembic revision --autogenerate -m "Description du changement"

# Exemples :
alembic revision --autogenerate -m "Add email_verified column to users"
alembic revision --autogenerate -m "Create events_tags table"
```

Alembic détecte automatiquement :
- Nouvelles tables
- Nouvelles colonnes
- Colonnes supprimées
- Changements de types
- Nouveaux index
- Nouvelles contraintes

---

### 3. Appliquer les migrations

```bash
# Appliquer toutes les migrations en attente
alembic upgrade head

# Appliquer jusqu'à une version spécifique
alembic upgrade abc123

# Appliquer la prochaine migration seulement
alembic upgrade +1
```

---

### 4. Revenir en arrière (Rollback)

```bash
# Revenir à la migration précédente
alembic downgrade -1

# Revenir à une version spécifique
alembic downgrade abc123

# Revenir au tout début (vide la base)
alembic downgrade base
```

---

### 5. Voir l'historique

```bash
# Voir toutes les migrations
alembic history

# Voir l'état actuel
alembic current

# Voir les migrations en attente
alembic heads
```

---

## Workflow de Développement

### Scénario 1: Ajouter une colonne

**1. Modifier le modèle SQLModel**

```python
# src/models/scanned_event.py
class ScannedEvent(SQLModel, table=True):
    # ...
    source_url: Optional[str] = None  # Nouvelle colonne
```

**2. Générer la migration**

```bash
alembic revision --autogenerate -m "Add source_url to scanned_events"
```

**3. Vérifier la migration générée**

```bash
cat alembic/versions/<fichier_généré>.py
```

**4. Appliquer la migration**

```bash
alembic upgrade head
```

---

### Scénario 2: Créer une nouvelle table

**1. Créer le modèle**

```python
# src/models/tag.py
from sqlmodel import SQLModel, Field

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, index=True)
```

**2. Importer dans alembic/env.py**

```python
# alembic/env.py
from src.models.tag import Tag  # noqa
```

**3. Générer la migration**

```bash
alembic revision --autogenerate -m "Create tags table"
```

**4. Appliquer**

```bash
alembic upgrade head
```

---

### Scénario 3: Collaborer avec d'autres développeurs

**Développeur A crée une migration:**

```bash
git checkout -b feat/add-ratings
# Modifie les modèles
alembic revision --autogenerate -m "Add ratings to events"
git add alembic/versions/
git commit -m "feat: Add ratings column"
git push
```

**Développeur B récupère les changements:**

```bash
git pull
alembic upgrade head  # Applique la nouvelle migration
```

**En cas de conflit de migrations:**

Alembic détecte automatiquement les branches parallèles et peut les merger.

---

## Migrations Manuelles

Parfois, l'auto-génération ne suffit pas (données à migrer, logique complexe).

### Créer une migration vide

```bash
alembic revision -m "Migrate existing event data"
```

### Exemple: Remplir une nouvelle colonne

```python
# alembic/versions/abc123_migrate_data.py
def upgrade():
    # Créer la colonne
    op.add_column('scanned_events', sa.Column('slug', sa.String(255)))

    # Remplir avec des données
    connection = op.get_bind()
    connection.execute(
        """
        UPDATE scanned_events
        SET slug = LOWER(REPLACE(title, ' ', '-'))
        """
    )

    # Rendre NOT NULL après remplissage
    op.alter_column('scanned_events', 'slug', nullable=False)

def downgrade():
    op.drop_column('scanned_events', 'slug')
```

---

## Dépannage

### "Target database is not up to date"

```bash
# Voir l'état actuel
alembic current

# Appliquer les migrations manquantes
alembic upgrade head
```

---

### "Can't locate revision identified by 'xyz'"

La migration n'existe pas localement. Faire un `git pull` pour récupérer les migrations des autres.

---

### "Multiple head revisions are present"

Plusieurs développeurs ont créé des migrations en parallèle.

```bash
# Voir les heads
alembic heads

# Merger les branches
alembic merge -m "Merge parallel migrations" head1 head2

# Appliquer le merge
alembic upgrade head
```

---

### Réinitialiser complètement la base

```bash
# Supprimer toutes les tables
alembic downgrade base

# Recréer depuis zéro
alembic upgrade head
```

Ou avec Docker :

```bash
docker-compose down -v
docker-compose up -d postgres
python main.py init-db
```

---

## Commandes Docker

### Avec PostgreSQL dans Docker

```bash
# 1. Démarrer PostgreSQL
docker-compose up -d postgres

# 2. Appliquer les migrations
python main.py init-db

# 3. Vérifier l'état
alembic current
```

---

### Dans un container backend (si activé)

```bash
# Appliquer les migrations depuis le container
docker-compose exec backend alembic upgrade head
```

---

## Best Practices

### 1. Toujours tester les migrations

```bash
# Appliquer
alembic upgrade head

# Tester l'app
python main.py scrape --max-pages 1

# Rollback pour tester le downgrade
alembic downgrade -1

# Réappliquer
alembic upgrade head
```

---

### 2. Nommer clairement les migrations

**Bon:**
```bash
alembic revision --autogenerate -m "Add email_verified column to users"
alembic revision --autogenerate -m "Create events_categories junction table"
```

**Mauvais:**
```bash
alembic revision --autogenerate -m "Update"
alembic revision --autogenerate -m "Fix"
```

---

### 3. Vérifier les migrations auto-générées

Alembic peut se tromper. Toujours vérifier le fichier généré avant de l'appliquer.

```bash
# Générer
alembic revision --autogenerate -m "Add status column"

# Vérifier
cat alembic/versions/<fichier>.py

# Si correct, appliquer
alembic upgrade head
```

---

### 4. Committer les migrations

```bash
git add alembic/versions/
git commit -m "feat: Add user authentication tables"
```

**Ne jamais** modifier une migration déjà mergée sur `main`. Créer une nouvelle migration à la place.

---

### 5. Pas de migrations sur les branches de dev longues

Sur les features branches longues, ne pas créer de migrations tant que la feature n'est pas prête à merger.

Sinon, risque de conflits avec d'autres branches.

---

## Références

- Documentation Alembic : https://alembic.sqlalchemy.org/
- SQLModel + Alembic : https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/
- Migrations tutorial : https://alembic.sqlalchemy.org/en/latest/tutorial.html

---

## Aide-mémoire

```bash
# Créer une migration auto
alembic revision --autogenerate -m "description"

# Appliquer toutes les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1

# Voir l'historique
alembic history

# Voir l'état actuel
alembic current

# Réinitialiser complètement
alembic downgrade base && alembic upgrade head
```

---

**Dernière mise à jour:** 2026-02-03
**Configuration:** Alembic 1.18+, SQLModel, PostgreSQL 15
