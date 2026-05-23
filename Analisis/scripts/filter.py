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

Flags especiales:
    --search "palabra" Filtra párrafos cuyo texto contenga la cadena (case-insensitive).
                       Combina con otros filtros via AND.
    --minimal          Output HTML con solo data-id + texto (sin otros atributos data-*).
                       Reduce tokens al enviar a Claude Web.
    --text             Output solo texto plano, sin ninguna etiqueta HTML.
                       Ideal para leer o compartir el contenido de la sección.
"""

import argparse
import unicodedata
from pathlib import Path
from bs4 import BeautifulSoup, Tag


def normalizar(texto):
    """Quita acentos y pasa a minúsculas para comparación tolerante."""
    return unicodedata.normalize("NFD", texto.lower()).encode("ascii", "ignore").decode("ascii")

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


def parrafo_cumple_filtros(tag, filtros_activos, texto_filtro=None):
    """Retorna True si el párrafo cumple TODOS los filtros activos."""
    for attr, valores_buscados in filtros_activos.items():
        valor_tag = tag.get(attr, "")
        # El atributo puede tener múltiples valores separados por coma
        valores_tag = {v.strip() for v in valor_tag.split(",")} if valor_tag else set()
        # Cumple si hay intersección (al menos un valor coincide)
        if not valores_tag.intersection(valores_buscados):
            return False
    if texto_filtro and normalizar(texto_filtro) not in normalizar(tag.get_text()):
        return False
    return True


def filtrar_secciones(carpeta, archivos_filtro, filtros_activos, texto_filtro=None):
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
            if parrafo_cumple_filtros(tag, filtros_activos, texto_filtro):
                h2, h3 = get_context_headers(tag)
                resultados.append((html.name, h2, h3, tag))

    return resultados


def tag_minimal(tag):
    """Devuelve el tag con solo data-id + texto, sin otros atributos data-*."""
    # Construir un <p> limpio con solo class y data-id
    clase = tag.get("class", [])
    clase_str = f' class="{" ".join(clase)}"' if clase else ""
    did = tag.get("data-id", "")
    did_str = f' data-id="{did}"' if did else ""
    texto = tag.decode_contents()
    return f"<p{clase_str}{did_str}>{texto}</p>"


def generar_texto_plano(resultados, output_path):
    """Genera un archivo de texto plano con solo el contenido de los párrafos."""
    seccion_actual = None
    lineas = []

    for seccion, h2, h3, tag in resultados:
        if seccion != seccion_actual:
            if seccion_actual is not None:
                lineas.append("")
            lineas.append(f"{'═' * 50}")
            lineas.append(f"  {seccion}")
            lineas.append(f"{'═' * 50}")
            lineas.append("")
            seccion_actual = seccion

        texto = tag.get_text(strip=True)
        if texto:
            lineas.append(texto)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))


def generar_html(resultados, filtros_activos, output_path, minimal=False):
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
        f"<!-- MODO: {'minimal' if minimal else 'completo'} -->",
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

        # Contexto h2/h3 solo en modo completo
        if not minimal:
            if h2 and h2 != h2_actual:
                lineas.append(f"  <h2>{h2}</h2>")
                h2_actual = h2
                h3_actual = None
            if h3 and h3 != h3_actual:
                lineas.append(f"  <h3>{h3}</h3>")
                h3_actual = h3

        contenido = tag_minimal(tag) if minimal else str(tag)
        lineas.append(f"  {contenido}")

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
    parser.add_argument(
        "--search",
        help="Filtrar párrafos cuyo texto contenga esta cadena (case-insensitive)",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Output HTML con solo data-id + texto, sin otros atributos. Reduce tokens para Claude Web.",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Output solo texto plano, sin etiquetas HTML. Ideal para leer o compartir.",
    )

    args = parser.parse_args()

    # Construir filtros activos
    filtros_activos = {}
    for nombre, attr in FILTROS.items():
        valor = getattr(args, nombre.replace("-", "_"), None)
        if valor:
            filtros_activos[attr] = {v.strip() for v in valor.split(",")}

    texto_filtro = args.search.lower() if args.search else None

    if not filtros_activos and not texto_filtro and not args.section:
        print("[!] Debes indicar al menos un filtro. Ejemplo: --speaker axel")
        parser.print_help()
        return

    archivos_filtro = {args.section} if args.section else None

    print(f"\n[>] Filtrando en: {Path(args.secciones).resolve()}")
    if filtros_activos:
        print(f"   Filtros: {filtros_activos}")
    if texto_filtro:
        print(f"   Búsqueda: {args.search!r}")
    if args.minimal:
        print(f"   Modo:    minimal (solo data-id + texto)")
    if args.text:
        print(f"   Modo:    texto plano (sin etiquetas)")

    resultados = filtrar_secciones(args.secciones, archivos_filtro, filtros_activos, texto_filtro)

    if not resultados:
        print("[!] No se encontraron parrafos con esos filtros.")
        return

    output_path = Path(args.output)

    if args.text:
        # Cambiar extensión a .txt si el output es el default
        if output_path.name == "story_temp.html":
            output_path = output_path.with_name("story_temp.txt")
        generar_texto_plano(resultados, output_path)
    else:
        generar_html(resultados, filtros_activos, output_path, minimal=args.minimal)

    print(f"\n[OK] {len(resultados)} parrafos encontrados")
    secciones = {r[0] for r in resultados}
    print(f"   Secciones afectadas : {sorted(secciones)}")
    print(f"   Guardado en         : {output_path.resolve()}\n")


if __name__ == "__main__":
    main()
