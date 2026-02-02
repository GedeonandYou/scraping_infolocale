# Guide de Dépannage - Windows WSL (PostgreSQL)

## Problème: "password authentication failed for user"

Si vous voyez cette erreur lors de `python main.py init-db`:

```
OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed:
FATAL: password authentication failed for user "infolocale_user"
```

### Cause

PostgreSQL tourne dans Docker, mais le `.env` pointe vers `localhost` depuis WSL.
**Le problème:** WSL et Docker Desktop ne partagent pas toujours le même `localhost`.

---

## Solutions (par ordre de priorité)

### Solution 1: Backend local (WSL) + PostgreSQL Docker (RECOMMANDÉ)

Cette solution lance PostgreSQL dans Docker et le backend Python directement dans WSL.

**Configuration actuelle du projet:** Le service backend est commenté dans `docker-compose.yml`, donc PostgreSQL tourne seul dans Docker.

#### 1.1 Démarrer PostgreSQL avec Docker

```bash
# 1. Aller dans le dossier backend
cd /mnt/c/Users/eric/Desktop/Event/Exercice/scraping_infolocale/backend

# 2. Vérifier que Docker Desktop tourne
docker --version

# 3. Démarrer uniquement PostgreSQL
docker-compose up -d postgres

# 4. Vérifier que PostgreSQL est UP
docker-compose ps
```

Vous devez voir:
```
NAME                  COMMAND                  SERVICE    STATUS
infolocale_postgres   "docker-entrypoint.s…"   postgres   Up (healthy)
```

#### 1.2 Modifier le fichier `.env` pour WSL

Le fichier `.env` doit pointer vers l'hôte Docker depuis WSL:

```env
# DATABASE - Utiliser host.docker.internal pour WSL2
POSTGRES_USER=infolocale_user
POSTGRES_PASSWORD=pwd_infolocale
POSTGRES_DB=infolocale_db
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432

OPENROUTESERVICE_API_KEY=eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImQ0YmUzMzcwMmFkNTQxN2U5MzE1ZWU1YjVlYWE2OTdlIiwiaCI6Im11cm11cjY0In0=

API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

**Note importante:** Sur WSL2, utiliser `host.docker.internal` au lieu de `localhost`.

#### 1.3 Activer l'environnement virtuel et lancer le backend

```bash
# Activer venv
source venv/bin/activate

# Installer les dépendances (si pas déjà fait)
pip install -r requirements.txt

# Initialiser la base de données
python main.py init-db

# Lancer le scraping
python main.py scrape --max-pages 5

# Ou lancer l'API
python main.py api
```

**Avantages de cette solution:**
- Développement rapide (pas besoin de rebuild Docker à chaque modification)
- Debugging facile avec VSCode/PyCharm
- PostgreSQL isolé dans Docker (pas de pollution de l'environnement local)
- Configuration utilisée actuellement dans le projet

**Si `host.docker.internal` ne fonctionne pas**, passer à la Solution 2 ci-dessous.

---

### Solution 2: Trouver l'IP du container PostgreSQL (Alternative WSL)

Si `host.docker.internal` ne fonctionne pas sur votre configuration WSL:

#### 2.1 Récupérer l'IP du container

```bash
# Lister les containers
docker ps

# Récupérer l'IP du container postgres
docker inspect infolocale_postgres | grep '"IPAddress"'
```

Vous verrez quelque chose comme:
```json
"IPAddress": "172.18.0.2"
```

#### 2.2 Modifier `.env` avec l'IP réelle

```env
POSTGRES_HOST=172.18.0.2  # Remplacer par l'IP obtenue ci-dessus
```

#### 2.3 Tester la connexion

```bash
# Tester avec psql
psql -h 172.18.0.2 -U infolocale_user -d infolocale_db -p 5432
# Mot de passe: pwd_infolocale

# Si ça marche, lancer l'application
python main.py init-db
```

---

### Solution 3: Utiliser le port forwarding Docker

Docker Desktop sur Windows expose automatiquement les ports. Vérifier:

```bash
# Vérifier que le port 5432 est bien mappé
docker-compose ps
```

Vous devez voir:
```
scraping_infolocale-postgres-1   postgres   Up   0.0.0.0:5432->5432/tcp
```

Si le port n'est **pas** exposé, éditer `docker-compose.yml`:

```yaml
services:
  postgres:
    ports:
      - "5432:5432"  # Vérifier que cette ligne existe
```

Puis redémarrer:

```bash
docker-compose down
docker-compose up -d postgres
```

---

### Solution 4: Tester la connexion manuellement

Vérifier que PostgreSQL est accessible:

```bash
# 1. Installer psql dans WSL (si pas déjà fait)
sudo apt update
sudo apt install postgresql-client -y

# 2. Tester la connexion
psql -h localhost -U infolocale_user -d infolocale_db -p 5432
# Mot de passe: pwd_infolocale
```

**Si la connexion fonctionne:** Le problème vient du `.env` Python
**Si la connexion échoue:** Le problème vient de Docker/réseau WSL

---

### Solution 5: Réinitialiser PostgreSQL complètement

Si rien ne marche, réinitialiser tout:

```bash
# 1. Arrêter et supprimer TOUS les volumes
docker-compose down -v

# 2. Vérifier qu'il ne reste rien
docker volume ls | grep scraping_infolocale

# 3. Redémarrer proprement
docker-compose up -d postgres

# 4. Attendre 10 secondes que PostgreSQL démarre
sleep 10

# 5. Vérifier les logs
docker-compose logs postgres

# 6. Tester la connexion
docker-compose exec postgres psql -U infolocale_user -d infolocale_db
```

Dans `psql`, vous devez voir le prompt:
```
infolocale_db=#
```

Taper `\q` pour quitter.

---

## Checklist de Diagnostic

Cocher au fur et à mesure:

- [ ] Docker Desktop est lancé sur Windows
- [ ] `docker ps` montre le container `postgres` en état `Up`
- [ ] Le fichier `.env` existe dans `backend/`
- [ ] Les variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` sont définies dans `.env`
- [ ] `docker-compose logs postgres` ne montre pas d'erreurs
- [ ] `psql -h localhost -U infolocale_user -d infolocale_db` fonctionne (connexion manuelle)
- [ ] `docker-compose exec backend python main.py init-db` fonctionne (depuis Docker)

---

## Problèmes Fréquents WSL + Docker

### 1. Docker Desktop pas lancé

**Symptôme:**
```
Cannot connect to the Docker daemon
```

**Solution:**
- Ouvrir Docker Desktop sur Windows
- Attendre qu'il soit complètement démarré (icône stable)

---

### 2. Volumes Docker sur mauvais disque

**Symptôme:** Très lent, erreurs aléatoires

**Solution:** Déplacer le projet hors de `/mnt/c/`, utiliser le filesystem WSL natif:

```bash
# Déplacer le projet
mv /mnt/c/Users/eric/Desktop/Event/Exercice/scraping_infolocale ~/scraping_infolocale
cd ~/scraping_infolocale
```

---

### 3. Permissions WSL

**Symptôme:**
```
Permission denied: '.env'
```

**Solution:**
```bash
# Corriger les permissions
chmod 644 backend/.env
chmod +x backend/venv/bin/activate
```

---

### 4. Ports déjà utilisés

**Symptôme:**
```
Bind for 0.0.0.0:5432 failed: port is already allocated
```

**Solution:**

```bash
# Trouver le processus qui utilise le port 5432
netstat -ano | findstr :5432  # Sur Windows PowerShell

# Ou depuis WSL
sudo lsof -i :5432

# Tuer le processus ou changer le port dans docker-compose.yml
```

---

## Test Final

Une fois tout configuré, lancer ce test complet:

```bash
#!/bin/bash
cd /mnt/c/Users/eric/Desktop/Event/Exercice/scraping_infolocale

echo "[1/5] Arrêt des containers..."
docker-compose down -v

echo "[2/5] Démarrage de PostgreSQL..."
docker-compose up -d postgres
sleep 10

echo "[3/5] Vérification PostgreSQL..."
docker-compose exec postgres psql -U infolocale_user -d infolocale_db -c "SELECT version();"

echo "[4/5] Initialisation de la base..."
docker-compose exec backend python main.py init-db

echo "[5/5] Test scraping..."
docker-compose exec backend python main.py scrape --max-pages 1

echo "Test terminé avec succès."
```

---

## Contact

Si rien ne fonctionne après toutes ces étapes:

1. Copier les sorties de ces commandes:
   ```bash
   docker --version
   docker-compose --version
   docker ps
   docker-compose logs postgres
   cat backend/.env (masquer le mot de passe)
   ```

2. Envoyer le tout pour diagnostic approfondi.

---

**Dernière mise à jour:** 2026-01-31
**Testé sur:** WSL2 Ubuntu 20.04/22.04 + Docker Desktop for Windows
