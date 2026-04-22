"""
patch.py — Aplica los cambios del archivo temporal a los HTMLs originales.
Compara párrafos por posición (data-source + orden dentro de la sección)
y reemplaza solo los que cambiaron.

Uso:
    python patch.py                          # usa story_temp.html por default
    python patch.py --input mi_contexto.html
    python patch.py --input story_temp.html --dry-run   # solo muestra cambios
    python patch.py --input story_temp.html --backup    # guarda .bak antes de editar

Cómo funciona:
    1. Lee el HTML temporal (ya editado por la IA)
    2. Para cada párrafo, busca su origen (data-source en <section>)
    3. Localiza el párrafo en el HTML original usando sus data-* como huella
    4. Reemplaza el contenido si cambió
    5. Reporta qué cambió y qué no
"""

import argparse
import shutil
from pathlib import Path
from bs4 import BeautifulSoup


def construir_huella(tag):
    """
    Crea una huella única para identificar un párrafo en el original.
    Usa la combinación de atributos data-* más estables + texto parcial.
    """
    partes = []
    for attr in ["data-day", "data-scene", "data-type", "data-focus", "data-speaker"]:
        v = tag.get(attr)
        if v:
            partes.append(f"{attr}={v}")
    # Texto como desempate (primeros 60 chars, sin espacios extra)
    texto = tag.get_text(strip=True)[:60]
    partes.append(f"texto={texto}")
    return "|".join(partes)


def cargar_parrafos_originales(html_path):
    """Retorna dict {huella: tag} del HTML original."""
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    mapa = {}
    for tag in soup.find_all("p", class_=["dialogo", "texto-narrativo"]):
        huella = construir_huella(tag)
        mapa[huella] = tag
    return soup, mapa


def aplicar_cambios(html_path, parrafos_nuevos, dry_run=False, backup=False):
    """
    Aplica los párrafos nuevos al HTML original.
    Retorna (cambiados, no_encontrados).
cambiados: lista de huellas que se reemplazaron.
    no_encontrados: lista de huellas que no se hallaron en el original.
    """
    soup, mapa_original = cargar_parrafos_originales(html_path)
    cambiados = []
    no_encontrados = []

    for tag_nuevo in parrafos_nuevos:
        huella = construir_huella(tag_nuevo)

        if huella not in mapa_original:
            no_encontrados.append(huella)
            continue

        tag_original = mapa_original[huella]

        # Comparar texto y atributos
        if str(tag_original) == str(tag_nuevo):
            continue  # Sin cambios

        if not dry_run:
            tag_original.replace_with(tag_nuevo)

        cambiados.append({
            "huella": huella,
            "antes": str(tag_original)[:120],
            "despues": str(tag_nuevo)[:120],
        })

    if not dry_run and cambiados:
        if backup:
            shutil.copy(html_path, str(html_path) + ".bak")
            print(f"   💾 Backup guardado: {html_path}.bak")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

    return cambiados, no_encontrados


def main():
    parser = argparse.ArgumentParser(
        description="Aplica cambios del HTML temporal a los archivos originales"
    )
    parser.add_argument(
        "--input",
        default="story_temp.html",
        help="Archivo HTML temporal editado por la IA (default: story_temp.html)",
    )
    parser.add_argument(
        "--secciones",
        default="../../secciones",
        help="Ruta a la carpeta con los HTMLs originales (default: ../../secciones)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra qué cambiaría sin modificar nada",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Guarda copia .bak de cada archivo antes de modificarlo",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    carpeta = Path(args.secciones)

    if not input_path.exists():
        print(f"❌ No se encontró el archivo: {input_path.resolve()}")
        return

    print(f"\n{'🔍 DRY RUN — ' if args.dry_run else ''}🩹 Aplicando cambios desde: {input_path.name}")
    print(f"   Secciones en: {carpeta.resolve()}\n")

    # Leer el archivo temporal
    with open(input_path, encoding="utf-8") as f:
        soup_temp = BeautifulSoup(f, "html.parser")

    # Agrupar párrafos por sección de origen
    por_seccion = {}
    for section in soup_temp.find_all("section"):
        origen = section.get("data-source")
        if not origen:
            continue
        parrafos = section.find_all("p", class_=["dialogo", "texto-narrativo"])
        if parrafos:
            por_seccion.setdefault(origen, []).extend(parrafos)

    if not por_seccion:
        print("⚠️  No se encontraron <section data-source='...'> en el archivo temporal.")
        print("   Asegúrate de usar el archivo generado por filter.py sin modificar la estructura.")
        return

    total_cambios = 0
    total_no_encontrados = 0

    for seccion, parrafos in sorted(por_seccion.items()):
        html_path = carpeta / seccion
        if not html_path.exists():
            print(f"   ⚠️  No existe: {html_path}")
            continue

        cambiados, no_encontrados = aplicar_cambios(
            html_path, parrafos, dry_run=args.dry_run, backup=args.backup
        )

        if cambiados or no_encontrados:
            print(f"  📄 {seccion}")
            for c in cambiados:
                modo = "  [DRY]" if args.dry_run else "  ✏️ "
                print(f"{modo} CAMBIADO: {c['huella'][:80]}")
                print(f"         ANTES   : {c['antes'][:100]}")
                print(f"         DESPUÉS : {c['despues'][:100]}")
            for h in no_encontrados:
                print(f"    ❓ NO ENCONTRADO: {h[:80]}")
        else:
            print(f"  ✓  {seccion} — sin cambios")

        total_cambios += len(cambiados)
        total_no_encontrados += len(no_encontrados)

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}✅ Resumen:")
    print(f"   Párrafos modificados  : {total_cambios}")
    print(f"   No encontrados        : {total_no_encontrados}")
    if args.dry_run:
        print("   (Ningún archivo fue modificado)\n")
    else:
        print()


if __name__ == "__main__":
    main()
