"""Main CLI entry point for the scraper."""

import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from src.services.scraper_service import ScraperService
from src.services.storage_service import StorageService
from src.exporters.csv_exporter import CSVExporter
from src.exporters.json_exporter import JSONExporter
from src.models.database import engine, create_db_and_tables
from src.models.scanned_event import ScannedEvent
from src.utils.logger import setup_logger

app = typer.Typer(help="Infolocale Scraper CLI")
console = Console()
logger = setup_logger()


@app.command()
def init_db():
    """Initialiser la base de données."""
    console.print("[bold blue]Initialisation de la base de données...[/bold blue]")
    create_db_and_tables()
    console.print("[bold green]✓ Base de données initialisée avec succès![/bold green]")


@app.command()
def scrape(
    region: str = typer.Option(None, help="Région à scraper"),
    max_pages: int = typer.Option(5, help="Nombre maximum de pages à scraper"),
    geocode: bool = typer.Option(True, help="Activer le géocodage"),
):
    """Lancer le scraping des événements."""
    console.print(f"[bold blue]Démarrage du scraping (max_pages={max_pages})...[/bold blue]")

    scraper = ScraperService()

    try:
        saved_count = scraper.scrape_and_store(
            region=region,
            max_pages=max_pages,
            with_geocoding=geocode
        )

        console.print(f"[bold green]✓ Scraping terminé: {saved_count} événements sauvegardés[/bold green]")

    except Exception as e:
        console.print(f"[bold red]✗ Erreur lors du scraping: {e}[/bold red]")
        raise
    finally:
        scraper.close()


@app.command()
def export(
    format: str = typer.Option("json", help="Format d'export (json, csv, all)"),
    limit: int = typer.Option(None, help="Limiter le nombre d'événements exportés"),
):
    """Exporter les événements depuis la base de données."""
    console.print(f"[bold blue]Export des événements au format {format}...[/bold blue]")

    try:
        with Session(engine) as session:
            statement = select(ScannedEvent)
            if limit:
                statement = statement.limit(limit)

            events = session.exec(statement).all()

            if not events:
                console.print("[yellow]Aucun événement à exporter[/yellow]")
                return

            if format in ("json", "all"):
                json_exporter = JSONExporter()
                json_path = json_exporter.export(events)
                console.print(f"[green]✓ Export JSON: {json_path}[/green]")

            if format in ("csv", "all"):
                csv_exporter = CSVExporter()
                csv_path = csv_exporter.export(events)
                console.print(f"[green]✓ Export CSV: {csv_path}[/green]")

    except Exception as e:
        console.print(f"[bold red]✗ Erreur lors de l'export: {e}[/bold red]")
        raise


@app.command()
def stats():
    """Afficher les statistiques sur les événements."""
    console.print("[bold blue]Statistiques des événements[/bold blue]\n")

    try:
        storage = StorageService()
        total = storage.count_events()

        with Session(engine) as session:
            # Count by category
            from sqlalchemy import func
            categories = session.exec(
                select(ScannedEvent.category, func.count(ScannedEvent.id))
                .group_by(ScannedEvent.category)
                .order_by(func.count(ScannedEvent.id).desc())
            ).all()

            # Count by city (top 10)
            cities = session.exec(
                select(ScannedEvent.city, func.count(ScannedEvent.id))
                .group_by(ScannedEvent.city)
                .order_by(func.count(ScannedEvent.id).desc())
                .limit(10)
            ).all()

        # Display stats
        console.print(f"[bold]Total d'événements:[/bold] {total}\n")

        # Categories table
        if categories:
            table = Table(title="Événements par catégorie")
            table.add_column("Catégorie", style="cyan")
            table.add_column("Nombre", style="green", justify="right")

            for category, count in categories:
                table.add_row(category or "Non catégorisé", str(count))

            console.print(table)
            console.print()

        # Cities table
        if cities:
            table = Table(title="Top 10 villes")
            table.add_column("Ville", style="cyan")
            table.add_column("Nombre", style="green", justify="right")

            for city, count in cities:
                table.add_row(city or "Non spécifié", str(count))

            console.print(table)

    except Exception as e:
        console.print(f"[bold red]✗ Erreur: {e}[/bold red]")
        raise


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host de l'API"),
    port: int = typer.Option(8000, help="Port de l'API"),
    reload: bool = typer.Option(True, help="Auto-reload"),
):
    """Lancer l'API FastAPI."""
    import uvicorn
    from src.config.settings import get_settings

    settings = get_settings()

    console.print(f"[bold blue]Démarrage de l'API sur {host}:{port}...[/bold blue]")
    console.print(f"[cyan]Documentation: http://{host}:{port}/docs[/cyan]\n")

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    app()
