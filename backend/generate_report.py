"""Genere un rapport Word comparant les 3 approches d'acces aux evenements Infolocale."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from datetime import date


def set_cell_shading(cell, color_hex):
    """Applique une couleur de fond a une cellule."""
    from lxml import etree
    tc_pr = cell._element.get_or_add_tcPr()
    shading_elm = etree.SubElement(tc_pr, qn("w:shd"))
    shading_elm.set(qn("w:fill"), color_hex)
    shading_elm.set(qn("w:val"), "clear")


def add_styled_table(doc, headers, rows, col_widths=None):
    """Cree un tableau stylise."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(cell, "2E74B5")

    for r, row_data in enumerate(rows):
        for c, value in enumerate(row_data):
            cell = table.rows[r + 1].cells[c]
            cell.text = str(value)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)
            if r % 2 == 1:
                set_cell_shading(cell, "D6E4F0")

    if col_widths:
        for i, width in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(width)

    return table


def generate_report():
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # ==========================================================
    # PAGE DE TITRE
    # ==========================================================
    for _ in range(6):
        doc.add_paragraph()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("RAPPORT COMPARATIF")
    run.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = RGBColor(46, 116, 181)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(
        "Trois approches pour la recuperation\n"
        "des evenements Infolocale"
    )
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(89, 89, 89)

    doc.add_paragraph()

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(
        f"Projet : scraping_infolocale\n"
        f"Date : {date.today().strftime('%d/%m/%Y')}\n"
        f"Repository : github.com/GedeonandYou/scraping_infolocale"
    )
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(127, 127, 127)

    doc.add_page_break()

    # ==========================================================
    # TABLE DES MATIERES
    # ==========================================================
    doc.add_heading("Table des matieres", level=1)
    toc_items = [
        "1. Contexte et objectifs",
        "2. V1 - Scraping HTML (architecture originale)",
        "3. V2 - Scraping via API Algolia",
        "4. V3 - API a la demande (architecture proposee)",
        "5. Comparaison detaillee des 3 approches",
        "6. Analyse des risques",
        "7. Performance et scalabilite",
        "8. Cout et maintenance",
        "9. Recommandation finale",
        "10. Plan de migration",
    ]
    for item in toc_items:
        p = doc.add_paragraph(item)
        p.paragraph_format.space_after = Pt(2)

    doc.add_page_break()

    # ==========================================================
    # 1. CONTEXTE ET OBJECTIFS
    # ==========================================================
    doc.add_heading("1. Contexte et objectifs", level=1)

    doc.add_paragraph(
        "Le projet scraping_infolocale a pour objectif de recuperer les evenements "
        "publies sur la plateforme infolocale.fr (propriete du groupe Ouest-France) "
        "et de les mettre a disposition via une API REST et une interface frontend."
    )

    doc.add_heading("1.1 Source de donnees", level=2)
    doc.add_paragraph(
        "Infolocale.fr est une plateforme d'evenements locaux couvrant l'ensemble "
        "du territoire francais. Le site affiche les evenements sous forme de cartes "
        "HTML et utilise en interne un index Algolia (memo_events, 110 000+ evenements) "
        "pour la recherche cote frontend."
    )

    doc.add_heading("1.2 Les trois approches", level=2)
    doc.add_paragraph(
        "Ce rapport compare trois architectures possibles pour exploiter ces donnees :"
    )
    approaches = [
        (
            "V1 - Scraping HTML (originale)",
            "Parcourir les pages HTML d'infolocale.fr avec Selenium et "
            "BeautifulSoup pour extraire les evenements, les stocker en base "
            "PostgreSQL, puis les servir via une API FastAPI.",
        ),
        (
            "V2 - Scraping Algolia",
            "Interroger directement l'API Algolia (index memo_events) pour "
            "recuperer massivement les evenements, les stocker en base et les servir "
            "via l'API. Necessite une cle API avec auto-renouvellement.",
        ),
        (
            "V3 - API a la demande (proposee)",
            "L'API FastAPI interroge Algolia en temps reel a chaque requete "
            "utilisateur, en utilisant les filtres geographiques natifs d'Algolia. "
            "Pas de stockage local des evenements.",
        ),
    ]
    for label, text in approaches:
        p = doc.add_paragraph()
        run = p.add_run(f"{label} : ")
        run.bold = True
        p.add_run(text)

    doc.add_page_break()

    # ==========================================================
    # 2. V1 - SCRAPING HTML
    # ==========================================================
    doc.add_heading("2. V1 - Scraping HTML (architecture originale)", level=1)

    doc.add_heading("2.1 Principe", level=2)
    doc.add_paragraph(
        "L'architecture originale du projet repose sur le scraping classique des pages "
        "HTML du site infolocale.fr. Un navigateur Chrome pilote par Selenium charge "
        "chaque page de resultats, puis BeautifulSoup extrait les informations des "
        "cartes d'evenements."
    )

    doc.add_heading("2.2 Pipeline de donnees", level=2)
    flow_steps = [
        "Selenium charge une page de resultats sur infolocale.fr",
        "BeautifulSoup parse le HTML et extrait les cartes (.memo-card)",
        "Chaque carte est transformee en objet evenement (titre, date, lieu, image...)",
        "Les dates en francais sont parsees (ex: \"sam. 15 mars\" -> 2026-03-15)",
        "Les evenements sont stockes en base PostgreSQL (table scanned_events)",
        "Deduplication via UPSERT sur le champ uid (infolocale_{data_id})",
        "Enrichissement optionnel : geocoding via OpenRouteService",
        "Exposition via API FastAPI (GET /api/v1/events)",
    ]
    for i, step in enumerate(flow_steps, 1):
        doc.add_paragraph(f"{i}. {step}")

    doc.add_heading("2.3 Stack technique", level=2)
    add_styled_table(
        doc,
        ["Composant", "Technologie", "Role"],
        [
            ["Scraping", "Selenium 4 + BeautifulSoup", "Navigation et parsing HTML"],
            ["Driver", "webdriver-manager", "Gestion automatique de ChromeDriver"],
            ["API", "FastAPI + Uvicorn", "Serveur REST"],
            ["ORM", "SQLModel (SQLAlchemy + Pydantic)", "Modeles et validation"],
            ["Base de donnees", "PostgreSQL 15+", "Stockage evenements"],
            ["Geocoding", "OpenRouteService", "Enrichissement geographique"],
            ["Migrations", "Alembic", "Schema de base"],
            ["CLI", "Typer + Rich", "Interface en ligne de commande"],
        ],
        col_widths=[3.5, 5, 5],
    )

    doc.add_heading("2.4 Limites de cette approche", level=2)
    for item in [
        "Lent : ~50 evenements par page, pagination manuelle, 2s de delai entre chaque page",
        "Fragile : depend de la structure HTML (selecteurs CSS .memo-card, .gender, .day...)",
        "WAF : le site est protege par un WAF Ouest-France qui bloque les navigateurs headless",
        "Incomplet : seules les informations visibles sur la carte sont recuperees (pas de description complete)",
        "Volume limite : scraper 110k evenements prendrait des heures",
        "Maintenance : tout changement de design du site casse les selecteurs",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_page_break()

    # ==========================================================
    # 3. V2 - SCRAPING ALGOLIA
    # ==========================================================
    doc.add_heading("3. V2 - Scraping via API Algolia", level=1)

    doc.add_heading("3.1 Principe", level=2)
    doc.add_paragraph(
        "Cette approche contourne le HTML en interrogeant directement l'API Algolia "
        "utilisee par le frontend d'infolocale.fr. L'index memo_events contient "
        "l'integralite des evenements avec toutes leurs metadonnees (titre, texte, "
        "lieu, coordonnees GPS, dates, categories, photos...)."
    )

    doc.add_heading("3.2 Pipeline de donnees", level=2)
    flow_steps_v2 = [
        "Appel a l'endpoint Browse d'Algolia (pagination par cursor, sans limite de 1000)",
        "Recuperation de tous les evenements avec leurs metadonnees completes",
        "Aplatissement des champs imbriques (lieu, rubrique, _geoloc, photo)",
        "Stockage en base PostgreSQL ou export direct en CSV/JSON",
        "Exposition via API FastAPI",
    ]
    for i, step in enumerate(flow_steps_v2, 1):
        doc.add_paragraph(f"{i}. {step}")

    doc.add_heading("3.3 Gestion de la cle API", level=2)
    doc.add_paragraph(
        "L'acces a l'API Algolia necessite une \"secured key\" (base64) avec un "
        "champ validUntil qui expire regulierement. Le service algolia_key_service.py "
        "gere le renouvellement automatique :"
    )
    for item in [
        "Lancement de Chrome headless avec options anti-detection (stealth)",
        "Chargement de infolocale.fr/activites pour declencher les requetes Algolia",
        "Interception des requetes reseau via Chrome DevTools Protocol (CDP)",
        "Extraction de la cle depuis les parametres d'URL (x-algolia-api-key)",
        "Gestion du WAF Ouest-France (detection de la page challenge, attente, retries)",
        "Renouvellement transparent : si la cle expire en cours d'export, elle est renouvelee automatiquement",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("3.4 Avantages par rapport a V1", level=2)
    for item in [
        "Beaucoup plus rapide : 1000 evenements par requete vs ~50 par page HTML",
        "Donnees completes : texte integral, coordonnees GPS, tarifs, accessibilite...",
        "Plus stable : pas de dependance aux selecteurs CSS du frontend",
        "Volume : peut recuperer les 110k+ evenements en quelques minutes",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("3.5 Limites", level=2)
    for item in [
        "Cle API expirant regulierement (necessite Selenium pour le renouvellement)",
        "Dependance a l'index Algolia d'Infolocale (s'il change, tout casse)",
        "Donnees pas forcement a jour entre deux syncs",
        "Necessite toujours une base PostgreSQL pour le stockage",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_page_break()

    # ==========================================================
    # 4. V3 - API A LA DEMANDE
    # ==========================================================
    doc.add_heading("4. V3 - API a la demande (architecture proposee)", level=1)

    doc.add_heading("4.1 Principe", level=2)
    doc.add_paragraph(
        "Au lieu de scraper et stocker localement les 110k+ evenements, "
        "l'API FastAPI interroge directement Algolia a chaque requete utilisateur. "
        "Les filtres geographiques natifs d'Algolia (aroundLatLng, aroundRadius) "
        "permettent de ne recuperer que les evenements pertinents."
    )

    doc.add_heading("4.2 Flux de donnees", level=2)
    flow_steps_v3 = [
        "L'utilisateur envoie une requete : GET /events?lat=48.8&lng=2.3&radius=10km",
        "L'API FastAPI transforme la requete en appel Algolia avec les filtres natifs",
        "Algolia retourne uniquement les evenements dans le rayon demande",
        "L'API formate et retourne la reponse au frontend",
        "Cache optionnel : les resultats sont mis en cache (Redis ou in-memory)",
    ]
    for i, step in enumerate(flow_steps_v3, 1):
        doc.add_paragraph(f"{i}. {step}")

    doc.add_heading("4.3 Filtres Algolia disponibles", level=2)
    add_styled_table(
        doc,
        ["Parametre Algolia", "Description", "Exemple"],
        [
            ["aroundLatLng", "Centre de recherche (lat, lng)", "48.8566,2.3522"],
            ["aroundRadius", "Rayon en metres", "10000 (10 km)"],
            ["numericFilters", "Filtres sur dates", "date-first>=1710460800"],
            ["facetFilters", "Filtres sur categories", "rubrique.lvl0:Concert"],
            ["hitsPerPage", "Nombre de resultats par page", "20"],
            ["page", "Numero de page", "0"],
        ],
        col_widths=[4, 5, 4.5],
    )

    doc.add_paragraph()

    doc.add_heading("4.4 Composants supprimes par rapport a V1/V2", level=2)
    for item in [
        "scraper_service.py (scraping HTML Selenium — V1)",
        "storage_service.py (stockage PostgreSQL des evenements)",
        "opendata_import_service.py (import CSV data.gouv.fr)",
        "export_events.py (export CSV/JSON)",
        "Table scanned_events (plus necessaire pour les evenements)",
        "Migrations Alembic pour la table evenements",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("4.5 Composants conserves", level=2)
    for item in [
        "algolia_service.py (adapte pour les requetes a la demande avec filtres geo)",
        "algolia_key_service.py (renouvellement automatique de cle — identique a V2)",
        "geocoding_service.py (geocoding inverse si necessaire)",
        "API FastAPI (routes adaptees pour le proxy Algolia)",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_page_break()

    # ==========================================================
    # 5. COMPARAISON DETAILLEE
    # ==========================================================
    doc.add_heading("5. Comparaison detaillee des 3 approches", level=1)

    doc.add_heading("5.1 Tableau comparatif", level=2)
    add_styled_table(
        doc,
        ["Critere", "V1 - Scraping HTML", "V2 - Scraping Algolia", "V3 - API a la demande"],
        [
            [
                "Fraicheur des donnees",
                "Obsoletes entre 2 syncs",
                "Obsoletes entre 2 syncs",
                "Temps reel",
            ],
            [
                "Richesse des donnees",
                "Limitee (carte HTML)",
                "Complete (toutes les metadonnees)",
                "Complete (toutes les metadonnees)",
            ],
            [
                "Volume stocke",
                "Variable (scraping lent)",
                "110k+ events en base",
                "Aucun (ou cache temporaire)",
            ],
            [
                "Latence utilisateur",
                "Rapide (SQL local)",
                "Rapide (SQL local)",
                "Moyenne (~200-500ms)",
            ],
            [
                "Complexite infra",
                "PostgreSQL + Selenium + Cron",
                "PostgreSQL + Selenium (cle) + Cron",
                "FastAPI + Redis (optionnel)",
            ],
            [
                "Resilience WAF",
                "Bloquant (chaque page)",
                "Uniquement pour la cle API",
                "Uniquement pour la cle API",
            ],
            [
                "Filtrage geographique",
                "Post-traitement serveur",
                "Post-traitement serveur",
                "Natif Algolia (aroundLatLng)",
            ],
            [
                "Gestion de cle Algolia",
                "Non necessaire",
                "Requise (auto-refresh)",
                "Requise (auto-refresh)",
            ],
            [
                "Mode offline",
                "Oui",
                "Oui",
                "Non",
            ],
            [
                "Maintenance",
                "Elevee (selecteurs CSS)",
                "Moyenne (cle API)",
                "Faible",
            ],
            [
                "Conformite legale",
                "Zone grise (scraping)",
                "Zone grise (scraping massif)",
                "Plus leger (usage normal)",
            ],
        ],
        col_widths=[3, 3.5, 3.5, 3.5],
    )

    doc.add_paragraph()

    doc.add_heading("5.2 Fraicheur des donnees", level=2)
    doc.add_paragraph(
        "Les approches V1 et V2 necessitent une synchronisation reguliere (cron job) "
        "pour maintenir les donnees a jour. Entre deux syncs, les evenements "
        "ajoutes, modifies ou annules sur Infolocale ne sont pas refletes.\n\n"
        "L'approche V3 retourne toujours les donnees les plus recentes puisqu'elle "
        "interroge Algolia en temps reel a chaque requete utilisateur."
    )

    doc.add_heading("5.3 Filtrage geographique", level=2)
    doc.add_paragraph(
        "Avec V1 et V2, le filtrage geographique est fait cote serveur apres "
        "avoir recupere tous les evenements. Cela implique de stocker les "
        "coordonnees GPS et de calculer les distances.\n\n"
        "V3 utilise les filtres natifs d'Algolia (aroundLatLng, aroundRadius) "
        "qui effectuent ce calcul cote Algolia avec des performances optimisees "
        "(index geographique). Le frontend n'a qu'a envoyer la position de l'utilisateur."
    )

    doc.add_heading("5.4 Robustesse face au WAF", level=2)
    doc.add_paragraph(
        "V1 est la plus vulnerable : chaque page scrapee passe par le WAF "
        "Ouest-France, qui peut bloquer le navigateur headless a tout moment.\n\n"
        "V2 et V3 ne sont exposees au WAF que lors du renouvellement de la cle API "
        "(une seule visite de page necessaire), ce qui reduit considerablement "
        "le risque de blocage."
    )

    doc.add_page_break()

    # ==========================================================
    # 6. ANALYSE DES RISQUES
    # ==========================================================
    doc.add_heading("6. Analyse des risques", level=1)

    add_styled_table(
        doc,
        ["Risque", "V1 - HTML", "V2 - Algolia", "V3 - API demande"],
        [
            [
                "Blocage WAF",
                "Critique\n(chaque page)",
                "Faible\n(cle uniquement)",
                "Faible\n(cle uniquement)",
            ],
            [
                "Changement design HTML",
                "Critique\n(selecteurs cassent)",
                "Aucun impact",
                "Aucun impact",
            ],
            [
                "Expiration cle Algolia",
                "Aucun impact",
                "Moyen\n(auto-refresh gere)",
                "Moyen\n(auto-refresh gere)",
            ],
            [
                "Changement index Algolia",
                "Aucun impact",
                "Critique",
                "Critique",
            ],
            [
                "Rate limiting",
                "Eleve\n(nombreuses pages)",
                "Moyen\n(browse massif)",
                "Faible\n(quelques req/min)",
            ],
            [
                "Panne PostgreSQL",
                "Critique\n(plus de donnees)",
                "Critique\n(plus de donnees)",
                "Aucun impact\n(pas de base requise)",
            ],
            [
                "Conformite legale",
                "Risque eleve\n(scraping HTML)",
                "Risque moyen\n(scraping API)",
                "Risque faible\n(usage proxy)",
            ],
        ],
        col_widths=[3.5, 3.5, 3.5, 3.5],
    )

    doc.add_page_break()

    # ==========================================================
    # 7. PERFORMANCE ET SCALABILITE
    # ==========================================================
    doc.add_heading("7. Performance et scalabilite", level=1)

    doc.add_heading("7.1 Latence", level=2)
    add_styled_table(
        doc,
        ["Operation", "V1 - HTML", "V2 - Algolia", "V3 - API demande"],
        [
            [
                "Scraping initial",
                "Plusieurs heures\n(110k events)",
                "~5-15 min\n(110k events)",
                "Aucun",
            ],
            [
                "Requete utilisateur",
                "~10-50 ms\n(SQL local)",
                "~10-50 ms\n(SQL local)",
                "~200-500 ms\n(Algolia distant)",
            ],
            [
                "Recherche geographique",
                "~50-200 ms\n(calcul serveur)",
                "~50-200 ms\n(calcul serveur)",
                "~50-100 ms\n(index Algolia natif)",
            ],
            [
                "Renouvellement cle",
                "Non applicable",
                "~10-15 s\n(Selenium)",
                "~10-15 s\n(Selenium)",
            ],
        ],
        col_widths=[4, 3.5, 3.5, 3.5],
    )

    doc.add_paragraph()

    doc.add_heading("7.2 Scalabilite", level=2)
    doc.add_paragraph(
        "V1 : la scalabilite est tres limitee. Le temps de scraping croit "
        "lineairement avec le nombre de pages, et le WAF peut bloquer a tout moment.\n\n"
        "V2 : meilleure scalabilite grace a l'API Algolia, mais la taille de la base "
        "PostgreSQL et le temps de synchronisation restent des facteurs limitants.\n\n"
        "V3 : la scalabilite est geree par Algolia (infrastructure CDN mondiale). "
        "L'ajout d'un cache Redis permet de reduire les appels repetes."
    )

    doc.add_heading("7.3 Cache (approche V3)", level=2)
    doc.add_paragraph(
        "L'approche V3 peut utiliser un cache a plusieurs niveaux :"
    )
    for item in [
        "Cache applicatif (in-memory, TTL 5 min) : pour les requetes identiques rapprochees",
        "Cache Redis (TTL 30 min) : pour les requetes par zone geographique",
        "Cache PostgreSQL (TTL 24h, optionnel) : pour l'analytique et les stats",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_page_break()

    # ==========================================================
    # 8. COUT ET MAINTENANCE
    # ==========================================================
    doc.add_heading("8. Cout et maintenance", level=1)

    doc.add_heading("8.1 Complexite du code", level=2)
    add_styled_table(
        doc,
        ["Composant", "V1 - HTML", "V2 - Algolia", "V3 - API demande"],
        [
            ["scraper_service.py", "~250 lignes", "Inutilise", "Supprime"],
            ["algolia_service.py", "Absent", "~300 lignes", "~150 (simplifie)"],
            ["algolia_key_service.py", "Absent", "~280 lignes", "~280 (inchange)"],
            ["storage_service.py", "~150 lignes", "~150 lignes", "Supprime"],
            ["opendata_import_service.py", "~200 lignes", "~200 lignes", "Supprime"],
            ["export (CSV/JSON)", "~200 lignes", "~200 lignes", "Supprime"],
            ["routes.py", "~200 lignes", "~200 lignes", "~100 (simplifie)"],
            ["models + migrations", "~150 lignes", "~150 lignes", "~50 (minimal)"],
            ["Total approximatif", "~1 150 lignes", "~1 480 lignes", "~580 lignes"],
        ],
        col_widths=[4, 3, 3, 3],
    )

    doc.add_paragraph()

    doc.add_heading("8.2 Infrastructure", level=2)
    add_styled_table(
        doc,
        ["Ressource", "V1 - HTML", "V2 - Algolia", "V3 - API demande"],
        [
            ["PostgreSQL", "Requis", "Requis", "Optionnel (cache)"],
            ["Redis", "Non utilise", "Non utilise", "Optionnel (cache)"],
            ["Chrome/Selenium", "Requis (scraping)", "Requis (cle API)", "Requis (cle API)"],
            ["Cron job", "Requis (sync)", "Requis (sync)", "Non requis"],
            ["Espace disque", "~500 Mo", "~500 Mo", "Minimal"],
        ],
        col_widths=[4, 3, 3.5, 3.5],
    )

    doc.add_page_break()

    # ==========================================================
    # 9. RECOMMANDATION FINALE
    # ==========================================================
    doc.add_heading("9. Recommandation finale", level=1)

    doc.add_heading("9.1 Synthese", level=2)
    doc.add_paragraph(
        "V1 (scraping HTML) a permis de demarrer le projet et de valider le concept, "
        "mais cette approche est fragile, lente et limitee en donnees.\n\n"
        "V2 (scraping Algolia) a apporte un gain majeur en termes de vitesse, de "
        "completude des donnees et de stabilite. Le mecanisme d'auto-renouvellement "
        "de la cle API resout le probleme de l'expiration.\n\n"
        "V3 (API a la demande) est l'evolution logique pour un cas d'usage centre "
        "sur la recherche d'evenements par localisation : elle est plus simple, "
        "garantit des donnees fraiches, et exploite le filtrage geographique natif d'Algolia."
    )

    doc.add_heading("9.2 Approche recommandee : Hybride V2+V3", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "L'approche recommandee combine les avantages de V2 et V3 :"
    )

    doc.add_paragraph()

    rec_items = [
        (
            "API a la demande pour les requetes utilisateur (V3)",
            "Les recherches geographiques et par categorie sont transmises "
            "directement a Algolia avec les filtres natifs (aroundLatLng, facetFilters). "
            "Donnees toujours fraiches, filtrage performant.",
        ),
        (
            "Cache intelligent",
            "Un cache Redis (TTL 15-30 min) stocke les resultats des requetes "
            "frequentes pour reduire la latence et eviter de surcharger Algolia.",
        ),
        (
            "Renouvellement automatique de la cle (V2)",
            "Le service algolia_key_service.py gere le renouvellement "
            "transparent de la cle API expiree, commun a V2 et V3.",
        ),
        (
            "Export massif optionnel (V2)",
            "Conserver la possibilite d'export CSV/JSON via algolia_service.py "
            "pour les besoins d'analytique ou d'archivage.",
        ),
    ]
    for label, text in rec_items:
        p = doc.add_paragraph()
        run = p.add_run(f"{label} : ")
        run.bold = True
        run.font.color.rgb = RGBColor(46, 116, 181)
        p.add_run(text)

    doc.add_heading("9.3 Matrice de decision", level=2)
    add_styled_table(
        doc,
        ["Cas d'usage", "Approche recommandee"],
        [
            ["App web : chercher des evenements proches", "V3 - API a la demande"],
            ["App mobile avec mode offline", "V2 - Scraping Algolia + sync"],
            ["Dashboard analytique", "V2 - Scraping Algolia (donnees locales)"],
            ["Moteur de recommandation", "Hybride V2+V3 (cache + ML local)"],
            ["Simple affichage d'evenements", "V3 - API a la demande"],
            ["Export massif CSV/JSON", "V2 - Scraping Algolia"],
            ["Prototype rapide", "V1 - Scraping HTML (deja en place)"],
        ],
        col_widths=[7, 7],
    )

    doc.add_page_break()

    # ==========================================================
    # 10. PLAN DE MIGRATION
    # ==========================================================
    doc.add_heading("10. Plan de migration vers V3", level=1)

    doc.add_paragraph(
        "Si la decision est prise de migrer vers l'approche V3 (API a la demande), "
        "voici les etapes recommandees :"
    )

    phases = [
        (
            "Phase 1 : Adapter AlgoliaService (1-2 jours)",
            [
                "Ajouter les methodes de recherche geographique (aroundLatLng, aroundRadius)",
                "Ajouter le support des facetFilters pour les categories",
                "Transformer les hits Algolia en schema EventRead existant",
            ],
        ),
        (
            "Phase 2 : Creer les nouveaux endpoints API (1-2 jours)",
            [
                "GET /events?lat=...&lng=...&radius=... (recherche geo)",
                "GET /events?category=...&city=... (filtres)",
                "Conserver la pagination (page, page_size)",
            ],
        ),
        (
            "Phase 3 : Ajouter le cache (1 jour)",
            [
                "Integrer Redis comme cache de resultats",
                "Definir les cles de cache (hash de la requete)",
                "Configurer les TTL par type de requete",
            ],
        ),
        (
            "Phase 4 : Adapter le frontend (1-2 jours)",
            [
                "Mettre a jour les appels API pour utiliser les nouveaux endpoints",
                "Passer la geolocalisation du navigateur a l'API",
                "Gerer le chargement (indicateur pendant l'appel Algolia)",
            ],
        ),
        (
            "Phase 5 : Nettoyage (1 jour)",
            [
                "Supprimer scraper_service.py (V1 obsolete)",
                "Simplifier les migrations Alembic",
                "Mettre a jour la documentation",
                "Conserver algolia_service.py et export_events.py pour l'export ponctuel",
            ],
        ),
    ]

    for phase_title, steps in phases:
        doc.add_heading(phase_title, level=2)
        for step in steps:
            doc.add_paragraph(step, style="List Bullet")

    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run("Effort total estime : 5 a 8 jours de developpement")
    run.bold = True

    doc.add_page_break()

    # ==========================================================
    # CONCLUSION
    # ==========================================================
    doc.add_heading("Conclusion", level=1)

    doc.add_paragraph(
        "Le projet a evolue en trois etapes naturelles :\n\n"
        "V1 (scraping HTML) a permis de valider le concept et de construire "
        "l'infrastructure de base (API, base de donnees, modeles).\n\n"
        "V2 (scraping Algolia) a apporte un saut qualitatif majeur : acces a "
        "l'integralite des 110k+ evenements avec toutes leurs metadonnees, "
        "et un mecanisme robuste de renouvellement de cle API.\n\n"
        "V3 (API a la demande) est l'evolution naturelle pour un produit centre "
        "sur la recherche d'evenements par localisation. Elle simplifie "
        "drastiquement l'architecture tout en garantissant des donnees toujours "
        "a jour et un filtrage geographique performant.\n\n"
        "L'approche hybride V2+V3 recommandee permet de conserver le meilleur de "
        "chaque version selon les besoins."
    )

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("--- Fin du rapport ---")
    run.font.color.rgb = RGBColor(127, 127, 127)
    run.italic = True

    # ==========================================================
    # SAUVEGARDER
    # ==========================================================
    output_path = "doc/rapport_comparatif_scraping_vs_api.docx"
    from pathlib import Path
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return output_path


if __name__ == "__main__":
    path = generate_report()
    print(f"Rapport genere : {path}")
