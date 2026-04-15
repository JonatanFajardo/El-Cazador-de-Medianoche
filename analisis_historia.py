"""
analisis_historia.py
Análisis literario: personajes + ritmo narrativo
Lee los archivos seccion_XX.html en orden canónico y extrae texto limpio.
Requiere: pip install spacy networkx pandas matplotlib wordcloud beautifulsoup4
          python -m spacy download es_core_news_sm
"""

import re
import json
from pathlib import Path
from collections import Counter, defaultdict

import spacy
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from wordcloud import WordCloud
from bs4 import BeautifulSoup
from pysentimiento import create_analyzer

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

# Orden canónico de secciones (ajusta si añades o quitas archivos)
ARCHIVOS_HTML = [
    "seccion_01.html",
    "seccion_02.html",
    "seccion_03.html",
    "seccion_03B.html",
    "seccion_04.html",
    "seccion_05.html",
    "seccion_06.html",
    "seccion_07.html",
    "seccion_07A.html",
    "seccion_07B.html",
    "seccion_08.html",
    "seccion_08A.html",
    "seccion_08B.html",
    "seccion_08C.html",
    "seccion_09.html",
    "seccion_09A.html",
    "seccion_09B.html",
    "seccion_10.html",
]

TOP_N_PERSONAJES = 15              # cuántos mostrar en gráficas (los más mencionados)
VENTANA_COOCURRENCIA = 3           # oraciones entre menciones para crear enlace
ARCHIVO_PERSONAJES  = "PERSONAJES-COMPLETO.md"

# ─── CARGA ────────────────────────────────────────────────────────────────────

def extraer_nombres_personajes(ruta: Path) -> list[str]:
    """Lee los encabezados ### del markdown y devuelve nombres canónicos limpios."""
    texto = ruta.read_text(encoding="utf-8")
    nombres = []
    for linea in texto.splitlines():
        if not linea.startswith("### "):
            continue
        nombre = linea[4:].strip()
        # Quitar emojis y marcadores de estado al final
        nombre = re.sub(r'[\U0001F300-\U0001FFFF\u2600-\u26FF\u2700-\u27BF]+.*$', '', nombre).strip()
        # Quitar paréntesis como "(BRASA)"
        nombre = re.sub(r'\s*\([^)]+\)', '', nombre).strip()
        # Quitar descripción tras " - "
        nombre = nombre.split(' - ')[0].strip()
        # Solo nombres con al menos 3 caracteres y sin encabezados genéricos
        if len(nombre) >= 3 and nombre not in ("...", "---"):
            nombres.append(nombre.title())
    # Eliminar duplicados manteniendo orden
    vistos = set()
    unicos = []
    for n in nombres:
        if n not in vistos:
            vistos.add(n)
            unicos.append(n)
    return unicos


def contar_menciones_texto(texto: str, nombres: list[str]) -> Counter:
    """Cuenta ocurrencias de cada nombre con límites de palabra (sin falsos positivos)."""
    c = Counter()
    for nombre in nombres:
        patron = re.compile(r'\b' + re.escape(nombre) + r'\b', re.IGNORECASE)
        total = len(patron.findall(texto))
        if total > 0:
            c[nombre] = total
    return c


def extraer_texto_html(ruta: Path) -> str:
    """Extrae el texto narrativo limpio de un archivo HTML."""
    html = ruta.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    # Eliminar scripts, estilos y navegación
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

nlp = spacy.load("es_core_news_sm")

base = Path(__file__).parent
OUT  = base / "Analisis"
OUT.mkdir(exist_ok=True)

capitulos = []
etiquetas = []

for nombre in ARCHIVOS_HTML:
    ruta = base / nombre
    if ruta.exists():
        capitulos.append(extraer_texto_html(ruta))
        etiquetas.append(nombre.replace(".html", ""))
    else:
        print(f"  (!) No encontrado: {nombre}")

texto = " ".join(capitulos)   # texto completo para wordcloud
n_cap = len(capitulos)
print(f"[OK] Secciones cargadas: {n_cap} -> {', '.join(etiquetas)}")

# ─── MÓDULO 1 · PERSONAJES ────────────────────────────────────────────────────

docs = list(nlp.pipe(capitulos, disable=["parser"]))  # necesario para show/tell (POS)

# 1a. Cargar nombres canónicos desde el markdown
todos_personajes = extraer_nombres_personajes(base / ARCHIVO_PERSONAJES)
print(f"[OK] Personajes cargados del markdown: {len(todos_personajes)}")

# 1b. Contar menciones por sección usando búsqueda exacta de texto
conteo_global: Counter = Counter()
menciones_por_cap: dict[int, Counter] = {}

for i, cap in enumerate(capitulos):
    c = contar_menciones_texto(cap, todos_personajes)
    menciones_por_cap[i] = c
    for nombre, n in c.items():
        conteo_global[nombre] += n

top_personajes = [n for n, _ in conteo_global.most_common(TOP_N_PERSONAJES)]
print(f"[OK] Top {TOP_N_PERSONAJES} por menciones: {', '.join(top_personajes)}")

# 1b. Arco de presencia: cap × personaje
presencia = pd.DataFrame(
    {p: [menciones_por_cap[i].get(p, 0) for i in range(n_cap)]
     for p in top_personajes},
    index=etiquetas
)

# 1c. Grafo de co-ocurrencia
G = nx.Graph()
G.add_nodes_from(top_personajes)

for doc in docs:
    oraciones = list(doc.sents) if doc.has_annotation("SENT_START") else \
                [doc]           # fallback si no hay sents
    for idx, sent in enumerate(oraciones):
        pers_en_sent = {
            e.text.strip().title()
            for e in sent.ents
            if e.label_ == "PER" and e.text.strip().title() in top_personajes
        }
        # Ventana: oraciones cercanas
        ventana = oraciones[max(0, idx - VENTANA_COOCURRENCIA):
                            min(len(oraciones), idx + VENTANA_COOCURRENCIA + 1)]
        pers_ventana = {
            e.text.strip().title()
            for s in ventana
            for e in s.ents
            if e.label_ == "PER" and e.text.strip().title() in top_personajes
        }
        for a in pers_en_sent:
            for b in pers_ventana:
                if a != b:
                    if G.has_edge(a, b):
                        G[a][b]["weight"] += 1
                    else:
                        G.add_edge(a, b, weight=1)

# ─── MÓDULO 2 · RITMO NARRATIVO ───────────────────────────────────────────────

metricas_cap = []
for i, cap in enumerate(capitulos):
    oraciones = [s.strip() for s in re.split(r'[.!?]+', cap) if s.strip()]
    palabras   = cap.split()
    longitudes = [len(s.split()) for s in oraciones]

    # Densidad de diálogos (líneas con «—» o «"»)
    dialogos = len(re.findall(r'[—"«"]', cap))

    # TTR: Root Type-Token Ratio (más estable que TTR crudo en textos de distinta longitud)
    rttr = len(set(cap.lower().split())) / max(len(palabras) ** 0.5, 1)

    # Tiempo de lectura estimado (220 ppm = ritmo cómodo para ficción en español)
    WPM = 220
    minutos = len(palabras) / WPM
    horas   = int(minutos // 60)
    mins    = int(minutos % 60)
    lectura = f"{horas}h {mins:02d}m" if horas else f"{mins}m"

    metricas_cap.append({
        "capitulo"          : etiquetas[i],
        "palabras"          : len(palabras),
        "lectura_estimada"  : lectura,
        "oraciones"         : len(oraciones),
        "longitud_media"    : round(sum(longitudes)/max(len(longitudes), 1), 1),
        "longitud_max"      : max(longitudes) if longitudes else 0,
        "longitud_min"      : min(longitudes) if longitudes else 0,
        "densidad_dialogo"  : round(dialogos / max(len(palabras), 1) * 100, 2),
        "rttr"              : round(rttr, 3),
    })

df_ritmo = pd.DataFrame(metricas_cap).set_index("capitulo")
print(df_ritmo.to_string())

# ─── MÓDULO 3 · CALIDAD DE SECCIONES ─────────────────────────────────────────

# 3a. Show vs Tell — ratio adverbios / verbos por sección
# (docs ya tiene POS porque solo desactivamos "parser", no el tagger)
calidad_rows = []
for i, doc in enumerate(docs):
    adverbios = sum(1 for t in doc if t.pos_ == "ADV")
    verbos    = sum(1 for t in doc if t.pos_ == "VERB")
    ratio_tell = round(adverbios / max(verbos, 1), 3)
    calidad_rows.append({"seccion": etiquetas[i], "ratio_tell": ratio_tell})

df_calidad = pd.DataFrame(calidad_rows).set_index("seccion")
df_calidad["rttr"] = df_ritmo["rttr"]

# 3b. Sentimiento por sección (BERT español via pysentimiento)
print("[...] Cargando modelo de sentimiento (primera vez descarga ~500MB)...")
sent_analyzer = create_analyzer(task="sentiment", lang="es")
print("[OK] Modelo cargado")

CHUNK_PALABRAS = 120   # palabras por chunk para analizar
MAX_CHUNKS = 20        # máximo de chunks por sección (velocidad)

def texto_a_chunks(texto: str, n: int) -> list[str]:
    """Divide el texto en bloques de n palabras."""
    palabras = texto.split()
    return [" ".join(palabras[i:i+n]) for i in range(0, len(palabras), n)]

sentimientos_medios = []
volatilidades = []

for i, cap in enumerate(capitulos):
    chunks = texto_a_chunks(cap, CHUNK_PALABRAS)[:MAX_CHUNKS]

    scores = []
    for chunk in chunks:
        try:
            resultado = sent_analyzer.predict(chunk[:512])
            # Score continuo: P(POS) - P(NEG), rango [-1, +1]
            score = resultado.probas.get("POS", 0.0) - resultado.probas.get("NEG", 0.0)
            scores.append(score)
        except Exception:
            pass

    media = round(sum(scores) / max(len(scores), 1), 3)
    volatilidad = round(pd.Series(scores).std() if len(scores) > 1 else 0.0, 3)
    sentimientos_medios.append(media)
    volatilidades.append(volatilidad)
    print(f"  {etiquetas[i]:12s}  sentimiento={media:+.3f}  volatilidad={volatilidad:.3f}  chunks={len(scores)}")

df_calidad["sentimiento"] = sentimientos_medios
df_calidad["volatilidad"] = volatilidades
print(df_calidad.to_string())

# ─── VISUALIZACIONES ─────────────────────────────────────────────────────────

fig = plt.figure(figsize=(18, 20), facecolor="#0f0f14")
fig.suptitle("Análisis Literario", color="white", fontsize=18, y=0.98)

gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

COLOR_BG  = "#0f0f14"
COLOR_AX  = "#1a1a24"
COLOR_ACC = "#7c6fcd"
COLOR_TXT = "#d4d0f0"

def estilo_ax(ax, titulo=""):
    ax.set_facecolor(COLOR_AX)
    ax.tick_params(colors=COLOR_TXT, labelsize=8)
    ax.spines[:].set_color("#333344")
    if titulo:
        ax.set_title(titulo, color=COLOR_TXT, fontsize=10, pad=8)

# — 1. Frecuencia de personajes (barras horizontales) —
ax1 = fig.add_subplot(gs[0, 0])
estilo_ax(ax1, "Frecuencia de personajes")
nombres_ord = [n for n, _ in conteo_global.most_common(TOP_N_PERSONAJES)][::-1]
valores_ord  = [conteo_global[n] for n in nombres_ord]
colors_bar   = plt.cm.plasma([v / max(valores_ord) for v in valores_ord])
bars = ax1.barh(nombres_ord, valores_ord, color=colors_bar, height=0.6)
ax1.set_xlabel("Menciones", color=COLOR_TXT, fontsize=8)
for bar, val in zip(bars, valores_ord):
    ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2,
             str(val), va="center", color=COLOR_TXT, fontsize=7)

# — 2. Grafo de co-ocurrencia —
ax2 = fig.add_subplot(gs[0, 1])
estilo_ax(ax2, "Grafo de relaciones")
pos   = nx.spring_layout(G, seed=42, k=2)
pesos = [G[u][v]["weight"] for u, v in G.edges()]
pmax  = max(pesos) if pesos else 1
nx.draw_networkx_edges(G, pos, ax=ax2,
    width=[1 + 4 * w/pmax for w in pesos],
    edge_color=[plt.cm.plasma(w/pmax) for w in pesos], alpha=0.7)
nx.draw_networkx_nodes(G, pos, ax=ax2,
    node_size=[300 + 50 * conteo_global.get(n, 0) for n in G.nodes()],
    node_color=COLOR_ACC, alpha=0.9)
nx.draw_networkx_labels(G, pos, ax=ax2,
    font_color=COLOR_TXT, font_size=7)
ax2.axis("off")

# — 3. Arco de presencia por capítulo —
ax3 = fig.add_subplot(gs[1, :])
estilo_ax(ax3, "Arco narrativo de personajes")
cmap = plt.cm.tab10
for idx, p in enumerate(top_personajes):
    ax3.plot(presencia.index, presencia[p],
             marker="o", markersize=3,
             color=cmap(idx / TOP_N_PERSONAJES),
             linewidth=1.5, label=p, alpha=0.85)
ax3.legend(loc="upper right", fontsize=7, facecolor=COLOR_AX,
           labelcolor=COLOR_TXT, framealpha=0.7, ncol=2)
ax3.set_xlabel("Capítulo", color=COLOR_TXT, fontsize=8)
ax3.set_ylabel("Menciones", color=COLOR_TXT, fontsize=8)
plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")

# — 4. Longitud media de oraciones (ritmo) —
ax4 = fig.add_subplot(gs[2, 0])
estilo_ax(ax4, "Ritmo: longitud media de oración")
ax4.fill_between(df_ritmo.index, df_ritmo["longitud_media"],
                 alpha=0.3, color=COLOR_ACC)
ax4.plot(df_ritmo.index, df_ritmo["longitud_media"],
         color=COLOR_ACC, linewidth=1.8, marker="o", markersize=4)
ax4.set_ylabel("Palabras / oración", color=COLOR_TXT, fontsize=8)
plt.setp(ax4.get_xticklabels(), rotation=45, ha="right")

# — 5. Densidad de diálogo —
ax5 = fig.add_subplot(gs[2, 1])
estilo_ax(ax5, "Densidad de diálogo por capítulo (%)")
ax5.bar(df_ritmo.index, df_ritmo["densidad_dialogo"],
        color=plt.cm.viridis(
            df_ritmo["densidad_dialogo"] / df_ritmo["densidad_dialogo"].max()),
        width=0.6)
ax5.set_ylabel("% marcas de diálogo", color=COLOR_TXT, fontsize=8)
plt.setp(ax5.get_xticklabels(), rotation=45, ha="right")

plt.savefig(OUT / "analisis_historia.png", dpi=150, bbox_inches="tight",
            facecolor=COLOR_BG)
print("[OK] Guardado: Analisis/analisis_historia.png")

# — Wordcloud del texto completo —
wc = WordCloud(
    width=1200, height=500,
    background_color="#0f0f14",
    colormap="plasma",
    max_words=150,
    stopwords=set(nlp.Defaults.stop_words),
    collocations=False,
).generate(texto)
wc.to_file(str(OUT / "wordcloud_historia.png"))
print("[OK] Guardado: Analisis/wordcloud_historia.png")

# — Heatmap de co-ocurrencia: personaje × seccion —
fig_hm, ax_hm = plt.subplots(figsize=(16, 6), facecolor=COLOR_BG)
ax_hm.set_facecolor(COLOR_AX)

# Normalizar por fila (por personaje) para que la escala sea comparable
presencia_norm = presencia.T.div(presencia.T.max(axis=1).replace(0, 1), axis=0)

sns.heatmap(
    presencia_norm,
    ax=ax_hm,
    cmap="plasma",
    linewidths=0.4,
    linecolor="#0f0f14",
    annot=presencia.T,          # muestra el número real de menciones
    fmt="d",
    annot_kws={"size": 7, "color": "white"},
    cbar_kws={"shrink": 0.6, "label": "Intensidad relativa"},
)

ax_hm.set_title("Presencia de personajes por seccion", color=COLOR_TXT, fontsize=13, pad=12)
ax_hm.tick_params(colors=COLOR_TXT, labelsize=8)
ax_hm.set_xlabel("Seccion", color=COLOR_TXT, fontsize=9)
ax_hm.set_ylabel("Personaje", color=COLOR_TXT, fontsize=9)
plt.setp(ax_hm.get_xticklabels(), rotation=40, ha="right", color=COLOR_TXT)
plt.setp(ax_hm.get_yticklabels(), rotation=0, color=COLOR_TXT)

# Colorbar labels
cbar = ax_hm.collections[0].colorbar
cbar.ax.tick_params(colors=COLOR_TXT, labelsize=7)
cbar.ax.yaxis.label.set_color(COLOR_TXT)

fig_hm.tight_layout()
fig_hm.savefig(OUT / "heatmap_personajes.png", dpi=150, bbox_inches="tight", facecolor=COLOR_BG)
plt.close(fig_hm)
print("[OK] Guardado: Analisis/heatmap_personajes.png")

# — Calidad de secciones: TTR + Show/Tell + Sentimiento —
fig_cal, (ca1, ca2, ca3) = plt.subplots(3, 1, figsize=(16, 13), facecolor=COLOR_BG)
fig_cal.suptitle("Calidad de secciones", color=COLOR_TXT, fontsize=14, y=0.98)

idx_x = range(len(etiquetas))

# Panel 1: Riqueza léxica (RTTR)
estilo_ax(ca1, "Riqueza lexica por seccion (RTTR — mayor = vocabulario mas variado)")
colores_rttr = plt.cm.RdYlGn(
    (df_calidad["rttr"] - df_calidad["rttr"].min()) /
    (df_calidad["rttr"].max() - df_calidad["rttr"].min() + 1e-9)
)
bars_r = ca1.bar(idx_x, df_calidad["rttr"], color=colores_rttr, width=0.6)
ca1.axhline(df_calidad["rttr"].mean(), color="white", linewidth=0.8,
            linestyle="--", alpha=0.5, label=f'media {df_calidad["rttr"].mean():.2f}')
ca1.set_xticks(idx_x)
ca1.set_xticklabels(etiquetas, rotation=40, ha="right", fontsize=7)
ca1.set_ylabel("RTTR", color=COLOR_TXT, fontsize=8)
ca1.legend(fontsize=7, facecolor=COLOR_AX, labelcolor=COLOR_TXT)
for bar, val in zip(bars_r, df_calidad["rttr"]):
    ca1.text(bar.get_x() + bar.get_width()/2, val + 0.005,
             f"{val:.2f}", ha="center", va="bottom", color=COLOR_TXT, fontsize=6)

# Panel 2: Show vs Tell (ratio adverbios/verbos)
estilo_ax(ca2, "Show vs Tell — ratio adverbios/verbos (menor = mas show, mayor = mas tell)")
colores_tell = plt.cm.RdYlGn_r(
    (df_calidad["ratio_tell"] - df_calidad["ratio_tell"].min()) /
    (df_calidad["ratio_tell"].max() - df_calidad["ratio_tell"].min() + 1e-9)
)
bars_t = ca2.bar(idx_x, df_calidad["ratio_tell"], color=colores_tell, width=0.6)
ca2.axhline(df_calidad["ratio_tell"].mean(), color="white", linewidth=0.8,
            linestyle="--", alpha=0.5, label=f'media {df_calidad["ratio_tell"].mean():.2f}')
ca2.set_xticks(idx_x)
ca2.set_xticklabels(etiquetas, rotation=40, ha="right", fontsize=7)
ca2.set_ylabel("ADV / VERB", color=COLOR_TXT, fontsize=8)
ca2.legend(fontsize=7, facecolor=COLOR_AX, labelcolor=COLOR_TXT)
for bar, val in zip(bars_t, df_calidad["ratio_tell"]):
    ca2.text(bar.get_x() + bar.get_width()/2, val + 0.001,
             f"{val:.2f}", ha="center", va="bottom", color=COLOR_TXT, fontsize=6)

# Panel 3: Sentimiento medio + volatilidad
estilo_ax(ca3, "Arco emocional — sentimiento medio por seccion (azul=neg, verde=pos)")
colores_sent = ["#e05c5c" if v < -0.1 else "#5ce05c" if v > 0.1 else "#9090b0"
                for v in df_calidad["sentimiento"]]
ca3.bar(idx_x, df_calidad["sentimiento"], color=colores_sent, width=0.6, alpha=0.85)
ca3.fill_between(idx_x,
                 df_calidad["sentimiento"] - df_calidad["volatilidad"],
                 df_calidad["sentimiento"] + df_calidad["volatilidad"],
                 alpha=0.15, color="white", label="volatilidad emocional")
ca3.axhline(0, color="white", linewidth=0.6, linestyle="-", alpha=0.3)
ca3.set_xticks(idx_x)
ca3.set_xticklabels(etiquetas, rotation=40, ha="right", fontsize=7)
ca3.set_ylabel("Score (-1 neg / +1 pos)", color=COLOR_TXT, fontsize=8)
ca3.legend(fontsize=7, facecolor=COLOR_AX, labelcolor=COLOR_TXT)

fig_cal.tight_layout(rect=[0, 0, 1, 0.97])
fig_cal.savefig(OUT / "calidad_secciones.png", dpi=150, bbox_inches="tight", facecolor=COLOR_BG)
plt.close(fig_cal)
print("[OK] Guardado: Analisis/calidad_secciones.png")

# ─── EXPORTAR DATOS ───────────────────────────────────────────────────────────

df_ritmo.to_csv(OUT / "ritmo_narrativo.csv")
presencia.to_csv(OUT / "presencia_personajes.csv")
df_calidad.to_csv(OUT / "calidad_secciones.csv")

grafo_data = {
    "nodos": [{"id": n, "menciones": conteo_global[n]} for n in G.nodes()],
    "enlaces": [{"fuente": u, "destino": v, "peso": d["weight"]}
                for u, v, d in G.edges(data=True)]
}
(OUT / "grafo_personajes.json").write_text(json.dumps(grafo_data, ensure_ascii=False, indent=2))

print(f"\n-- Archivos generados en: {OUT} --")
print("  analisis_historia.png    -> dashboard visual completo")
print("  wordcloud_historia.png   -> nube de palabras")
print("  heatmap_personajes.png   -> presencia de personajes por seccion")
print("  calidad_secciones.png    -> TTR + show/tell + arco emocional")
print("  ritmo_narrativo.csv      -> metricas por capitulo")
print("  presencia_personajes.csv -> arco de cada personaje")
print("  calidad_secciones.csv    -> metricas de calidad por seccion")
print("  grafo_personajes.json    -> red de relaciones (importable en Gephi/D3)")