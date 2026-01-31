# Infolocale Scraper (Backend)

Système de scraping + API REST pour collecter et exposer les événements du site [infolocale.fr](https://www.infolocale.fr).

## Sommaire

- **[Prérequis](#prérequis)**
- **[Installation (local)](#installation-local)**
- **[Configuration](#configuration)**
- **[Démarrage avec Docker Compose](#démarrage-avec-docker-compose)**
- **[Démarrage en local (sans Docker)](#démarrage-en-local-sans-docker)**
- **[Services et URLs](#services-et-urls)**
- **[CLI (scraper, export, stats)](#cli-scraper-export-stats)**
- **[API REST](#api-rest)**
- **[Tests](#tests)**
- **[Dépannage](#dépannage)**

## Prérequis

- Python 3.11+
- Docker et Docker Compose (optionnel, recommandé)

## Installation (local)

```bash
# 1) Cloner le dépôt (si besoin)
# git clone <repo> && cd backend

# 2) Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
# venv\Scripts\activate  # Windows

# 3) Installer les dépendances
pip install -r requirements.txt
```

## Configuration

Copier l'exemple d'environnement et ajuster les variables selon vos besoins :

```bash
cp .env.example .env
```

Voir `backend/.env.example` pour la liste complète des variables (DB, logs, etc.).

## Démarrage avec Docker Compose

```bash
# Démarre la base PostgreSQL et Adminer
# (si l'API est commentée dans docker-compose.yml, elle ne sera pas lancée)
docker compose up -d
```

Si l'API FastAPI est commentée dans `backend/docker-compose.yml`, lancez-la en local (voir section suivante) tout en gardant PostgreSQL sous Docker.

## Démarrage en local (sans Docker)

```bash
# Lancer l'API (rechargement auto)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Ou via le CLI
python main.py serve --host 0.0.0.0 --port 8000
```

Assurez-vous que les variables d'environnement (notamment la connexion Postgres) correspondent à votre setup (Docker ou local).

## Services et URLs

- **PostgreSQL**: `localhost:5432`
- **Adminer (UI DB)**: http://localhost:8080
- **API FastAPI**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## CLI (scraper, export, stats)

```bash
# Initialiser la base de données
python main.py init-db

# Lancer le scraping (sans géocodage)
python main.py scrape --max-pages 10

# Lancer le scraping (avec géocodage)
python main.py scrape --max-pages 10 --geocode

# Exporter les données
python main.py export --format json
python main.py export --format csv
python main.py export --format all --limit 100

# Afficher les statistiques
python main.py stats

# Lancer l'API
python main.py serve --host 0.0.0.0 --port 8000
```

## API REST

### Démarrage de l'API

```bash
# Option 1: via Uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: via le CLI
python main.py serve
```

### Endpoints principaux (exemples)

```http
# Liste des événements (pagination + filtres)
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

### Métadonnées (exemples)

```http
# Liste des catégories
GET /api/v1/categories

# Liste des villes (filtrage possible)
GET /api/v1/cities?state=Bretagne

# Statistiques
GET /api/v1/stats
```

### Exemples rapides

```bash
# Récupérer les événements à Paris
curl "http://localhost:8000/api/v1/events?city=Paris&page=1&page_size=10"

# Statistiques
curl "http://localhost:8000/api/v1/stats"
```

## Tests

```bash
# Installer les dépendances (si nécessaire)
pip install -r requirements.txt

# Lancer les tests
pytest

# Couverture
pytest --cov=src --cov-report=html

# Sous-ensembles
pytest tests/unit/
pytest tests/integration/
```

## Dépannage

- **Port déjà utilisé**: changez les ports dans `docker-compose.yml` ou ajoutez `--port` pour Uvicorn.
- **Connexion DB**: vérifiez `DATABASE_URL` dans `.env` et que Postgres est prêt (Docker: `docker compose logs -f db`).
- **API non démarrée avec Docker**: si le service API est commenté dans `docker-compose.yml`, démarrez-la en local via Uvicorn.

---

- **Docs API**: http://localhost:8000/docs
- **Adminer (DB UI)**: http://localhost:8080
- **Logs**: `logs/scraper.log`
