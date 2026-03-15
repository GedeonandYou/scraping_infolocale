"""CLI pour exporter les evenements Infolocale via l'API Algolia."""

import glob
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from src.services.algolia_service import AlgoliaService

app = typer.Typer(help="Export des evenements Infolocale via Algolia.")
console = Console()


@app.command()
def export(
    limit: int = typer.Option(
        1000, "--limit", "-n", help="Nombre d'evenements a recuperer"
    ),
    from_date: Optional[str] = typer.Option(
        None,
        "--from-date",
        "-f",
        help="Date de debut (YYYY-MM-DD). Defaut: aujourd'hui",
    ),
    to_date: Optional[str] = typer.Option(
        None, "--to-date", "-t", help="Date de fin (YYYY-MM-DD)"
    ),
    format: str = typer.Option(
        "csv", "--format", help="Format de sortie: csv ou json"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Chemin du fichier de sortie"
    ),
):
    """Exporte les evenements Infolocale en CSV ou JSON."""

    # Validation du format
    format = format.lower()
    if format not in ("csv", "json"):
        console.print(f"[red]Format invalide: {format}. Utilisez csv ou json.[/red]")
        raise typer.Exit(1)

    # Parser les dates
    if from_date:
        try:
            dt_from = datetime.strptime(from_date, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Date de debut invalide. Format attendu: YYYY-MM-DD[/red]")
            raise typer.Exit(1)
    else:
        dt_from = datetime.combine(date.today(), datetime.min.time())

    ts_from = int(dt_from.timestamp())

    ts_to = None
    if to_date:
        try:
            dt_to = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Date de fin invalide. Format attendu: YYYY-MM-DD[/red]")
            raise typer.Exit(1)
        ts_to = int(dt_to.timestamp())

    # Generer le nom de fichier par defaut : infolocale_DATE_#.ext
    if not output:
        today = date.today().strftime("%Y%m%d")
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        existing = glob.glob(str(export_dir / f"infolocale_{today}_*.{format}"))
        increment = len(existing) + 1
        output = str(export_dir / f"infolocale_{today}_{increment}.{format}")

    console.print(f"[bold]Export Infolocale[/bold]")
    console.print(f"  Limite     : {limit} evenements")
    console.print(f"  Depuis     : {dt_from.strftime('%Y-%m-%d')}")
    if ts_to:
        console.print(f"  Jusqu'au   : {to_date}")
    console.print(f"  Format     : {format.upper()}")
    console.print(f"  Fichier    : {output}")
    console.print()

    service = AlgoliaService()
    try:
        hits = service.fetch_events(
            limit=limit,
            date_from=ts_from,
            date_to=ts_to,
        )

        if not hits:
            console.print("[yellow]Aucun evenement trouve.[/yellow]")
            raise typer.Exit(0)

        if format == "json":
            result_path = service.export_to_json(hits, output_path=output)
        else:
            result_path = service.export_to_csv(hits, output_path=output)

        console.print(
            f"[green]Export termine: {len(hits)} evenements -> {result_path}[/green]"
        )
    finally:
        service.close()


if __name__ == "__main__":
    app()
