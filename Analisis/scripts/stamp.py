"""
stamp.py — Asigna data-id únicos a todos los <p> de la historia.

Recorre todos los seccion*.html en /secciones/ y añade data-id="xxxxxxxx"
(primeros 8 caracteres de un UUID4) a cada <p class="dialogo"> y
<p class="texto-narrativo"> que no lo tenga ya.

Uso:
    python stamp.py              # aplica cambios
    python stamp.py --dry-run    # solo muestra cuántos párrafos se sellarían
    python stamp.py --backup     # guarda .bak antes de modificar

IDs son globalmente únicos entre todas las secciones.
"""

import argparse
import shutil
import uuid
from pathlib import Path
from bs4 import BeautifulSoup

CLASES = {"dialogo", "texto-narrativo"}


def short_uid():
    return uuid.uuid4().hex[:8]


def stamp_file(html_path, dry_run=False, backup=False):
    """Añade data-id a los <p> que no lo tienen. Retorna (sellados, ya_tenian)."""
    content = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(content, "html.parser")

    sellados = 0
    ya_tenian = 0

    for tag in soup.find_all("p"):
        clases = set(tag.get("class", []))
        if not clases.intersection(CLASES):
            continue
        if tag.get("data-id"):
            ya_tenian += 1
            continue
        if not dry_run:
            tag["data-id"] = short_uid()
        sellados += 1

    if not dry_run and sellados > 0:
        if backup:
            shutil.copy(html_path, str(html_path) + ".bak")
        html_path.write_text(str(soup), encoding="utf-8")

    return sellados, ya_tenian


def main():
    parser = argparse.ArgumentParser(description="Sella parrafos con data-id unicos")
    parser.add_argument(
        "--secciones",
        default="../../secciones",
        help="Ruta a la carpeta con los HTMLs (default: ../../secciones)",
    )
    parser.add_argument("--dry-run", action="store_true", help="No modifica archivos")
    parser.add_argument("--backup", action="store_true", help="Guarda .bak antes de editar")
    args = parser.parse_args()

    carpeta = Path(args.secciones)
    archivos = sorted(carpeta.glob("seccion*.html"))

    if not archivos:
        print(f"No se encontraron archivos en {carpeta.resolve()}")
        return

    modo = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{modo}Sellando parrafos en: {carpeta.resolve()}\n")

    total_sellados = 0
    total_ya = 0

    for html in archivos:
        sellados, ya = stamp_file(html, dry_run=args.dry_run, backup=args.backup)
        total_sellados += sellados
        total_ya += ya
        if sellados or ya:
            print(f"  {html.name:30s}  nuevos={sellados:4d}  ya_tenian={ya:4d}")

    print(f"\n{modo}Resumen:")
    print(f"  Parrafos sellados  : {total_sellados}")
    print(f"  Ya tenian data-id  : {total_ya}")
    print(f"  Total procesados   : {total_sellados + total_ya}\n")


if __name__ == "__main__":
    main()
