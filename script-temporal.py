"""
mejorar_seccion01.py
Aplica sustituciones léxicas al capítulo 01 para aumentar RTTR (riqueza léxica).
Uso: python mejorar_seccion01.py <ruta_html>
     python mejorar_seccion01.py  (usa "seccion_01.html" por defecto)
"""

import sys
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────────
DEFAULT_FILE = "seccion_01.html"
SUFFIX       = "_mejorada"          # se añade al nombre de salida

# ── Sustituciones ──────────────────────────────────────────────────────────────
# Orden importa: las más específicas primero.
CAMBIOS = [

    # ── RTTR: variar "ojos compuestos" (aparece 6+ veces) ─────────────────────
    (
        "Sus ojos compuestos lo encontraron inmediatamente.",
        "Su mirada facetada lo encontró de inmediato."
    ),
    (
        "sus ojos compuestos se nublaron con lágrimas que no podía derramar",
        "sus ojos iridiscentes se velaron con lágrimas que no podía derramar"
    ),
    (
        "sus ojos compuestos parpadearon —la pregunta la había detenido a medio gesto",
        "su mirada multifacetada parpadeó —la pregunta la había detenido a medio gesto"
    ),
    (
        "Sus ojos compuestos se humedecieron con lágrimas que no podía derramar",
        "Sus ojos facetados brillaron húmedos, con lágrimas que no podía derramar"
    ),
    # La quinta ocurrencia la dejamos intacta para no sobreeditar

    # ── RTTR: variar "garras" en contextos repetidos ──────────────────────────
    (
        "sus garras se clavaron en la nieve, dejando marcas profundas.",
        "sus zarpas se hundieron en la nieve, dejando surcos profundos."
    ),
    (
        "sus garras se clavaban en el suelo de piedra y dejaban surcos finos en la roca.",
        "sus extremidades se clavaban en el suelo de piedra, labrando surcos finos en la roca."
    ),
    (
        "Sus garras tamborilearon nerviosamente contra el mango de su arco.",
        "Sus dedos tamborilearon contra el mango del arco con impaciencia."
    ),
    (
        "sus garras se cerraron en puños temblorosos.",
        "sus extremidades se tensaron en puños temblorosos."
    ),
    (
        "Sus garras temblaban —no del frío, sino de algo más viejo, más pesado.",
        "Sus apéndices temblaban —no del frío, sino de algo más viejo, más pesado."
    ),

    # ── RTTR: variar "montañas / alturas" ────────────────────────────────────
    (
        "Tres años solo en las Montañas Heladas le habían enseñado",
        "Tres años solo entre los picos glaciales le habían enseñado"
    ),
    (
        "no pertenecía a estas alturas heladas.",
        "no pertenecía a estas cumbres gélidas."
    ),

    # ── RTTR: variar "antenas" (aparece 5+ veces) ─────────────────────────────
    (
        "sus antenas se inclinaron hacia él, quietas.",
        "sus sensilias se inclinaron hacia él, inmóviles."
    ),
    (
        "sus antenas se irguieron, inclinadas hacia él.",
        "sus antenas se alzaron, apuntando hacia él."
    ),
    (
        "sus antenas dejaron de temblar por primera vez en cuatro días.",
        "sus palpos dejaron de temblar por primera vez en cuatro días."
    ),

    # ── RTTR: variar "heridas / curar" ────────────────────────────────────────
    (
        "Sus heridas eran más serias de lo que había estimado inicialmente",
        "Sus lesiones resultaron más graves de lo que había estimado"
    ),
    (
        "No era la primera criatura herida que curaba en esa cueva.",
        "No era la primera criatura malherida que había atendido en esa cueva."
    ),

    # ── Show/Tell: un par de adverbios → verbos más expresivos ───────────────
    (
        "acariciaron suavemente una hoja medicinal.",
        "recorrieron una hoja medicinal con reverencia."
    ),
    (
        "pulsó una vez, breve, contra su espalda. No caliente",
        "latió una vez contra su espalda, seco y breve. No caliente"
    ),
]

# ── Lógica principal ──────────────────────────────────────────────────────────
def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE)

    if not src.exists():
        print(f"❌  Archivo no encontrado: {src}")
        sys.exit(1)

    contenido = src.read_text(encoding="utf-8")
    aplicados = 0
    omitidos  = 0

    for viejo, nuevo in CAMBIOS:
        if viejo in contenido:
            contenido = contenido.replace(viejo, nuevo)
            print(f"✅  {viejo[:55].strip()}...")
            aplicados += 1
        else:
            print(f"⚠️   No hallado › {viejo[:55].strip()}...")
            omitidos += 1

    dest = src.with_stem(src.stem + SUFFIX)
    dest.write_text(contenido, encoding="utf-8")

    print(f"\n{'─'*60}")
    print(f"✅  Cambios aplicados : {aplicados}")
    print(f"⚠️   No encontrados   : {omitidos}")
    print(f"📄  Guardado en      : {dest}")


if __name__ == "__main__":
    main()