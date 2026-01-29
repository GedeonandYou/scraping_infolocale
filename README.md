# Infolocale Scraper

Système complet de scraping et d'API REST pour collecter et exposer les événements du site [infolocale.fr](https://www.infolocale.fr).

## 📋 Table des matières

- [Caractéristiques](#caractéristiques)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API REST](#api-rest)
- [Tests](#tests)
- [Documentation](#documentation)

## ✨ Caractéristiques

### MVP (Minimum Viable Product)
- ✅ Scraping automatisé des événements depuis Infolocale.fr
- ✅ Pagination automatique
- ✅ Stockage PostgreSQL avec déduplication (champ `uid`)
- ✅ Géocodage via Google Places API (latitude/longitude)
- ✅ Logging complet des opérations
- ✅ Export CSV et JSON
- ✅ API REST FastAPI avec documentation Swagger
- ✅ Docker Compose (PostgreSQL + Adminer + API)

### Fonctionnalités avancées
- Rate limiting respectueux
- Retry automatique avec backoff exponentiel
- Cache des résultats de géocodage
- Interface CLI interactive (Typer + Rich)
- Statistiques et métriques

## 🏗 Architecture

```
src/
├── api/              # Endpoints FastAPI
├── models/           # Modèles SQLModel (ORM)
├── schemas/          # Schémas Pydantic (validation)
├── services/         # Logique métier
│   ├── scraper_service.py
│   ├── geocoding_service.py
│   └── storage_service.py
├── exporters/        # Export CSV/JSON
├── utils/            # Utilitaires (logging)
└── config/           # Configuration

docker/               # Fichiers Docker
tests/                # Tests unitaires et d'intégration
data/exports/         # Données exportées
logs/                 # Logs applicatifs
```

## 📦 Prérequis

- Python 3.10+
- Docker & Docker Compose
- Clé API Google Places (pour le géocodage)

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone <repo_url>
cd scraping_infolocale
```

### 2. Configuration de l'environnement

```bash
cp .env.example .env
```

Éditer le fichier `.env` :
```env
# Database
POSTGRES_USER=infolocale_user
POSTGRES_PASSWORD=votre_mot_de_passe_securise
POSTGRES_DB=infolocale_db

# Google Places API
GOOGLE_PLACES_API_KEY=votre_cle_api_google

# Scraping
SCRAPING_DELAY=2
SCRAPING_USER_AGENT=InfoLocaleScraper/1.0 (Educational Project; contact@example.com)
```

### 3. Démarrage avec Docker Compose

```bash
docker-compose up -d
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

### Google Places API

1. Créer un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activer l'API "Places API"
3. Créer une clé API
4. Ajouter la clé dans `.env` : `GOOGLE_PLACES_API_KEY=...`

## 💻 Utilisation

### Interface CLI

```bash
# Initialiser la base de données
python main.py init-db

# Lancer le scraping
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

### API REST

```bash
# Démarrer l'API
uvicorn src.main:app --reload

# Ou via le CLI
python main.py serve
```

Accéder à la documentation interactive :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🔌 API REST

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

## 📊 Modèle de données

### Table `scanned_events`

Conforme au cahier des charges (section 5) :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | SERIAL | Clé primaire |
| `user_id` | INTEGER | FK vers `users(id)` |
| `uid` | VARCHAR(100) | Identifiant unique (déduplication) |
| `title` | VARCHAR(500) | Titre de l'événement |
| `category` | VARCHAR(255) | Catégorie |
| `begin_date` | DATE | Date de début |
| `description` | TEXT | Description |
| `city` | VARCHAR(200) | Ville |
| `latitude` | DOUBLE PRECISION | Latitude GPS |
| `longitude` | DOUBLE PRECISION | Longitude GPS |
| `place_id` | VARCHAR(255) | Google Place ID |
| ... | ... | (voir [docker/init.sql](docker/init.sql)) |

### Index optimisés

- `idx_scanned_events_user` : sur `user_id`
- `idx_scanned_events_private` : sur `is_private`
- `idx_scanned_events_coords` : sur `(latitude, longitude)`
- `idx_scanned_events_uid` : sur `uid` (déduplication)
- `idx_scanned_events_city` : sur `city`

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** : Schéma d'architecture détaillé
- **[DATABASE.md](docs/DATABASE.md)** : Schéma de la base de données
- **[LEGAL.md](docs/LEGAL.md)** : Aspects légaux et éthiques du scraping
- **[API.md](docs/API.md)** : Documentation complète de l'API

## 🛡 Aspects légaux

Ce projet respecte :
- ✅ `robots.txt` du site cible
- ✅ Rate limiting (délai de 2s entre requêtes)
- ✅ User-Agent identifiable
- ✅ Pas de collecte de données personnelles
- ✅ Respect du RGPD

**Note** : Infolocale propose des données ouvertes sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/donnees-evenementielles-infolocale/) (licence ODbL).

## 🤝 Contribution

Ce projet est réalisé dans un cadre pédagogique. Pour toute question ou suggestion, ouvrir une issue.

## 📄 Licence

Projet éducatif - Tous droits réservés.

## 👨‍💻 Auteur

Projet Scraping Infolocale - Janvier 2026

---

## 🚀 Quick Start

```bash
# 1. Configuration
cp .env.example .env
# Éditer .env avec vos credentials

# 2. Démarrer les services Docker
docker compose up -d

# 3. Initialiser la base de données
python main.py init-db

# 4. Importer les données (CSV d'exemple)
python main.py import-opendata --csv-path data/example_events.csv

# 5. Voir les stats
python main.py stats

# 6. Lancer l'API
python main.py serve

# 7. Accéder à la documentation
# http://localhost:8000/docs
```

**⚠️ Note** : Les données Open Data d'Infolocale ne sont plus accessibles via l'ancienne API.
Consultez [DATASOURCES.md](DATASOURCES.md) pour les alternatives.

## 📞 Support

- Documentation : http://localhost:8000/docs
- Adminer (DB UI) : http://localhost:8080
- Logs : `logs/scraper.log`
