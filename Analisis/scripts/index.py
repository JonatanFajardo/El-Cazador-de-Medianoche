"""
index.py — Genera un índice JSON de toda la historia.
Lee todos los HTMLs en /secciones/ y extrae los data-* únicos por sección y globales.

Uso:
    python index.py
    python index.py --output mi_index.json
    python index.py --secciones ../../secciones

Salida: index.json (o el archivo indicado con --output)
"""

import json
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict

# ── Atributos que queremos indexar ──────────────────────────────────────────
ATRIBUTOS = [
    "data-speaker",
    "data-to",
    "data-focus",
    "data-type",
    "data-emotion",
    "data-plot",
    "data-location",
    "data-day",
    "data-scene",
    "data-relationship",
    "data-rel-direction",
]


def extraer_valores(soup, atributo):
    """Devuelve set de valores únicos para un atributo en un soup."""
    valores = set()
    for tag in soup.find_all(attrs={atributo: True}):
        for v in tag[atributo].split(","):
            valores.add(v.strip())
    return valores


def procesar_seccion(html_path):
    """Procesa un archivo HTML y retorna dict con datos por atributo."""
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    datos = {}
    for attr in ATRIBUTOS:
        valores = extraer_valores(soup, attr)
        if valores:
            # Ordenar días como enteros si es posible
            if attr == "data-day":
                datos[attr] = sorted(valores, key=lambda x: int(x) if x.isdigit() else x)
            elif attr == "data-scene":
                datos[attr] = sorted(valores)
            else:
                datos[attr] = sorted(valores)

    # Contar párrafos anotados
    total = len(soup.find_all("p", class_=["dialogo", "texto-narrativo"]))
    anotados = len(soup.find_all("p", attrs={"data-type": True}))
    datos["_stats"] = {
        "total_parrafos": total,
        "anotados": anotados,
        "pendientes": total - anotados,
    }

    return datos


def construir_indice(carpeta_secciones):
    carpeta = Path(carpeta_secciones)
    archivos = sorted(carpeta.glob("seccion*.html"))

    if not archivos:
        print(f"⚠️  No se encontraron archivos seccion*.html en {carpeta.resolve()}")
        return {}

    indice = {
        "global": defaultdict(set),
        "por_seccion": {},
        "_meta": {
            "total_secciones": len(archivos),
            "secciones": [f.name for f in archivos],
        },
    }

    for html in archivos:
        print(f"  → Procesando {html.name}...")
        datos = procesar_seccion(html)
        indice["por_seccion"][html.name] = datos

        # Acumular en global
        for attr, valores in datos.items():
            if attr.startswith("_"):
                continue
            if isinstance(valores, list):
                indice["global"][attr].update(valores)

    # Convertir sets a listas ordenadas
    global_limpio = {}
    for attr, valores in indice["global"].items():
        if attr == "data-day":
            global_limpio[attr] = sorted(valores, key=lambda x: int(x) if x.isdigit() else x)
        else:
            global_limpio[attr] = sorted(valores)

    indice["global"] = global_limpio
    indice["_meta"]["total_secciones"] = len(archivos)

    return indice


def main():
    parser = argparse.ArgumentParser(description="Genera índice JSON de la historia")
    parser.add_argument(
        "--secciones",
        default="../../secciones",
        help="Ruta a la carpeta con los HTMLs (default: ../../secciones)",
    )
    parser.add_argument(
        "--output",
        default="index.json",
        help="Archivo de salida (default: index.json)",
    )
    args = parser.parse_args()

    print(f"\n📖 Indexando secciones en: {Path(args.secciones).resolve()}")
    indice = construir_indice(args.secciones)

    if not indice:
        return

    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=2)

    total = indice["_meta"]["total_secciones"]
    personajes = len(indice["global"].get("data-speaker", []))
    print(f"\n✅ index.json generado")
    print(f"   Secciones procesadas : {total}")
    print(f"   Hablantes únicos     : {personajes}")
    print(f"   Días encontrados     : {indice['global'].get('data-day', [])}")
    print(f"   Guardado en          : {output_path.resolve()}\n")


if __name__ == "__main__":
    main()
