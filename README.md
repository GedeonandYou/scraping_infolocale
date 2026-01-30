# Infolocale Scraper

Système complet de scraping et d'API REST pour collecter et exposer les événements du site [infolocale.fr](https://www.infolocale.fr).

### 2. Configuration de l'environnement

```bash
cp .env.example .env
```

```env

```

### 3. Démarrage avec Docker Compose

```bash
docker-compose up -d
J'ai encore commenter le API dans docker compose, donc il vas falloir le lancer en localhost
```

Services disponibles :

- **PostgreSQL** : `localhost:5432`
- **Adminer** (UI DB) : http://localhost:8080
- **API FastAPI** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs

### 4. Installation locale (alternative)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## ⚙️ Configuration

### Variables d'environnement

Voir [.env.example](.env.example) pour la liste complète des variables configurables.

## 💻 Utilisation

### Interface CLI

```bash
# Initialiser la base de données
python main.py init-db

# Lancer le scraping sans le geocode
python main.py scrape --max-pages 10 --geocode
# Lancer le scraping avec le geocode
python main.py scrape --max-pages 10

# Exporter les données
python main.py export --format json
python main.py export --format csv
python main.py export --format all --limit 100

# Afficher les statistiques
python main.py stats

# Lancer l'API
python main.py serve --host 0.0.0.0 --port 8000
```

### API REST

```bash
# Démarrer l'API
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Ou via le CLI
python main.py serve
```

Accéder à la documentation interactive :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## API REST

### Endpoints principaux

#### Événements

```bash
# Liste des événements (avec pagination et filtres)
GET /api/v1/events?page=1&page_size=20&city=Paris&category=Concert

# Détail d'un événement
GET /api/v1/events/{event_id}

# Créer un événement
POST /api/v1/events

# Mettre à jour un événement
PATCH /api/v1/events/{event_id}

# Supprimer un événement
DELETE /api/v1/events/{event_id}
```

#### Métadonnées

```bash
# Liste des catégories
GET /api/v1/categories

# Liste des villes
GET /api/v1/cities?state=Bretagne

# Statistiques
GET /api/v1/stats
```

### Exemples de requêtes

```bash
# Récupérer les événements à Paris
curl "http://localhost:8000/api/v1/events?city=Paris&page=1&page_size=10"

# Statistiques
curl "http://localhost:8000/api/v1/stats"
```

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install -r requirements.txt

# Lancer les tests
pytest

# Avec couverture
pytest --cov=src --cov-report=html

# Tests spécifiques
pytest tests/unit/
pytest tests/integration/
```

## Support

- Documentation : http://localhost:8000/docs
- Adminer (DB UI) : http://localhost:8080
- Logs : `logs/scraper.log`
