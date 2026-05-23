"""
query_index.py — Consulta rápida del index.json de anotaciones narrativas.

═══════════════════════════════════════════════════════════════
USO BÁSICO
═══════════════════════════════════════════════════════════════
  python query_index.py                            → tabla resumen de todas las secciones
  python query_index.py --seccion seccion_08       → detalles de esa sección
  python query_index.py --pendientes               → secciones con párrafos sin anotar
  python query_index.py --exportar                 → genera index_compact.md

═══════════════════════════════════════════════════════════════
BÚSQUEDA
═══════════════════════════════════════════════════════════════
  python query_index.py --buscar umbra             → en qué secciones aparece "umbra"
  python query_index.py --buscar umbra axel        → AND: ambos deben aparecer
  python query_index.py --buscar-o umbra axel      → OR: cualquiera de los dos
  python query_index.py --sin-campo data-relationship → secciones que NO tienen ese campo

═══════════════════════════════════════════════════════════════
PERSONAJES Y RELACIONES
═══════════════════════════════════════════════════════════════
  python query_index.py --personaje axel           → arco completo de un personaje
  python query_index.py --relacion axel-seraphina  → evolución de la relación sección a sección

═══════════════════════════════════════════════════════════════
NAVEGACIÓN Y CONTINUIDAD
═══════════════════════════════════════════════════════════════
  python query_index.py --contexto seccion_08      → sección anterior + actual + siguiente
  python query_index.py --timeline                 → mapa de los 11 días con sus secciones
  python query_index.py --plot climax              → dónde están distribuidos los climax
  python query_index.py --location valle-mariposas → qué secciones ocurren en ese lugar

═══════════════════════════════════════════════════════════════
PARA LA IA (máximo ahorro de tokens)
═══════════════════════════════════════════════════════════════
  python query_index.py --prompt seccion_08        → bloque listo para pegar en el prompt
"""

import json
import argparse
import sys
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

# Ruta al index.json (se busca en la misma carpeta que este script)
RUTA_INDEX = Path(__file__).parent / "index.json"


# ─────────────────────────────────────────────
# UTILIDADES INTERNAS
# ─────────────────────────────────────────────

def cargar_index():
    """Lee el archivo index.json y lo devuelve como diccionario."""
    if not RUTA_INDEX.exists():
        print(f"[ERROR] No se encontró index.json en: {RUTA_INDEX}")
        sys.exit(1)
    with open(RUTA_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)


def normalizar_seccion(nombre):
    """Acepta 'seccion_08', '08', 'seccion_08.html' → devuelve 'seccion_08.html'."""
    nombre = nombre.strip()
    if nombre.isdigit():
        nombre = f"seccion_{nombre.zfill(2)}"
    if not nombre.endswith(".html"):
        nombre += ".html"
    return nombre


def obtener_orden(datos):
    """Devuelve la lista ordenada de secciones según _meta."""
    return datos.get("_meta", {}).get("secciones",
           list(datos.get("por_seccion", {}).keys()))


def rango_dias(info):
    """Devuelve string '3-5' o '4' con el rango de días de una sección."""
    dias = info.get("data-day", [])
    if not dias:
        return "?"
    return f"{dias[0]}-{dias[-1]}" if len(dias) > 1 else dias[0]


def validar_seccion(secciones, nombre):
    """Termina el programa con mensaje útil si la sección no existe."""
    if nombre not in secciones:
        print(f"[ERROR] Sección no encontrada: '{nombre}'")
        print("Disponibles:", ", ".join(secciones.keys()))
        sys.exit(1)


# ─────────────────────────────────────────────
# BÁSICOS
# ─────────────────────────────────────────────

def mostrar_resumen(datos):
    """Tabla corta: todas las secciones con párrafos, anotados, pendientes y días."""
    secciones = datos.get("por_seccion", {})
    orden = obtener_orden(datos)

    print(f"\n{'SECCIÓN':<22} {'PÁRR':>5} {'ANOT':>5} {'PEND':>5}  DÍAS")
    print("-" * 55)

    for nombre in orden:
        info  = secciones.get(nombre, {})
        stats = info.get("_stats", {})
        total = stats.get("total_parrafos", "?")
        anot  = stats.get("anotados", "?")
        pend  = stats.get("pendientes", "?")
        alerta = " [!]" if isinstance(pend, int) and pend > 0 else ""
        print(f"{nombre:<22} {total:>5} {anot:>5} {pend:>5}  dia {rango_dias(info)}{alerta}")
    print()


def mostrar_seccion(datos, nombre_raw):
    """Detalle completo de una sección, formateado en líneas cortas."""
    secciones = datos.get("por_seccion", {})
    nombre = normalizar_seccion(nombre_raw)
    validar_seccion(secciones, nombre)

    info  = secciones[nombre]
    stats = info.get("_stats", {})

    print(f"\n-- {nombre} --")
    print(f"Parrafos : {stats.get('total_parrafos','?')} total | "
          f"{stats.get('anotados','?')} anotados | "
          f"{stats.get('pendientes','?')} pendientes")

    campos = [
        ("data-day",          "Dias"),
        ("data-scene",        "Escenas"),
        ("data-location",     "Locations"),
        ("data-speaker",      "Speakers"),
        ("data-to",           "To"),
        ("data-focus",        "Focus"),
        ("data-type",         "Tipos"),
        ("data-emotion",      "Emociones"),
        ("data-plot",         "Plot"),
        ("data-relationship", "Relaciones"),
        ("data-rel-direction","Rel-dir"),
    ]

    for clave, etiqueta in campos:
        valores = info.get(clave)
        if valores:
            print(f"{etiqueta:<12}: {', '.join(valores)}")
    print()


def mostrar_pendientes(datos):
    """Lista secciones con párrafos sin anotar."""
    secciones = datos.get("por_seccion", {})
    hay = False

    print("\nSecciones con parrafos PENDIENTES:")
    print("-" * 40)
    for nombre, info in secciones.items():
        pend = info.get("_stats", {}).get("pendientes", 0)
        if isinstance(pend, int) and pend > 0:
            total = info.get("_stats", {}).get("total_parrafos", "?")
            print(f"  {nombre:<25} {pend}/{total} pendientes")
            hay = True
    if not hay:
        print("  Todo anotado.")
    print()


def exportar_compact(datos):
    """Genera index_compact.md (~100 líneas) para orientación rápida de la IA."""
    secciones = datos.get("por_seccion", {})
    orden     = obtener_orden(datos)
    destino   = Path(__file__).parent.parent / "index_compact.md"

    lineas = ["# index_compact -- resumen de secciones\n",
              "_Generado automaticamente por query_index.py_\n\n"]

    for nombre in orden:
        info  = secciones.get(nombre, {})
        stats = info.get("_stats", {})
        lineas.append(f"## {nombre}  "
                      f"(parrafos: {stats.get('total_parrafos','?')} | "
                      f"pendientes: {stats.get('pendientes','?')} | "
                      f"dias: {rango_dias(info)})\n")

        for clave in ["data-speaker", "data-focus", "data-location", "data-emotion"]:
            vals = info.get(clave)
            if vals:
                lineas.append(f"- **{clave}**: {', '.join(vals)}\n")
        lineas.append("\n")

    with open(destino, "w", encoding="utf-8") as f:
        f.writelines(lineas)
    print(f"\nExportado: {destino}\n")


# ─────────────────────────────────────────────
# BÚSQUEDA
# ─────────────────────────────────────────────

def buscar_terminos(datos, terminos, modo_or=False):
    """
    Busca uno o varios términos en todos los campos de todas las secciones.
    modo_or=False → AND (todos deben aparecer en la misma sección)
    modo_or=True  → OR (basta con que uno aparezca)
    """
    terminos_lower = [t.lower() for t in terminos]
    secciones = datos.get("por_seccion", {})
    resultados = {}

    for nombre, info in secciones.items():
        # Para cada término registramos en qué campos apareció
        hits_por_termino = {}

        for clave, valores in info.items():
            if not isinstance(valores, list):
                continue
            for t in terminos_lower:
                for v in valores:
                    if t in str(v).lower():
                        hits_por_termino.setdefault(t, []).append(clave)
                        break  # no repetir el mismo campo para el mismo término

        # Aplicar lógica AND / OR
        if modo_or:
            cumple = len(hits_por_termino) > 0
        else:
            cumple = all(t in hits_por_termino for t in terminos_lower)

        if cumple:
            resultados[nombre] = hits_por_termino

    modo_txt = "OR" if modo_or else "AND"
    print(f"\nBusqueda {modo_txt}: {' | '.join(terminos)}")
    print("-" * 50)

    if not resultados:
        print("  (sin resultados)\n")
        return

    for nombre, hits in resultados.items():
        detalle = "  |  ".join(
            f"{t} -> {', '.join(campos)}" for t, campos in hits.items()
        )
        print(f"  {nombre:<25} {detalle}")
    print()


def sin_campo(datos, campo):
    """Lista secciones que NO tienen un campo data-* específico (o está vacío)."""
    secciones = datos.get("por_seccion", {})
    faltantes = []

    for nombre, info in secciones.items():
        vals = info.get(campo)
        if not vals:  # None o lista vacía
            faltantes.append(nombre)

    print(f"\nSecciones SIN campo '{campo}':")
    print("-" * 40)
    if faltantes:
        for nombre in faltantes:
            print(f"  {nombre}")
    else:
        print("  Todas lo tienen.")
    print()


# ─────────────────────────────────────────────
# PERSONAJES Y RELACIONES
# ─────────────────────────────────────────────

def mostrar_personaje(datos, personaje):
    """
    Arco completo de un personaje: en qué secciones aparece,
    en qué rol (speaker / focus / to / relaciones) y qué emociones hay.
    """
    personaje_lower = personaje.lower()
    secciones = datos.get("por_seccion", {})
    orden     = obtener_orden(datos)

    print(f"\nArco de personaje: {personaje}")
    print("-" * 70)
    print(f"{'SECCION':<22} {'ROL':<30} {'DIAS':<6} EMOCIONES")
    print("-" * 70)

    aparece = False
    for nombre in orden:
        info = secciones.get(nombre, {})
        roles = []

        if personaje_lower in [v.lower() for v in info.get("data-speaker", [])]:
            roles.append("speaker")
        if personaje_lower in [v.lower() for v in info.get("data-focus", [])]:
            roles.append("focus")
        if personaje_lower in [v.lower() for v in info.get("data-to", [])]:
            roles.append("to")

        # Relaciones donde participa este personaje
        rels = [r for r in info.get("data-relationship", [])
                if personaje_lower in r.lower()]
        for r in rels:
            roles.append(f"rel:{r}")

        if not roles:
            continue

        aparece = True
        emociones = ", ".join(info.get("data-emotion", []))
        roles_str = ", ".join(roles)
        print(f"  {nombre:<20} {roles_str:<30} {rango_dias(info):<6} {emociones}")

    if not aparece:
        print(f"  ('{personaje}' no encontrado en ninguna seccion)")
    print()


def mostrar_relacion(datos, relacion):
    """
    Evolución de una relación específica sección por sección:
    en qué secciones aparece y la dirección (positiva/tensa/negativa/neutral).
    """
    relacion_lower = relacion.lower()
    secciones = datos.get("por_seccion", {})
    orden     = obtener_orden(datos)

    print(f"\nEvolucion de relacion: {relacion}")
    print("-" * 55)
    print(f"{'SECCION':<22} {'DIRECCION':<20} DIAS")
    print("-" * 55)

    aparece = False
    for nombre in orden:
        info = secciones.get(nombre, {})
        rels = [r.lower() for r in info.get("data-relationship", [])]

        if relacion_lower not in rels:
            continue

        aparece = True
        direcciones = ", ".join(info.get("data-rel-direction", ["?"]))
        print(f"  {nombre:<20} {direcciones:<20} dia {rango_dias(info)}")

    if not aparece:
        print(f"  (relacion '{relacion}' no encontrada)")
        # Sugerir relaciones parecidas desde el global
        todas = datos.get("global", {}).get("data-relationship", [])
        # Buscar relaciones que compartan alguno de los nombres del par
        partes = relacion_lower.split("-")
        parecidas = [r for r in todas if any(p in r for p in partes)]
        if parecidas:
            print(f"  Relaciones similares: {', '.join(parecidas)}")
    print()


# ─────────────────────────────────────────────
# NAVEGACIÓN Y CONTINUIDAD
# ─────────────────────────────────────────────

def mostrar_contexto(datos, nombre_raw):
    """
    Muestra la sección anterior, la actual y la siguiente.
    Ideal para no perder el hilo narrativo al escribir.
    """
    secciones = datos.get("por_seccion", {})
    orden     = obtener_orden(datos)
    nombre    = normalizar_seccion(nombre_raw)
    validar_seccion(secciones, nombre)

    idx = orden.index(nombre)

    # Construir lista con rol + nombre de cada sección del grupo
    grupo = []
    if idx > 0:
        grupo.append(("ANTERIOR", orden[idx - 1]))
    grupo.append(("ACTUAL", nombre))
    if idx < len(orden) - 1:
        grupo.append(("SIGUIENTE", orden[idx + 1]))

    print(f"\nContexto narrativo alrededor de {nombre}")
    print("=" * 60)

    for rol, sec in grupo:
        info  = secciones.get(sec, {})
        stats = info.get("_stats", {})
        print(f"\n[{rol}] {sec}  --  dia {rango_dias(info)}  "
              f"({stats.get('total_parrafos','?')} parrafos)")
        print("-" * 50)

        campos_cortos = [
            ("data-location",     "Locations"),
            ("data-speaker",      "Speakers"),
            ("data-focus",        "Focus"),
            ("data-plot",         "Plot"),
            ("data-emotion",      "Emociones"),
            ("data-relationship", "Relaciones"),
        ]
        for clave, etiqueta in campos_cortos:
            valores = info.get(clave)
            if valores:
                print(f"  {etiqueta:<12}: {', '.join(valores)}")
    print()


def mostrar_timeline(datos):
    """
    Mapa de los 11 días de la historia.
    Para cada día muestra qué secciones ocurren en él.
    """
    secciones = datos.get("por_seccion", {})
    orden     = obtener_orden(datos)

    # Construir { dia: [secciones] }
    por_dia = {}
    for nombre in orden:
        info = secciones.get(nombre, {})
        for dia in info.get("data-day", []):
            por_dia.setdefault(dia, []).append(nombre)

    print("\nTIMELINE -- distribucion por dias")
    print("-" * 60)

    for dia in sorted(por_dia.keys(), key=lambda d: int(d)):
        secs = por_dia[dia]
        print(f"  Dia {dia:>2} | {', '.join(secs)}")
    print()


def mostrar_plot(datos, tipo_plot):
    """
    Muestra en qué secciones aparece un tipo de plot específico
    (climax, foreshadowing, revelacion, etc.) con su distribución.
    """
    tipo_lower = tipo_plot.lower()
    secciones  = datos.get("por_seccion", {})
    orden      = obtener_orden(datos)

    # Verificar que el tipo existe en el global
    plots_globales = datos.get("global", {}).get("data-plot", [])
    if tipo_lower not in [p.lower() for p in plots_globales]:
        parecidos = [p for p in plots_globales if tipo_lower in p.lower()]
        print(f"\n[AVISO] '{tipo_plot}' no es un tipo de plot reconocido.")
        if parecidos:
            print(f"  Similares: {', '.join(parecidos)}")
        else:
            print(f"  Tipos disponibles: {', '.join(plots_globales)}")
        print()
        return

    print(f"\nDistribucion de plot '{tipo_plot}':")
    print("-" * 50)

    encontrado = False
    for nombre in orden:
        info  = secciones.get(nombre, {})
        plots = [p.lower() for p in info.get("data-plot", [])]
        if tipo_lower not in plots:
            continue
        encontrado = True
        # Mostrar otros plots de esa sección para dar contexto
        otros = [p for p in plots if p != tipo_lower]
        otros_txt = f"  (tb: {', '.join(otros)})" if otros else ""
        print(f"  {nombre:<25} dia {rango_dias(info)}{otros_txt}")

    if not encontrado:
        print("  (no encontrado)")
    print()


def mostrar_location(datos, location):
    """
    Qué secciones ocurren en un lugar específico,
    con qué días y qué personajes hay.
    """
    location_lower = location.lower()
    secciones = datos.get("por_seccion", {})
    orden     = obtener_orden(datos)

    # Verificar que existe en el global
    locs_globales = datos.get("global", {}).get("data-location", [])
    if location_lower not in [l.lower() for l in locs_globales]:
        parecidas = [l for l in locs_globales if location_lower in l.lower()]
        print(f"\n[AVISO] '{location}' no esta en la lista de locations.")
        if parecidas:
            print(f"  Similares: {', '.join(parecidas)}")
        else:
            print(f"  Locations disponibles: {', '.join(locs_globales)}")
        print()
        return

    print(f"\nLocation '{location}' aparece en:")
    print("-" * 60)
    print(f"{'SECCION':<22} {'DIAS':<8} SPEAKERS")
    print("-" * 60)

    encontrado = False
    for nombre in orden:
        info  = secciones.get(nombre, {})
        locs  = [l.lower() for l in info.get("data-location", [])]
        if location_lower not in locs:
            continue
        encontrado = True
        speakers = ", ".join(info.get("data-speaker", []))
        print(f"  {nombre:<20} {rango_dias(info):<8} {speakers}")

    if not encontrado:
        print("  (no encontrado en ninguna seccion)")
    print()


# ─────────────────────────────────────────────
# PARA LA IA
# ─────────────────────────────────────────────

def generar_prompt(datos, nombre_raw):
    """
    Genera un bloque de contexto listo para pegar al inicio de un prompt.
    Incluye la sección pedida completa + anterior/siguiente resumidas.
    Máximo ahorro de tokens con información mínima necesaria.
    También guarda el bloque en prompt_context.txt para copiar fácilmente.
    """
    secciones = datos.get("por_seccion", {})
    orden     = obtener_orden(datos)
    nombre    = normalizar_seccion(nombre_raw)
    validar_seccion(secciones, nombre)

    idx = orden.index(nombre)
    lineas = ["=== CONTEXTO DE SECCION (generado por query_index.py) ===\n"]

    # Sección anterior (muy resumida)
    if idx > 0:
        prev   = orden[idx - 1]
        info_p = secciones.get(prev, {})
        lineas.append(f"\n[SECCION ANTERIOR: {prev} | dia {rango_dias(info_p)}]\n")
        lineas.append(f"  locations: {', '.join(info_p.get('data-location', []))}\n")
        lineas.append(f"  speakers : {', '.join(info_p.get('data-speaker', []))}\n")
        lineas.append(f"  plot     : {', '.join(info_p.get('data-plot', []))}\n")

    # Sección actual (completa)
    info  = secciones[nombre]
    stats = info.get("_stats", {})
    lineas.append(f"\n[SECCION ACTUAL: {nombre} | dia {rango_dias(info)} | "
                  f"{stats.get('total_parrafos','?')} parrafos]\n")

    campos_prompt = [
        ("data-location",     "locations"),
        ("data-speaker",      "speakers"),
        ("data-to",           "to"),
        ("data-focus",        "focus"),
        ("data-type",         "tipos"),
        ("data-emotion",      "emociones"),
        ("data-plot",         "plot"),
        ("data-relationship", "relaciones"),
        ("data-rel-direction","rel-dir"),
    ]
    for clave, etiqueta in campos_prompt:
        valores = info.get(clave)
        if valores:
            lineas.append(f"  {etiqueta:<12}: {', '.join(valores)}\n")

    # Sección siguiente (muy resumida)
    if idx < len(orden) - 1:
        nxt    = orden[idx + 1]
        info_n = secciones.get(nxt, {})
        lineas.append(f"\n[SECCION SIGUIENTE: {nxt} | dia {rango_dias(info_n)}]\n")
        lineas.append(f"  locations: {', '.join(info_n.get('data-location', []))}\n")
        lineas.append(f"  speakers : {', '.join(info_n.get('data-speaker', []))}\n")
        lineas.append(f"  plot     : {', '.join(info_n.get('data-plot', []))}\n")

    lineas.append("\n=== FIN CONTEXTO ===\n")

    bloque = "".join(lineas)
    print(bloque)

    # Guardar para copiar fácilmente
    destino = Path(__file__).parent.parent / "prompt_context.txt"
    with open(destino, "w", encoding="utf-8") as f:
        f.write(bloque)
    print(f"(guardado en {destino})\n")


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Consulta rapida del index.json sin leerlo completo.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Básicos
    parser.add_argument("--seccion",    metavar="NOMBRE",
                        help="Detalles de una seccion (ej: seccion_08, 08 o seccion_08.html)")
    parser.add_argument("--pendientes", action="store_true",
                        help="Lista secciones con parrafos sin anotar")
    parser.add_argument("--exportar",   action="store_true",
                        help="Genera index_compact.md")

    # Búsqueda
    parser.add_argument("--buscar",    nargs="+", metavar="TERM",
                        help="AND: todos los términos deben aparecer en la seccion")
    parser.add_argument("--buscar-o",  nargs="+", metavar="TERM",
                        help="OR: basta con que uno de los terminos aparezca")
    parser.add_argument("--sin-campo", metavar="CAMPO",
                        help="Secciones que NO tienen ese campo (ej: data-relationship)")

    # Personajes y relaciones
    parser.add_argument("--personaje", metavar="NOMBRE",
                        help="Arco completo de un personaje (ej: axel)")
    parser.add_argument("--relacion",  metavar="PAR",
                        help="Evolucion de una relacion (ej: axel-seraphina)")

    # Navegación
    parser.add_argument("--contexto",  metavar="NOMBRE",
                        help="Seccion anterior + actual + siguiente")
    parser.add_argument("--timeline",  action="store_true",
                        help="Mapa de los 11 dias con sus secciones")
    parser.add_argument("--plot",      metavar="TIPO",
                        help="Donde esta distribuido un tipo de plot (ej: climax)")
    parser.add_argument("--location",  metavar="LUGAR",
                        help="Que secciones ocurren en ese lugar (ej: valle-mariposas)")

    # Para la IA
    parser.add_argument("--prompt",    metavar="NOMBRE",
                        help="Bloque de contexto listo para pegar en un prompt")

    args  = parser.parse_args()
    datos = cargar_index()

    # Despacho — se ejecuta solo la primera opción que encuentre
    if args.seccion:
        mostrar_seccion(datos, args.seccion)
    elif args.pendientes:
        mostrar_pendientes(datos)
    elif args.exportar:
        exportar_compact(datos)
    elif args.buscar:
        buscar_terminos(datos, args.buscar, modo_or=False)
    elif getattr(args, "buscar_o", None):
        buscar_terminos(datos, args.buscar_o, modo_or=True)
    elif args.sin_campo:
        sin_campo(datos, args.sin_campo)
    elif args.personaje:
        mostrar_personaje(datos, args.personaje)
    elif args.relacion:
        mostrar_relacion(datos, args.relacion)
    elif args.contexto:
        mostrar_contexto(datos, args.contexto)
    elif args.timeline:
        mostrar_timeline(datos)
    elif args.plot:
        mostrar_plot(datos, args.plot)
    elif args.location:
        mostrar_location(datos, args.location)
    elif args.prompt:
        generar_prompt(datos, args.prompt)
    else:
        # Sin argumentos → resumen general
        mostrar_resumen(datos)


if __name__ == "__main__":
    main()
