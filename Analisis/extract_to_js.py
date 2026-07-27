#!/usr/bin/env python3
"""
extract_to_js.py
Extrae el contenido narrativo de seccion_NN.html y genera seccion-NN-historia.js
para el lector de pantalla.

Uso:
    python Analisis/extract_to_js.py              # default: seccion_01
    python Analisis/extract_to_js.py --seccion 02
    python Analisis/extract_to_js.py --seccion 07A

Salida:
    secciones/seccion-NN-historia.js
"""
import re, os, sys, argparse
from collections import Counter

# ── Argumentos de línea de comandos ──────────────────────────────────────────
parser = argparse.ArgumentParser(description='Extrae HTML narrativo a JS')
parser.add_argument('--seccion', default='01',
                    help='Número (y sufijo opcional) de sección, ej: 01, 02, 07A')
args = parser.parse_args()

seccion = args.seccion.upper()          # normalizar: "02" → "02", "07a" → "07A"
seccion_lower = seccion.lower()         # para nombres de archivo de salida

BASE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
)
HTML_IN = os.path.join(BASE_DIR, 'secciones', f'seccion_{seccion_lower}.html')
JS_OUT  = os.path.join(BASE_DIR, 'secciones', f'seccion-{seccion_lower}-historia.js')
CONST_NAME = f'CAPITULO_{seccion}'     # ej: CAPITULO_01, CAPITULO_02, CAPITULO_07A

# ── Leer HTML ─────────────────────────────────────────────────────────────
print(f'Leyendo: {HTML_IN}')
if not os.path.exists(HTML_IN):
    sys.exit(f'ERROR: no se encontró el archivo {HTML_IN}')

with open(HTML_IN, encoding='utf-8') as f:
    html = f.read()

# ── Detectar subtítulo ────────────────────────────────────────────────────
# 1) Buscar <h2> en el documento
h2_m = re.search(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
if h2_m:
    subtitulo = re.sub(r'<[^>]+>', '', h2_m.group(1)).strip()
else:
    # 2) Fallback: extraer de <title>
    title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    if title_m:
        raw_title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
        # El título suele ser "Nombre del libro - Subtítulo del capítulo"
        # Tomar la parte después del primer " - " si existe
        parts = raw_title.split(' - ', 1)
        subtitulo = parts[1] if len(parts) > 1 else raw_title
    else:
        subtitulo = f'Capítulo {seccion}'

print(f'  Subtítulo detectado: "{subtitulo}"')

# ── Detectar <section> principal (opcional) ──────────────────────────────
# Algunos archivos (seccion_03B) no tienen <section> — se toma el <body> entero.
all_sections = list(re.finditer(r'<section\b[^>]*\bid="([^"]+)"[^>]*>', html))

if all_sections:
    # Elegir la sección raíz: la primera que NO tenga class="new-content"
    root_section_id = None
    for sm in all_sections:
        if 'new-content' not in sm.group(0):
            root_section_id = sm.group(1)
            break
    if root_section_id is None:
        root_section_id = all_sections[0].group(1)
    print(f'  Sección raíz detectada: id="{root_section_id}"')
else:
    print('  (sin <section>: se procesa el <body> completo)')

# ── Aislar cuerpo ────────────────────────────────────────────────────────
# Empezar desde <body> para no perder contenido huérfano antes de la primera
# <section> (caso seccion_04: <div class="contenido-condicional"> con párrafos).
body_open = re.search(r'<body\b[^>]*>', html)
body_close = html.rfind('</body>')
body_start = body_open.end() if body_open else 0

# Tomar hasta el último </section> o </body> del documento.
last_close = max(html.rfind('</section>'), body_close)
if last_close == -1 or last_close < body_start:
    body_end = len(html)
else:
    body_end = last_close

body = html[body_start:body_end]

# ── Recopilar tokens con su posición ─────────────────────────────────────
tokens = []

# h3 headings
for hm in re.finditer(r'<h3[^>]*>(.*?)</h3>', body, re.DOTALL):
    tokens.append({'pos': hm.start(), 'tag': 'h3', 'tipo': None, 'raw': hm.group(1)})

# p.texto-narrativo y p.dialogo
for pm in re.finditer(r'<p\b([^>]*)>(.*?)</p>', body, re.DOTALL):
    attrs = pm.group(1)
    inner = pm.group(2)
    if re.search(r'class="[^"]*texto-narrativo[^"]*"', attrs):
        tokens.append({'pos': pm.start(), 'tag': 'p', 'tipo': 'narrativo', 'raw': inner})
    elif re.search(r'class="[^"]*dialogo[^"]*"', attrs):
        tokens.append({'pos': pm.start(), 'tag': 'p', 'tipo': 'dialogo', 'raw': inner})

# div.book-image-scroll (imagen + caption)
for dm in re.finditer(
    r'<div[^>]*\bclass="book-image-scroll"[^>]*>.*?</div>\s*</div>',
    body, re.DOTALL
):
    block = dm.group(0)
    src_m = re.search(r'\bsrc="([^"]+)"', block)
    alt_m = re.search(r'\balt="([^"]*)"', block)
    cap_m = re.search(r'<div[^>]*\bclass="image-caption"[^>]*>(.*?)</div>', block, re.DOTALL)
    if src_m:
        tokens.append({
            'pos': dm.start(), 'tag': 'imagen', 'tipo': None,
            'data': {
                'src':     src_m.group(1),
                'alt':     alt_m.group(1) if alt_m else '',
                'caption': cap_m.group(1).strip() if cap_m else '',
            }
        })

tokens.sort(key=lambda x: x['pos'])

# ── Limpieza de HTML interno (conservar <em> para itálicas) ──────────────
def clean(s):
    s = re.sub(r'<(?!/?em\b)[^>]+>', '', s)  # quitar todos los tags excepto <em>
    s = (s.replace('&amp;', '&')
          .replace('&lt;', '<')
          .replace('&gt;', '>')
          .replace('&nbsp;', ' ')
          .replace('&#8212;', '—')
          .replace('&mdash;', '—'))
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# ── Construir lista ordenada de ítems ────────────────────────────────────
items = []
for tok in tokens:
    tag = tok['tag']
    if tag == 'h3':
        t = clean(tok['raw'])
        if t:
            items.append({'tipo': 'h3', 'texto': t})
    elif tag == 'p':
        t = clean(tok['raw'])
        if t:
            items.append({'tipo': tok['tipo'], 'texto': t})
    elif tag == 'imagen':
        items.append({'tipo': 'imagen', **tok['data']})

# ── Serializar a JS (template literals para manejo seguro de comillas) ────
def js_esc(s):
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

lines = [
    '// Generado automáticamente por Analisis/extract_to_js.py',
    '// NO editar manualmente — regenerar con:',
    f'//   python Analisis/extract_to_js.py --seccion {seccion}',
    '',
    f'const {CONST_NAME} = {{',
    '  titulo:    "El Cazador de Medianoche",',
    f'  subtitulo: "{js_esc(subtitulo)}",',
    '  parrafos: [',
]

for item in items:
    t = item['tipo']
    if t in ('narrativo', 'dialogo', 'h3'):
        s = js_esc(item['texto'])
        lines.append(f'    {{ tipo: "{t}", texto: `{s}` }},')
    elif t == 'imagen':
        src = js_esc(item['src'])
        alt = js_esc(item['alt'])
        cap = js_esc(item['caption'])
        lines.append(f'    {{ tipo: "imagen", src: `{src}`, alt: `{alt}`, caption: `{cap}` }},')

lines += ['  ],', '};', '']

with open(JS_OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

counts = Counter(x['tipo'] for x in items)
print(f'Generado: {JS_OUT}')
print(f'  h3={counts["h3"]}  narrativo={counts["narrativo"]}  '
      f'dialogo={counts["dialogo"]}  imagen={counts["imagen"]}')
print(f'  Total: {len(items)} items')
