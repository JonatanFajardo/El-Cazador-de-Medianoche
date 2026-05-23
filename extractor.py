#!/usr/bin/env python3
"""
extractor.py — Lee todos los seccion_XX.html y genera datos_historia.json
para el dashboard de análisis narrativo.

Uso:
    python extractor.py

Requisitos:
    pip install beautifulsoup4
"""

import os
import json
import csv
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECCIONES_CONFIG = [
    {"id": "seccion_01",  "nombre": "Cap.1",  "dia": 1},
    {"id": "seccion_02",  "nombre": "Cap.2",  "dia": 2},
    {"id": "seccion_03",  "nombre": "Cap.3",  "dia": 3},
    {"id": "seccion_03B", "nombre": "Cap.3B", "dia": 4},
    {"id": "seccion_04",  "nombre": "Cap.4",  "dia": 5},
    {"id": "seccion_05",  "nombre": "Cap.5",  "dia": 6},
    {"id": "seccion_06",  "nombre": "Cap.6",  "dia": 7},
    {"id": "seccion_07",  "nombre": "Cap.7",  "dia": 7},
    {"id": "seccion_07A", "nombre": "Cap.7A", "dia": 8},
    {"id": "seccion_07B", "nombre": "Cap.7B", "dia": 8},
    {"id": "seccion_08",  "nombre": "Cap.8",  "dia": 8},
    {"id": "seccion_08A", "nombre": "Cap.8A", "dia": 9},
    {"id": "seccion_08B", "nombre": "Cap.8B", "dia": 9},
    {"id": "seccion_08C", "nombre": "Cap.8C", "dia": 9},
    {"id": "seccion_09",  "nombre": "Cap.9",  "dia": 9},
    {"id": "seccion_09A", "nombre": "Cap.9A", "dia": 10},
    {"id": "seccion_09B", "nombre": "Cap.9B", "dia": 10},
    {"id": "seccion_10",  "nombre": "Cap.10", "dia": 11},
]

COLORES_PERSONAJES = {
    "Axel":            "#e8c870",
    "Seraphina":       "#7bb87b",
    "Ember":           "#7098c8",
    "El Erizo":        "#b07850",
    "Sol":             "#e8a030",
    "Luna Suave":      "#a0b8d8",
    "Groundbreaker":   "#907060",
    "Problemas":       "#a0a0a0",
    "Eco Pergaminada": "#c090c0",
    "Sombra":          "#505878",
    "Pelaje Gris":     "#909090",
    "Susurradores":    "#7bc8c8",
    "Cuevas Brillantes": "#90c870",
    "Templo Celestial":  "#c8a060",
}

# ─── LECTURA DE CSVs ──────────────────────────────────────────────────────────

def leer_csv_calidad():
    ruta = os.path.join(BASE_DIR, "Analisis", "calidad_secciones.csv")
    datos = {}
    with open(ruta, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            datos[row["seccion"]] = {
                "rttr":        float(row["rttr"]),
                "ratio_tell":  float(row["ratio_tell"]),
                "sentimiento": float(row["sentimiento"]),
                "volatilidad": float(row["volatilidad"]),
            }
    return datos


def leer_csv_ritmo():
    ruta = os.path.join(BASE_DIR, "Analisis", "ritmo_narrativo.csv")
    datos = {}
    with open(ruta, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            datos[row["capitulo"]] = {
                "palabras":         int(row["palabras"]),
                "lectura":          row["lectura_estimada"],
                "oraciones":        int(row["oraciones"]),
                "longitud_media":   float(row["longitud_media"]),
                "densidad_dialogo": float(row["densidad_dialogo"]),
            }
    return datos


def leer_csv_presencia():
    ruta = os.path.join(BASE_DIR, "Analisis", "presencia_personajes.csv")
    with open(ruta, encoding="utf-8") as f:
        lines = f.readlines()

    reader = csv.reader(lines)
    headers = next(reader)
    # Primera columna es el nombre de sección (sin cabecera), resto son personajes
    personajes = headers[1:]

    datos = {}
    for row in reader:
        if not row:
            continue
        seccion = row[0]
        datos[seccion] = {}
        for i, p in enumerate(personajes):
            try:
                datos[seccion][p] = int(row[i + 1])
            except (ValueError, IndexError):
                datos[seccion][p] = 0
    return datos, personajes


def leer_grafo():
    ruta = os.path.join(BASE_DIR, "Analisis", "grafo_personajes.json")
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            with open(ruta, encoding=enc) as f:
                data = json.load(f)
            break
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    else:
        raise RuntimeError(f"No se pudo leer {ruta} con ningún encoding conocido")
    for nodo in data["nodos"]:
        nodo["color"] = COLORES_PERSONAJES.get(nodo["id"], "#8b949e")
    return data

# ─── ANÁLISIS DE ANOTACIONES HTML ────────────────────────────────────────────

def analizar_html(seccion_id):
    """
    Extrae todos los data-* de cada <p> anotado.
    Devuelve None si el archivo no existe.
    Devuelve métricas agregadas si existe.
    """
    ruta = os.path.join(BASE_DIR, f"{seccion_id}.html")
    if not os.path.exists(ruta):
        return None

    with open(ruta, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    parrafos = soup.find_all(
        "p",
        class_=lambda c: c and ("dialogo" in c or "texto-narrativo" in c)
    )

    total     = len(parrafos)
    anotados  = sum(1 for p in parrafos if p.get("data-type"))
    cobertura = round(anotados / total * 100, 1) if total > 0 else 0.0

    por_tipo     = defaultdict(int)
    por_emocion  = defaultdict(int)
    por_plot     = defaultdict(int)
    tensiones    = []
    intensidades = []
    dialogos_por_speaker  = defaultdict(int)
    narracion_por_focus   = defaultdict(int)
    palabras_por_location = defaultdict(int)
    relaciones_raw        = defaultdict(lambda: defaultdict(int))
    secretos   = 0
    revelaciones = []
    escenas    = set()

    for p in parrafos:
        texto     = p.get_text(strip=True)
        n_palabras = len(texto.split())

        tipo = p.get("data-type", "")
        if tipo:
            por_tipo[tipo] += 1

        emocion = p.get("data-emotion", "")
        if emocion:
            por_emocion[emocion] += 1

        try:
            tensiones.append(int(p.get("data-tension", "")))
        except ValueError:
            pass

        try:
            intensidades.append(int(p.get("data-intensity", "")))
        except ValueError:
            pass

        plot = p.get("data-plot", "")
        if plot:
            por_plot[plot] += 1

        speaker = p.get("data-speaker", "")
        if speaker:
            dialogos_por_speaker[speaker] += 1

        focus = p.get("data-focus", "")
        if focus and focus != "ambiente":
            for f in focus.split(","):
                narracion_por_focus[f.strip()] += 1

        escena = p.get("data-scene", "")
        if escena:
            escenas.add(escena)

        location = p.get("data-location", "")
        if location:
            palabras_por_location[location] += n_palabras

        rel = p.get("data-relationship", "")
        if rel:
            direccion = p.get("data-rel-direction", "neutral")
            relaciones_raw[rel][direccion] += 1

        if p.get("data-secret") == "true":
            secretos += 1

        rev = p.get("data-reveals", "")
        if rev:
            revelaciones.append(rev)

    return {
        "total_parrafos":   total,
        "anotados":         anotados,
        "cobertura_pct":    cobertura,
        "por_tipo":         dict(por_tipo),
        "por_emocion":      dict(por_emocion),
        "por_plot":         dict(por_plot),
        "tension_media":    round(sum(tensiones) / len(tensiones), 2) if tensiones else None,
        "intensidad_media": round(sum(intensidades) / len(intensidades), 2) if intensidades else None,
        "dialogos_por_speaker":  dict(dialogos_por_speaker),
        "narracion_por_focus":   dict(narracion_por_focus),
        "num_escenas":           len(escenas),
        "palabras_por_location": dict(palabras_por_location),
        "relaciones":            {k: dict(v) for k, v in relaciones_raw.items()},
        "secretos_activos":      secretos,
        "revelaciones":          revelaciones,
    }

# ─── CONSTRUCCIÓN DEL JSON ────────────────────────────────────────────────────

def construir_json():
    print("📖 Leyendo CSVs...")
    calidad              = leer_csv_calidad()
    ritmo                = leer_csv_ritmo()
    presencia_raw, lista_personajes = leer_csv_presencia()
    grafo                = leer_grafo()

    secciones_out        = []
    palabras_por_dia     = defaultdict(int)
    todas_locations      = defaultdict(int)
    secretos_serie       = []
    revelaciones_serie   = []

    print(f"📂 Procesando {len(SECCIONES_CONFIG)} secciones...")

    for cfg in SECCIONES_CONFIG:
        sid = cfg["id"]
        print(f"   → {sid}", end="")

        cal  = calidad.get(sid, {})
        rit  = ritmo.get(sid, {})
        html = analizar_html(sid)

        estado = f"  ({'anotado' if html and html['anotados'] > 0 else 'sin anotar'})"
        print(estado)

        sec = {
            "id":     sid,
            "nombre": cfg["nombre"],
            "dia":    cfg["dia"],
            # Métricas de CSV (siempre disponibles)
            "rttr":             cal.get("rttr"),
            "ratio_tell":       cal.get("ratio_tell"),
            "sentimiento":      cal.get("sentimiento"),
            "volatilidad":      cal.get("volatilidad"),
            "palabras":         rit.get("palabras"),
            "lectura":          rit.get("lectura"),
            "oraciones":        rit.get("oraciones"),
            "longitud_media":   rit.get("longitud_media"),
            "densidad_dialogo": rit.get("densidad_dialogo"),
            # Métricas de anotaciones (disponibles tras anotar)
            "anotado":          bool(html and html["anotados"] > 0),
            "cobertura_pct":    html["cobertura_pct"] if html else 0,
            "total_parrafos":   html["total_parrafos"] if html else None,
            "por_tipo":         html["por_tipo"] if html else {},
            "por_emocion":      html["por_emocion"] if html else {},
            "por_plot":         html["por_plot"] if html else {},
            "tension_media":    html["tension_media"] if html else None,
            "intensidad_media": html["intensidad_media"] if html else None,
            "dialogos_por_speaker":  html["dialogos_por_speaker"] if html else {},
            "narracion_por_focus":   html["narracion_por_focus"] if html else {},
            "num_escenas":           html["num_escenas"] if html else None,
            "palabras_por_location": html["palabras_por_location"] if html else {},
            "relaciones":            html["relaciones"] if html else {},
            "secretos_activos":      html["secretos_activos"] if html else 0,
            "revelaciones":          html["revelaciones"] if html else [],
        }
        secciones_out.append(sec)

        # Acumulados globales
        palabras_por_dia[cfg["dia"]] += rit.get("palabras", 0)
        secretos_serie.append(sec["secretos_activos"])
        revelaciones_serie.append(len(sec["revelaciones"]))
        for loc, w in sec["palabras_por_location"].items():
            todas_locations[loc] += w

    # Presencia de personajes por sección (alineada al orden canónico)
    sids_orden = [c["id"] for c in SECCIONES_CONFIG]
    presencia_out = {}
    for p in lista_personajes:
        vals = [presencia_raw.get(sid, {}).get(p, 0) for sid in sids_orden]
        if any(v > 0 for v in vals):
            presencia_out[p] = vals

    # Revelaciones acumuladas
    rev_acum = []
    acum = 0
    for r in revelaciones_serie:
        acum += r
        rev_acum.append(acum)

    # Palabras por día
    dias = sorted(palabras_por_dia.keys())
    palabras_dia_out = {
        "labels": [f"Día {d}" for d in dias],
        "vals":   [palabras_por_dia[d] for d in dias],
    }

    # Anotadas
    n_anotadas = sum(1 for s in secciones_out if s["anotado"])

    output = {
        "generado": datetime.now().isoformat(),
        "resumen": {
            "total_secciones":    len(secciones_out),
            "total_palabras":     sum(s["palabras"] or 0 for s in secciones_out),
            "secciones_anotadas": n_anotadas,
            "pct_anotado":        round(n_anotadas / len(secciones_out) * 100, 1),
        },
        "labels":               [c["nombre"] for c in SECCIONES_CONFIG],
        "secciones":            secciones_out,
        "presencia_personajes": presencia_out,
        "grafo_personajes":     grafo,
        "palabras_por_dia":     palabras_dia_out,
        "misterio": {
            "secretos_activos":  secretos_serie,
            "revelaciones_acum": rev_acum,
        },
        "lugares": dict(todas_locations),
    }

    salida = os.path.join(BASE_DIR, "datos_historia.json")
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅  datos_historia.json generado")
    print(f"    Secciones:  {output['resumen']['total_secciones']}")
    print(f"    Palabras:   {output['resumen']['total_palabras']:,}")
    print(f"    Anotadas:   {n_anotadas}/{len(secciones_out)}  ({output['resumen']['pct_anotado']}%)")
    if todas_locations:
        print(f"    Ubicaciones detectadas: {len(todas_locations)}")


if __name__ == "__main__":
    construir_json()
