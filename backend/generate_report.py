"""Genere un rapport Word comparant l'approche scraping vs API a la demande."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
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

    # Header row
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

    # Data rows
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

    # -- Styles --
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
        "Scraping Algolia vs API a la demande\n"
        "pour la recuperation des evenements Infolocale"
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
        "2. Architecture actuelle (Scraping Algolia)",
        "3. Architecture proposee (API a la demande)",
        "4. Comparaison detaillee",
        "5. Analyse des risques",
        "6. Performance et scalabilite",
        "7. Cout et maintenance",
        "8. Recommandation finale",
        "9. Plan de migration",
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
        "Infolocale.fr utilise l'index Algolia memo_events qui contient plus de "
        "110 000 evenements. L'acces a cet index se fait via une \"secured key\" "
        "base64 avec un champ validUntil qui expire regulierement."
    )

    doc.add_heading("1.2 Problematique", level=2)
    doc.add_paragraph(
        "Deux approches sont possibles pour exploiter ces donnees :"
    )
    bullets = [
        ("Approche 1 (actuelle)", "Scraping massif : recuperer tous les evenements via l'API Algolia Browse, les stocker en base PostgreSQL, puis les servir via une API FastAPI."),
        ("Approche 2 (proposee)", "API a la demande : l'API FastAPI interroge Algolia directement a chaque requete utilisateur, en utilisant les filtres geographiques natifs d'Algolia."),
    ]
    for label, text in bullets:
        p = doc.add_paragraph()
        run = p.add_run(f"{label} : ")
        run.bold = True
        p.add_run(text)

    doc.add_page_break()

    # ==========================================================
    # 2. ARCHITECTURE ACTUELLE
    # ==========================================================
    doc.add_heading("2. Architecture actuelle (Scraping Algolia)", level=1)

    doc.add_heading("2.1 Pipeline de donnees", level=2)
    doc.add_paragraph(
        "L'architecture actuelle repose sur 3 pipelines d'ingestion :"
    )

    add_styled_table(
        doc,
        ["Pipeline", "Source", "Methode", "Volume"],
        [
            ["HTML Scraping", "infolocale.fr", "Selenium + BeautifulSoup", "~50 events/page"],
            ["Algolia API", "Algolia (memo_events)", "HTTPX + Browse endpoint", "110k+ events"],
            ["Open Data", "data.gouv.fr", "CSV download + parsing", "Variable"],
        ],
        col_widths=[3.5, 4, 5, 3.5],
    )

    doc.add_paragraph()

    doc.add_heading("2.2 Flux de donnees", level=2)
    flow_steps = [
        "Recuperation de la cle API Algolia (automatique via Selenium CDP)",
        "Scraping massif via l'endpoint Browse (pagination par cursor)",
        "Enrichissement : geocoding via OpenRouteService",
        "Deduplication : UPSERT PostgreSQL sur le champ uid",
        "Stockage en base PostgreSQL (table scanned_events)",
        "Exposition via API FastAPI (GET /api/v1/events)",
        "Export optionnel en CSV/JSON",
    ]
    for i, step in enumerate(flow_steps, 1):
        doc.add_paragraph(f"{i}. {step}")

    doc.add_heading("2.3 Gestion de la cle API", level=2)
    doc.add_paragraph(
        "La cle API Algolia est une secured key avec un timestamp d'expiration "
        "(validUntil). Le service algolia_key_service.py gere le renouvellement "
        "automatique via :"
    )
    for item in [
        "Lancement de Chrome headless avec options anti-detection (stealth)",
        "Chargement de infolocale.fr/activites",
        "Interception des requetes reseau via Chrome DevTools Protocol (CDP)",
        "Extraction de la cle depuis les parametres d'URL des requetes Algolia",
        "Gestion du WAF Ouest-France (attente du challenge, retries)",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("2.4 Stack technique", level=2)
    add_styled_table(
        doc,
        ["Composant", "Technologie", "Role"],
        [
            ["API", "FastAPI + Uvicorn", "Serveur REST"],
            ["ORM", "SQLModel (SQLAlchemy + Pydantic)", "Modeles et validation"],
            ["Base de donnees", "PostgreSQL 15+", "Stockage evenements"],
            ["Scraping", "Selenium 4 + HTTPX", "Recuperation donnees"],
            ["Geocoding", "OpenRouteService", "Enrichissement geographique"],
            ["Migrations", "Alembic", "Schema de base"],
            ["CLI", "Typer + Rich", "Interface en ligne de commande"],
            ["Logs", "Loguru", "Journalisation structuree"],
        ],
        col_widths=[3.5, 5, 5],
    )

    doc.add_page_break()

    # ==========================================================
    # 3. ARCHITECTURE PROPOSEE
    # ==========================================================
    doc.add_heading("3. Architecture proposee (API a la demande)", level=1)

    doc.add_heading("3.1 Principe", level=2)
    doc.add_paragraph(
        "Au lieu de scraper et stocker localement les 110k+ evenements, "
        "l'API FastAPI interroge directement Algolia a chaque requete utilisateur. "
        "Les filtres geographiques natifs d'Algolia (aroundLatLng, aroundRadius) "
        "permettent de ne recuperer que les evenements pertinents."
    )

    doc.add_heading("3.2 Flux de donnees simplifie", level=2)
    flow_steps_new = [
        "L'utilisateur envoie une requete : GET /events?lat=48.8&lng=2.3&radius=10km",
        "L'API FastAPI transforme la requete en appel Algolia",
        "Algolia retourne uniquement les evenements dans le rayon demande",
        "L'API formate et retourne la reponse au frontend",
        "Cache optionnel : les resultats sont mis en cache (Redis ou PostgreSQL)",
    ]
    for i, step in enumerate(flow_steps_new, 1):
        doc.add_paragraph(f"{i}. {step}")

    doc.add_heading("3.3 Filtres Algolia disponibles", level=2)
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

    doc.add_heading("3.4 Composants supprimes", level=2)
    doc.add_paragraph(
        "Dans cette approche, plusieurs composants deviennent inutiles :"
    )
    for item in [
        "scraper_service.py (scraping HTML Selenium)",
        "storage_service.py (stockage PostgreSQL des evenements)",
        "opendata_import_service.py (import CSV data.gouv.fr)",
        "export_events.py (export CSV/JSON)",
        "Table scanned_events (plus necessaire pour les evenements)",
        "Migrations Alembic pour la table evenements",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("3.5 Composants conserves", level=2)
    for item in [
        "algolia_service.py (adapte pour les requetes a la demande)",
        "algolia_key_service.py (renouvellement automatique de cle)",
        "geocoding_service.py (geocoding inverse si necessaire)",
        "API FastAPI (routes adaptees pour le proxy Algolia)",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_page_break()

    # ==========================================================
    # 4. COMPARAISON DETAILLEE
    # ==========================================================
    doc.add_heading("4. Comparaison detaillee", level=1)

    doc.add_heading("4.1 Tableau comparatif", level=2)
    add_styled_table(
        doc,
        ["Critere", "Scraping Algolia", "API a la demande"],
        [
            ["Fraicheur des donnees", "Donnees obsoletes entre 2 syncs", "Temps reel"],
            ["Volume stocke", "110k+ events en base", "Aucun (ou cache temporaire)"],
            ["Latence utilisateur", "Rapide (donnees locales)", "Moyenne (~200-500ms Algolia)"],
            ["Complexite infrastructure", "PostgreSQL + Alembic + Cron", "FastAPI + Redis (optionnel)"],
            ["Resilience WAF", "Risque de blocage au scraping", "Meme risque (cle API)"],
            ["Filtrage geographique", "Post-traitement cote serveur", "Natif Algolia (aroundLatLng)"],
            ["Cout de maintenance", "Eleve (3 pipelines, sync, cle)", "Faible (1 service, cle)"],
            ["Mode offline", "Oui (donnees locales)", "Non"],
            ["Analytique / stats", "Oui (requetes SQL)", "Limite (pas de donnees locales)"],
            ["Conformite legale", "Zone grise (scraping massif)", "Plus leger (usage normal API)"],
        ],
        col_widths=[4, 5.5, 5.5],
    )

    doc.add_paragraph()

    doc.add_heading("4.2 Fraicheur des donnees", level=2)
    doc.add_paragraph(
        "L'approche scraping necessite une synchronisation reguliere (cron job) "
        "pour maintenir les donnees a jour. Entre deux syncs, les evenements "
        "ajoutes, modifies ou annules sur Infolocale ne sont pas refletes.\n\n"
        "L'approche API a la demande retourne toujours les donnees les plus "
        "recentes puisqu'elle interroge Algolia en temps reel."
    )

    doc.add_heading("4.3 Filtrage geographique", level=2)
    doc.add_paragraph(
        "Avec le scraping, le filtrage geographique est fait cote serveur apres "
        "avoir recupere tous les evenements. Cela implique de stocker les "
        "coordonnees GPS et de calculer les distances.\n\n"
        "Algolia propose nativement les filtres aroundLatLng et aroundRadius "
        "qui effectuent ce calcul cote Algolia, avec des performances optimisees "
        "(index geographique). Le frontend n'a qu'a envoyer la position GPS de "
        "l'utilisateur."
    )

    doc.add_heading("4.4 Deduplication", level=2)
    doc.add_paragraph(
        "Le scraping necessite un mecanisme de deduplication (UPSERT sur uid) "
        "pour eviter les doublons entre les imports. L'API a la demande n'a pas "
        "ce probleme puisqu'elle ne stocke rien."
    )

    doc.add_page_break()

    # ==========================================================
    # 5. ANALYSE DES RISQUES
    # ==========================================================
    doc.add_heading("5. Analyse des risques", level=1)

    add_styled_table(
        doc,
        ["Risque", "Scraping", "API a la demande", "Impact"],
        [
            [
                "Expiration de la cle API",
                "Bloque le pipeline de sync",
                "Bloque les requetes utilisateur",
                "Critique (les 2)",
            ],
            [
                "Blocage WAF",
                "Bloque le scraping\n(donnees en cache restent dispo)",
                "Bloque le renouvellement de cle",
                "Eleve",
            ],
            [
                "Changement d'API Algolia",
                "Casse le scraping",
                "Casse les requetes",
                "Critique (les 2)",
            ],
            [
                "Infolocale change d'index",
                "Casse completement",
                "Casse completement",
                "Critique (les 2)",
            ],
            [
                "Rate limiting Algolia",
                "Pendant le scraping\n(110k requetes)",
                "Proportionnel au trafic\n(quelques req/min)",
                "Moyen",
            ],
            [
                "Panne PostgreSQL",
                "Plus d'acces aux donnees",
                "Pas d'impact\n(pas de base requise)",
                "Eleve (scraping)",
            ],
            [
                "Conformite RGPD/legale",
                "Stockage massif de donnees tierces",
                "Proxy sans stockage",
                "Moyen (scraping)",
            ],
        ],
        col_widths=[3.5, 4, 4, 3],
    )

    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run("Note : ")
    run.bold = True
    p.add_run(
        "Le risque d'expiration de cle est commun aux deux approches. "
        "Le service algolia_key_service.py le gere automatiquement dans les deux cas."
    )

    doc.add_page_break()

    # ==========================================================
    # 6. PERFORMANCE ET SCALABILITE
    # ==========================================================
    doc.add_heading("6. Performance et scalabilite", level=1)

    doc.add_heading("6.1 Latence", level=2)
    add_styled_table(
        doc,
        ["Operation", "Scraping (donnees locales)", "API a la demande"],
        [
            ["Requete utilisateur", "~10-50 ms (SQL local)", "~200-500 ms (Algolia)"],
            ["Sync initiale", "~5-15 min (110k events)", "Aucune"],
            ["Renouvellement de cle", "~10-15 s (Selenium)", "~10-15 s (Selenium)"],
            ["Recherche geographique", "~50-200 ms (PostGIS/SQL)", "~50-100 ms (Algolia natif)"],
        ],
        col_widths=[4.5, 5, 5],
    )

    doc.add_paragraph()

    doc.add_heading("6.2 Scalabilite", level=2)
    doc.add_paragraph(
        "Approche scraping : la scalabilite est limitee par la taille de la base "
        "PostgreSQL et le temps de synchronisation. Chaque nouvelle sync doit "
        "parcourir tous les evenements.\n\n"
        "Approche API : la scalabilite est geree par Algolia (infrastructure CDN). "
        "L'ajout d'un cache Redis permet de reduire les appels repetes a Algolia."
    )

    doc.add_heading("6.3 Cache (approche hybride)", level=2)
    doc.add_paragraph(
        "L'approche recommandee utilise un cache a plusieurs niveaux :"
    )
    for item in [
        "Cache applicatif (in-memory, TTL 5 min) : pour les requetes identiques rapprochees",
        "Cache Redis (TTL 30 min) : pour les requetes par zone geographique",
        "Cache PostgreSQL (TTL 24h, optionnel) : pour l'analytique et les stats",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_page_break()

    # ==========================================================
    # 7. COUT ET MAINTENANCE
    # ==========================================================
    doc.add_heading("7. Cout et maintenance", level=1)

    doc.add_heading("7.1 Complexite du code", level=2)
    add_styled_table(
        doc,
        ["Composant", "Scraping (lignes)", "API a la demande (lignes)"],
        [
            ["scraper_service.py", "~250", "Supprime"],
            ["algolia_service.py", "~300", "~150 (simplifie)"],
            ["algolia_key_service.py", "~280", "~280 (inchange)"],
            ["storage_service.py", "~150", "Supprime"],
            ["opendata_import_service.py", "~200", "Supprime"],
            ["export (CSV/JSON)", "~200", "Supprime"],
            ["routes.py", "~200", "~100 (simplifie)"],
            ["models + migrations", "~150", "~50 (minimal)"],
            ["Total approximatif", "~1 730 lignes", "~580 lignes"],
        ],
        col_widths=[5, 4.5, 5],
    )

    doc.add_paragraph()

    p = doc.add_paragraph()
    run = p.add_run("Reduction de ~65% du code ")
    run.bold = True
    p.add_run(
        "avec l'approche API a la demande, ce qui reduit proportionnellement "
        "la surface de bugs et l'effort de maintenance."
    )

    doc.add_heading("7.2 Infrastructure", level=2)
    add_styled_table(
        doc,
        ["Ressource", "Scraping", "API a la demande"],
        [
            ["PostgreSQL", "Requis (scanned_events)", "Optionnel (cache/users)"],
            ["Redis", "Non utilise", "Optionnel (cache)"],
            ["Chrome/Selenium", "Pour scraping + cle API", "Uniquement pour cle API"],
            ["Cron job", "Requis (sync periodique)", "Non requis"],
            ["Espace disque", "~500 Mo (110k events)", "Minimal"],
        ],
        col_widths=[4, 5, 5.5],
    )

    doc.add_page_break()

    # ==========================================================
    # 8. RECOMMANDATION FINALE
    # ==========================================================
    doc.add_heading("8. Recommandation finale", level=1)

    doc.add_heading("8.1 Approche recommandee : Hybride", level=2)
    p = doc.add_paragraph()
    run = p.add_run(
        "L'approche recommandee est un modele hybride qui combine les avantages "
        "des deux architectures :"
    )

    doc.add_paragraph()

    # Encadre recommandation
    rec_items = [
        (
            "API a la demande pour les requetes utilisateur",
            "Les recherches geographiques et par categorie sont transmises "
            "directement a Algolia avec les filtres natifs (aroundLatLng, facetFilters). "
            "Cela garantit des donnees toujours fraiches et un filtrage performant.",
        ),
        (
            "Cache intelligent",
            "Un cache Redis (TTL 15-30 min) stocke les resultats des requetes "
            "frequentes pour eviter de surcharger Algolia et reduire la latence.",
        ),
        (
            "Renouvellement automatique de la cle",
            "Le service algolia_key_service.py existant gere le renouvellement "
            "transparent de la cle API expiree.",
        ),
        (
            "Base PostgreSQL allegee",
            "PostgreSQL conserve uniquement les donnees utilisateur "
            "(favoris, preferences, historique) et eventuellement un cache "
            "d'evenements pour l'analytique.",
        ),
    ]
    for label, text in rec_items:
        p = doc.add_paragraph()
        run = p.add_run(f"{label} : ")
        run.bold = True
        run.font.color.rgb = RGBColor(46, 116, 181)
        p.add_run(text)

    doc.add_heading("8.2 Quand garder le scraping", level=2)
    doc.add_paragraph(
        "Le scraping massif reste pertinent dans les cas suivants :"
    )
    for item in [
        "Besoin d'analytique avancee (statistiques, tendances, rapports)",
        "Mode offline requis (application mobile sans connexion)",
        "Besoin de croiser avec d'autres sources de donnees localement",
        "Requirement de conserver un historique des evenements passes",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("8.3 Matrice de decision", level=2)
    add_styled_table(
        doc,
        ["Cas d'usage", "Approche recommandee"],
        [
            ["App web : chercher des evenements proches", "API a la demande"],
            ["App mobile avec mode offline", "Scraping + sync"],
            ["Dashboard analytique", "Scraping (donnees locales)"],
            ["Moteur de recommandation", "Hybride (cache + ML local)"],
            ["Simple affichage d'evenements", "API a la demande"],
            ["Export massif CSV/JSON", "Scraping"],
        ],
        col_widths=[7, 7],
    )

    doc.add_page_break()

    # ==========================================================
    # 9. PLAN DE MIGRATION
    # ==========================================================
    doc.add_heading("9. Plan de migration", level=1)

    doc.add_paragraph(
        "Si la decision est prise de migrer vers l'approche API a la demande, "
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
                "Supprimer les services inutilises (scraper, storage, opendata)",
                "Simplifier les migrations Alembic",
                "Mettre a jour la documentation",
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
        "L'approche actuelle par scraping massif a permis de construire une base "
        "solide avec 3 pipelines d'ingestion, un mecanisme de deduplication et "
        "un renouvellement automatique de la cle API. Cependant, pour un cas "
        "d'usage centre sur la recherche d'evenements par localisation, l'approche "
        "API a la demande est plus adaptee : elle est plus simple, plus fiable, "
        "et garantit des donnees toujours a jour."
    )

    doc.add_paragraph(
        "L'approche hybride recommandee conserve le meilleur des deux mondes : "
        "la fraicheur des donnees en temps reel, le filtrage geographique "
        "natif d'Algolia, et la possibilite de maintenir un cache local pour "
        "les performances et l'analytique."
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
    output_path = "data/exports/rapport_comparatif_scraping_vs_api.docx"
    from pathlib import Path
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return output_path


if __name__ == "__main__":
    path = generate_report()
    print(f"Rapport genere : {path}")
