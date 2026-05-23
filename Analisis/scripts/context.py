"""
context.py — Extrae pilares narrativos de la historia para consulta de solo lectura.
Salida en markdown limpio, sin data-id, sin HTML. NO compatible con patch.py (intencional).

Uso:
    python context.py                          # pilares de todas las secciones
    python context.py --section seccion_01     # solo una sección
    python context.py --tipo cronologia        # solo hechos temporales
    python context.py --tipo reveals           # solo hechos que la historia establece
    python context.py --tipo foreshadowing     # solo promesas a futuro
    python context.py --tipo todo              # todo combinado (default)
    python context.py --personaje axel         # pilares donde axel es foco
    python context.py --output pilares.md      # guardar en archivo (default: imprime en pantalla)

Tipos disponibles:
    todo          — todo combinado
    reveals       — párrafos con data-reveals (hechos que la historia establece)
    foreshadowing — párrafos con data-plot=foreshadowing
    revelacion    — párrafos con data-plot=revelacion (giros de trama)
    cronologia    — párrafos con menciones temporales (años, semanas, días, meses)
    secretos      — párrafos con data-secret=true (engaños o info oculta al lector)
    climax        — párrafos con data-plot=climax o data-plot=gancho
"""

import argparse
import re
from pathlib import Path
from bs4 import BeautifulSoup

SECCIONES_DIR = Path(__file__).parent.parent.parent / "secciones"

# Palabras que indican referencias temporales
PATRON_TEMPORAL = re.compile(
    r"\b(\d+\s*(año|años|semana|semanas|mes|meses|día|días|hora|horas)|"
    r"hace\s+\w+|desde\s+que|tres\s+años|cinco\s+años|hace\s+poco|"
    r"desde\s+entonces|antes\s+de|tiempo\s+atrás)\b",
    re.IGNORECASE
)


def get_section_label(filename):
    """Convierte seccion_01.html → Sección 01"""
    stem = Path(filename).stem  # seccion_01
    parts = stem.split("_")
    if len(parts) >= 2:
        return f"Sección {parts[1].upper()}"
    return filename


def get_context_header(tag):
    """Encuentra el h3 más cercano antes del párrafo."""
    for sibling in tag.find_all_previous():
        if sibling.name == "h3":
            return sibling.get_text(strip=True)
    return None


def texto_limpio(tag):
    """Extrae texto plano del tag, sin HTML."""
    return tag.get_text(separator=" ", strip=True)


def extraer_pilares(html_path, tipo, personaje_filtro):
    """Lee un HTML y devuelve lista de (escena, tipo_pilar, reveals_attr, texto)."""
    pilares = []

    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for tag in soup.find_all("p", class_=["dialogo", "texto-narrativo"]):
        texto = texto_limpio(tag)
        if not texto:
            continue

        # Filtro de personaje (data-focus)
        if personaje_filtro:
            focus = tag.get("data-focus", "")
            if personaje_filtro not in focus.lower():
                continue

        plot = tag.get("data-plot", "")
        reveals = tag.get("data-reveals", "")
        secret = tag.get("data-secret", "")
        escena = get_context_header(tag) or "—"
        dia = tag.get("data-day", "?")

        incluir = False
        etiqueta = ""

        if tipo in ("todo", "reveals") and reveals:
            incluir = True
            etiqueta = "ESTABLECE"

        if tipo in ("todo", "foreshadowing") and plot == "foreshadowing":
            if not incluir:
                incluir = True
                etiqueta = "FORESHADOW"

        if tipo in ("todo", "revelacion") and plot == "revelacion":
            if not incluir:
                incluir = True
                etiqueta = "REVELACIÓN"

        if tipo in ("todo", "secretos") and secret == "true":
            if not incluir:
                incluir = True
                etiqueta = "SECRETO"

        if tipo in ("todo", "climax") and plot in ("climax", "gancho"):
            if not incluir:
                incluir = True
                etiqueta = plot.upper()

        if tipo == "cronologia" and PATRON_TEMPORAL.search(texto):
            incluir = True
            etiqueta = "TIEMPO"

        if incluir:
            pilares.append({
                "dia": dia,
                "escena": escena,
                "etiqueta": etiqueta,
                "reveals": reveals,
                "texto": texto,
            })

    return pilares


def formatear_markdown(seccion_nombre, pilares):
    """Convierte lista de pilares en markdown legible."""
    if not pilares:
        return ""

    lineas = [f"\n## {seccion_nombre}\n"]
    escena_actual = None

    for p in pilares:
        if p["escena"] != escena_actual:
            lineas.append(f"\n### {p['escena']} (Día {p['dia']})\n")
            escena_actual = p["escena"]

        etiqueta = f"**[{p['etiqueta']}]**"
        if p["reveals"]:
            lineas.append(f"{etiqueta} _{p['reveals']}_")
            lineas.append(f"> {p['texto']}\n")
        else:
            lineas.append(f"{etiqueta}")
            lineas.append(f"> {p['texto']}\n")

    return "\n".join(lineas)


def main():
    parser = argparse.ArgumentParser(
        description="Extrae pilares narrativos para consulta (solo lectura, sin data-id)"
    )
    parser.add_argument(
        "--section",
        help="Limitar a una sección, ej: seccion_01 o seccion_01.html",
    )
    parser.add_argument(
        "--tipo",
        default="todo",
        choices=["todo", "reveals", "foreshadowing", "revelacion", "cronologia", "secretos", "climax"],
        help="Qué tipo de pilares extraer (default: todo)",
    )
    parser.add_argument(
        "--personaje",
        help="Filtrar por personaje en data-focus, ej: axel, seraphina",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Guardar resultado en archivo .md (default: imprime en pantalla)",
    )
    parser.add_argument(
        "--secciones",
        default=str(SECCIONES_DIR),
        help="Ruta a la carpeta con los HTMLs",
    )

    args = parser.parse_args()

    carpeta = Path(args.secciones)
    if not carpeta.exists():
        print(f"❌ No se encuentra la carpeta: {carpeta}")
        return

    # Determinar qué archivos procesar
    archivos = sorted(carpeta.glob("seccion*.html"))
    if args.section:
        nombre = args.section if args.section.endswith(".html") else args.section + ".html"
        archivos = [a for a in archivos if a.name == nombre]
        if not archivos:
            print(f"❌ No se encontró: {nombre}")
            return

    personaje = args.personaje.lower() if args.personaje else None

    print(f"\n📖 Extrayendo pilares [{args.tipo}]", end="")
    if personaje:
        print(f" | personaje: {personaje}", end="")
    if args.section:
        print(f" | sección: {args.section}", end="")
    print(f"\n   Fuente: {carpeta.resolve()}\n")

    salida_total = ["# Pilares Narrativos — El Cazador de Medianoche"]
    salida_total.append(f"_Tipo: {args.tipo}" + (f" | Personaje: {personaje}" if personaje else "") + "_\n")
    salida_total.append("---")

    total_pilares = 0

    for html in archivos:
        pilares = extraer_pilares(html, args.tipo, personaje)
        if pilares:
            total_pilares += len(pilares)
            bloque = formatear_markdown(get_section_label(html.name), pilares)
            salida_total.append(bloque)

    salida_total.append(f"\n---\n_Total: {total_pilares} pilares encontrados en {len(archivos)} sección(es)_")
    resultado = "\n".join(salida_total)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(resultado, encoding="utf-8")
        print(f"✅ {total_pilares} pilares → guardados en {out_path.resolve()}")
    else:
        print(resultado)
        print(f"\n✅ {total_pilares} pilares encontrados")


if __name__ == "__main__":
    main()
