# Solution ChromeDriver - Gestion Automatique des Versions

## Problème Résolu

**Avant:** Erreurs de version ChromeDriver incompatible avec Chrome
```
SessionNotCreatedException: session not created: This version of ChromeDriver only supports Chrome version 120
Current browser version is 122.0.6261.94 with binary path /usr/bin/google-chrome
```

**Après:** Gestion automatique des versions, aucune configuration manuelle nécessaire

---

## Solution Implémentée: webdriver-manager

Le projet utilise maintenant `webdriver-manager` qui:
- Détecte automatiquement la version de Chrome installée
- Télécharge la version compatible de ChromeDriver
- Met en cache les drivers pour éviter les téléchargements répétés
- Fonctionne sur Linux, Windows, macOS

### Avantages

1. **Aucune configuration manuelle**
   - Plus besoin de télécharger ChromeDriver manuellement
   - Plus de problème de version incompatible
   - Fonctionne sur toutes les machines sans modification

2. **Mise à jour automatique**
   - ChromeDriver se met à jour automatiquement quand Chrome change de version
   - Pas besoin de commit de binaires dans le repo Git

3. **Multi-plateforme**
   - Fonctionne identiquement sur tous les systèmes d'exploitation
   - Détection automatique de l'architecture (x64, ARM, etc.)

---

## Installation

### Pour les nouveaux collaborateurs

```bash
# 1. Cloner le projet
git clone <repo-url>
cd scraping_infolocale/backend

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer les dépendances (inclut webdriver-manager)
pip install -r requirements.txt

# 4. Lancer le scraping (ChromeDriver se télécharge automatiquement au premier lancement)
python main.py scrape --max-pages 1
```

### Premier lancement

Au premier lancement, vous verrez:

```
[WDM] - Downloading chromedriver version 122.0.6261.94 for chrome version 122
[WDM] - Downloaded chromedriver to /home/user/.wdm/drivers/chromedriver/linux64/122.0.6261.94/chromedriver
Chrome WebDriver initialized with automatic driver management
```

Les lancements suivants réutilisent le driver en cache (instantané).

---

## Mise à Jour des Dépendances

Si vous avez déjà le projet installé:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## Cache ChromeDriver

### Emplacement du cache

Les drivers sont stockés dans:
- **Linux/macOS**: `~/.wdm/drivers/`
- **Windows**: `C:\Users\<username>\.wdm\drivers\`

### Vider le cache (si nécessaire)

```bash
# Linux/macOS
rm -rf ~/.wdm/

# Windows PowerShell
Remove-Item -Recurse -Force $env:USERPROFILE\.wdm\
```

Le driver se retéléchargera automatiquement au prochain lancement.

---

## Dépannage

### Problème: "Chrome binary not found"

**Cause:** Chrome/Chromium n'est pas installé

**Solution:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install google-chrome-stable

# Fedora/RHEL
sudo dnf install google-chrome-stable

# macOS
brew install --cask google-chrome

# Windows
# Télécharger depuis https://www.google.com/chrome/
```

---

### Problème: "Permission denied" sur le driver

**Cause:** Droits d'exécution manquants (rare avec webdriver-manager)

**Solution:**

```bash
chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver
```

---

### Problème: Téléchargement échoue (réseau d'entreprise)

**Cause:** Proxy ou firewall bloquant

**Solution:** Configurer les variables d'environnement proxy

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
python main.py scrape
```

Ou télécharger manuellement et utiliser le cache:

```bash
# Télécharger ChromeDriver manuellement depuis https://googlechromelabs.github.io/chrome-for-testing/
# Extraire dans ~/.wdm/drivers/chromedriver/linux64/<version>/
```

---

### Problème: Version de Chrome très récente non supportée

**Cause:** Chrome Beta/Dev/Canary pas encore supporté par ChromeDriver

**Solution:** Utiliser Chrome Stable

```bash
# Ubuntu: forcer Chrome Stable
sudo apt remove google-chrome-beta google-chrome-unstable
sudo apt install google-chrome-stable
```

---

## Alternative: Selenium Manager (Selenium 4.6+)

Selenium 4.6+ inclut son propre gestionnaire de drivers automatique.

**Si vous voulez utiliser Selenium Manager à la place:**

Modifier `src/services/scraper_service.py`:

```python
def _init_driver(self):
    chrome_options = Options()
    # ... options ...

    # Selenium Manager (pas besoin de Service)
    self.driver = webdriver.Chrome(options=chrome_options)
    logger.info("Chrome WebDriver initialized with Selenium Manager")
```

Retirer `webdriver-manager` de `requirements.txt`.

**Note:** webdriver-manager est plus mature et offre plus de contrôle.

---

## Configuration Avancée

### Forcer une version spécifique de ChromeDriver

```python
from webdriver_manager.chrome import ChromeDriverManager

# Forcer une version
service = Service(ChromeDriverManager(version="120.0.6099.109").install())
```

### Désactiver la vérification SSL (réseau d'entreprise)

```python
ChromeDriverManager(cache_valid_range=7).install()
```

### Changer le dossier de cache

```python
import os
os.environ['WDM_LOCAL'] = '/custom/cache/path'
```

---

## Pour les Développeurs

### Code modifié

**Fichier:** `backend/src/services/scraper_service.py`

**Avant:**
```python
chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
service = Service(executable_path=chromedriver_path)
```

**Après:**
```python
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())
```

**Fichier:** `backend/requirements.txt`

**Ajouté:**
```
webdriver-manager>=4.0.0
```

---

## Tests

Vérifier que tout fonctionne:

```bash
# Test rapide
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get('https://www.google.com')
print('Title:', driver.title)
driver.quit()
print('Success: ChromeDriver works!')
"
```

Résultat attendu:
```
[WDM] - Using cached driver
Title: Google
Success: ChromeDriver works!
```

---

## Références

- webdriver-manager GitHub: https://github.com/SergeyPirogov/webdriver_manager
- Chrome for Testing: https://googlechromelabs.github.io/chrome-for-testing/
- Selenium Documentation: https://www.selenium.dev/documentation/

---

**Dernière mise à jour:** 2026-02-02
**Testé avec:** Selenium 4.15+, Chrome 122+, webdriver-manager 4.0+
