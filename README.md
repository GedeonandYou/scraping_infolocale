# Infolocale Scraper

Système complet de scraping et d'API REST pour collecter et exposer les événements du site [infolocale.fr](https://www.infolocale.fr)

## Description

Ce projet automatise la collecte d'événements locaux depuis Infolocale et expose les données via une API REST. Il inclut un scraper Selenium avec géocodage automatique (OpenRouteService) et une base de données PostgreSQL.

## ⚡ Démarrage rapide

# 1. Cloner le projet

git clone `<repo-url>`
cd scraping_infolocale

## 🛠️ Technologies

- **Backend**: FastAPI (Python 3.11)
- **Scraping**: Selenium + ChromeDriver
- **Base de données**: PostgreSQL 15
- **Géocodage**: OpenRouteService API
- **Frontend**: React + TypeScript + Vite
- **Conteneurisation**: Docker + Docker Compose

**En local**:

```bash
# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py api

# Frontend
cd frontend
npm install
npm run dev
```

## 🚀 Utilisation

### Commandes CLI

```bash
# Scraper des événements
python main.py scrape --max-pages 10

# Lancer l'API
python main.py api

# Scraper sans géocodage (plus rapide)
python main.py scrape --no-geocode --max-pages 20

# Voir l'aide
python main.py --help
```

### API Endpoints

**Documentation interactive**: `http://localhost:8000/docs`

**Principaux endpoints**:

- `GET /events` - Liste tous les événements
- `GET /events/{id}` - Détails d'un événement
- `GET /events/search?city=Paris` - Recherche par ville
- `GET /health` - Status de l'API

### Géocodage

Le projet utilise OpenRouteService avec respect des rate limits:

- Délai de 2 secondes entre requêtes (30 req/min)
- Géocodage automatique pendant le scraping
- Script batch pour géocoder rétroactivement: `info-dev/geocode_missing_events.py`

### Scraping

Le scraper respecte automatiquement:

- Détection des doublons (via `data-id`)
- Gestion de la pagination
- Rate limiting du géocodage
- Headless Chrome via Selenium
