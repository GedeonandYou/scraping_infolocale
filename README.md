# Infolocale Scraper

Système complet de scraping et d'API REST pour collecter et exposer les événements du site [infolocale.fr](https://www.infolocale.fr)

## Description

Ce projet automatise la collecte d'événements locaux depuis Infolocale et expose les données via une API REST. Il inclut un scraper Selenium avec géocodage automatique (OpenRouteService) et une base de données PostgreSQL.

## ⚡ Démarrage rapide

# 1. Cloner le projet
```bash
git clone `<repo-url>`
cd scraping_infolocale
```
## 🛠️ Technologies

- **Backend**: FastAPI (Python 3.11)
- **Scraping**: Selenium + ChromeDriver / API Algolia (index `memo_events`)
- **Base de données**: PostgreSQL 16
- **Cache**: Redis 7 (géocodage)
- **Géocodage**: OpenRouteService API
- **Frontend**: React + TypeScript + Vite
- **Conteneurisation**: Docker + Docker Compose

**En local**:

```bash
# Backend
python3 -m venv venv
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
# Scraper des événements via Selenium
python main.py scrape --max-pages 10
python main.py scrape --no-geocode --max-pages 20

# Importer massivement via l'API Algolia d'Infolocale
python main.py import-algolia                     # tous les départements
python main.py import-algolia --limit 500         # limiter le nombre d'événements
python main.py import-algolia --dept vaucluse     # un seul département

# Importer depuis le CSV Open Data (data.gouv.fr)
python main.py import-opendata

# Lancer l'API
python main.py serve

# Voir l'aide
python main.py --help
```

### Import Algolia

Infolocale expose ses données via une API Algolia (index `memo_events`). Cette méthode est **plus rapide et plus complète** que le scraping Selenium.

La clé API est publique mais rotative (~30 jours). Elle est **récupérée automatiquement** depuis infolocale.fr au lancement. En cas d'échec, renseigner manuellement dans `backend/.env` :

```bash
# Récupérer depuis les DevTools de infolocale.fr
# Onglet Network → requête *.algolia.net → header X-Algolia-API-Key
ALGOLIA_APP_ID=E35VBJOT1F
ALGOLIA_API_KEY=<clé copiée depuis DevTools>
ALGOLIA_INDEX_NAME=memo_events
```

Champs importés depuis Algolia (en plus des champs communs) :
- `genre` — sous-catégorie (ex: "Animation", "Marché")
- `annule` / `complet` / `permanent` — statuts de l'événement
- `accessibilites` — accessibilité PMR, etc.
- `ages` — tranches d'âge ciblées

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
- **Gestion automatique de ChromeDriver** (webdriver-manager)
  - Plus de problème de version incompatible
  - Fonctionne sur toutes les machines sans configuration
  - Voir [CHROMEDRIVER_SOLUTION.md](CHROMEDRIVER_SOLUTION.md) pour les détails
