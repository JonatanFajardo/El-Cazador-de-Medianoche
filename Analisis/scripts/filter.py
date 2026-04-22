"""
filter.py — Filtra párrafos por data-* y genera un HTML temporal para la IA.
Incluye contexto h2/h3 de cada párrafo para que la IA entienda dónde está.

Uso básico:
    python filter.py --speaker axel
    python filter.py --speaker axel --day 3
    python filter.py --emotion ira --tension 4
    python filter.py --speaker axel --to seraphina --day 3 --output contexto.html
    python filter.py --location montanas-heladas --type dialogo
    python filter.py --relationship axel-seraphina
    python filter.py --plot revelacion --section seccion_02.html

Múltiples valores (OR dentro del mismo filtro):
    python filter.py --speaker axel,seraphina
    python filter.py --emotion miedo,ira

Todos los filtros se combinan con AND entre ellos.
"""

import argparse
from pathlib import Path
from bs4 import BeautifulSoup, Tag

# ── Filtros disponibles y su atributo HTML correspondiente ──────────────────
FILTROS = {
    "speaker":       "data-speaker",
    "to":            "data-to",
    "focus":         "data-focus",
    "type":          "data-type",
    "emotion":       "data-emotion",
    "intensity":     "data-intensity",
    "tension":       "data-tension",
    "plot":          "data-plot",
    "location":      "data-location",
    "day":           "data-day",
    "scene":         "data-scene",
    "relationship":  "data-relationship",
    "rel_direction": "data-rel-direction",
    "secret":        "data-secret",
}


def get_context_headers(tag):
    """Sube en el DOM para encontrar el h2 y h3 más cercanos antes del párrafo."""
    h2, h3 = None, None
    for sibling in tag.find_all_previous():
        if sibling.name == "h3" and h3 is None:
            h3 = sibling.get_text(strip=True)
        if sibling.name == "h2" and h2 is None:
            h2 = sibling.get_text(strip=True)
        if h2 and h3:
            break
    return h2, h3


def parrafo_cumple_filtros(tag, filtros_activos):
    """Retorna True si el párrafo cumple TODOS los filtros activos."""
    for attr, valores_buscados in filtros_activos.items():
        valor_tag = tag.get(attr, "")
        # El atributo puede tener múltiples valores separados por coma
        valores_tag = {v.strip() for v in valor_tag.split(",")} if valor_tag else set()
        # Cumple si hay intersección (al menos un valor coincide)
        if not valores_tag.intersection(valores_buscados):
            return False
    return True


def filtrar_secciones(carpeta, archivos_filtro, filtros_activos):
    """Recorre los HTMLs y devuelve lista de (seccion, h2, h3, tag)."""
    resultados = []
    carpeta = Path(carpeta)
    archivos = sorted(carpeta.glob("seccion*.html"))

    if archivos_filtro:
        archivos = [a for a in archivos if a.name in archivos_filtro]

    for html in archivos:
        with open(html, encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        for tag in soup.find_all("p", class_=["dialogo", "texto-narrativo"]):
            if parrafo_cumple_filtros(tag, filtros_activos):
                h2, h3 = get_context_headers(tag)
                resultados.append((html.name, h2, h3, tag))

    return resultados


def generar_html(resultados, filtros_activos, output_path):
    """Genera el HTML temporal agrupado por sección para la IA."""
    resumen_filtros = ", ".join(
        f'{k}="{",".join(sorted(v))}"' for k, v in filtros_activos.items()
    )

    lineas = [
        "<!DOCTYPE html>",
        "<html lang='es'>",
        "<head><meta charset='UTF-8'>",
        f"<title>Fragmentos filtrados — {resumen_filtros}</title>",
        "</head><body>",
        f"<!-- FILTROS APLICADOS: {resumen_filtros} -->",
        f"<!-- TOTAL PÁRRAFOS: {len(resultados)} -->",
        "",
    ]

    seccion_actual = None
    h2_actual = None
    h3_actual = None

    for seccion, h2, h3, tag in resultados:
        # Separador de sección
        if seccion != seccion_actual:
            if seccion_actual is not None:
                lineas.append("</section>")
            lineas.append(f"\n<!-- ══════════ {seccion} ══════════ -->")
            lineas.append(f"<section data-source='{seccion}'>")
            seccion_actual = seccion
            h2_actual = None
            h3_actual = None

        # Contexto h2
        if h2 and h2 != h2_actual:
            lineas.append(f"  <h2>{h2}</h2>")
            h2_actual = h2
            h3_actual = None

        # Contexto h3
        if h3 and h3 != h3_actual:
            lineas.append(f"  <h3>{h3}</h3>")
            h3_actual = h3

        lineas.append(f"  {str(tag)}")

    if seccion_actual:
        lineas.append("</section>")

    lineas.extend(["", "</body></html>"])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))


def main():
    parser = argparse.ArgumentParser(
        description="Filtra párrafos de la historia por data-* y genera HTML para IA"
    )

    # Filtros
    for nombre in FILTROS:
        parser.add_argument(f"--{nombre}", help=f"Filtrar por {nombre} (varios: a,b,c)")

    # Opciones
    parser.add_argument(
        "--secciones",
        default="../../secciones",
        help="Ruta a la carpeta con los HTMLs (default: ../../secciones)",
    )
    parser.add_argument(
        "--section",
        help="Limitar a una sección específica, ej: seccion_02.html",
    )
    parser.add_argument(
        "--output",
        default="story_temp.html",
        help="Archivo de salida (default: story_temp.html)",
    )

    args = parser.parse_args()

    # Construir filtros activos
    filtros_activos = {}
    for nombre, attr in FILTROS.items():
        valor = getattr(args, nombre.replace("-", "_"), None)
        if valor:
            filtros_activos[attr] = {v.strip() for v in valor.split(",")}

    if not filtros_activos:
        print("⚠️  Debes indicar al menos un filtro. Ejemplo: --speaker axel")
        parser.print_help()
        return

    archivos_filtro = {args.section} if args.section else None

    print(f"\n🔍 Filtrando en: {Path(args.secciones).resolve()}")
    print(f"   Filtros: {filtros_activos}")

    resultados = filtrar_secciones(args.secciones, archivos_filtro, filtros_activos)

    if not resultados:
        print("⚠️  No se encontraron párrafos con esos filtros.")
        return

    output_path = Path(args.output)
    generar_html(resultados, filtros_activos, output_path)

    print(f"\n✅ {len(resultados)} párrafos encontrados")
    secciones = {r[0] for r in resultados}
    print(f"   Secciones afectadas : {sorted(secciones)}")
    print(f"   Guardado en         : {output_path.resolve()}\n")


if __name__ == "__main__":
    main()
