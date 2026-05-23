# PROMPT: Dashboard de Análisis Narrativo — El Cazador de Medianoche

## Tu tarea

Crea un archivo HTML completo llamado `dashboard-analisis.html`. Es un dashboard de análisis narrativo para una novela de fantasía llamada **"El Cazador de Medianoche y las Lágrimas Robadas"**. El archivo debe funcionar abriéndolo directamente en el navegador sin servidor ni dependencias locales.

---

## Estilo visual requerido

- **Fondo general:** `#0d1117` (negro azulado oscuro)
- **Fondo de tarjetas/gráficas:** `#161b22`
- **Texto:** `#e6edf3` (blanco suave)
- **Texto secundario:** `#8b949e` (gris)
- **Bordes:** `1px solid #30363d`
- **Fuente:** `'Segoe UI', system-ui, sans-serif`
- **Título principal:** centrado, blanco, grande
- **Subtítulo de cada gráfica:** centrado, gris, más pequeño que el título
- **Línea de media/promedio:** punteada, color `#ffffff` con opacidad 0.5
- **Bordes de barras:** redondeados (`borderRadius: 4`)
- **Grid lines:** sutiles, color `#21262d`

### Sistema de colores por valor (para barras):
Cada gráfica tiene su propia lógica de color. Ver cada gráfica abajo.

---

## Librería

Usa **Chart.js 4** desde CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

Para la gráfica de red de personajes usa **D3.js v7**:
```html
<script src="https://d3js.org/d3.v7.min.js"></script>
```

---

## Datos reales (embeber directamente como JS en el HTML)

```javascript
const SECCIONES = [
  { id: 'seccion_01',  nombre: 'Cap. 1',   dia: 1,  rttr: 24.629, ratio_tell: 0.358, sentimiento: -0.213, volatilidad: 0.374, palabras: 3222,  lectura: '14m', oraciones: 260,  longitud_media: 12.4, densidad_dialogo: 3.91  },
  { id: 'seccion_02',  nombre: 'Cap. 2',   dia: 2,  rttr: 33.094, ratio_tell: 0.406, sentimiento:  0.090, volatilidad: 0.348, palabras: 8488,  lectura: '38m', oraciones: 839,  longitud_media: 10.2, densidad_dialogo: 3.85  },
  { id: 'seccion_03',  nombre: 'Cap. 3',   dia: 3,  rttr: 22.870, ratio_tell: 0.435, sentimiento: -0.287, volatilidad: 0.349, palabras: 3758,  lectura: '17m', oraciones: 278,  longitud_media: 13.5, densidad_dialogo: 3.30  },
  { id: 'seccion_03B', nombre: 'Cap. 3B',  dia: 4,  rttr: 32.537, ratio_tell: 0.402, sentimiento:  0.056, volatilidad: 0.213, palabras: 11061, lectura: '50m', oraciones: 1056, longitud_media: 10.6, densidad_dialogo: 4.85  },
  { id: 'seccion_04',  nombre: 'Cap. 4',   dia: 5,  rttr: 23.993, ratio_tell: 0.313, sentimiento: -0.333, volatilidad: 0.317, palabras: 3313,  lectura: '15m', oraciones: 329,  longitud_media: 10.1, densidad_dialogo: 3.35  },
  { id: 'seccion_05',  nombre: 'Cap. 5',   dia: 6,  rttr: 25.942, ratio_tell: 0.392, sentimiento: -0.271, volatilidad: 0.478, palabras: 3370,  lectura: '15m', oraciones: 311,  longitud_media: 10.9, densidad_dialogo: 3.50  },
  { id: 'seccion_06',  nombre: 'Cap. 6',   dia: 7,  rttr: 23.378, ratio_tell: 0.463, sentimiento: -0.028, volatilidad: 0.502, palabras: 3679,  lectura: '16m', oraciones: 357,  longitud_media: 10.3, densidad_dialogo: 2.56  },
  { id: 'seccion_07',  nombre: 'Cap. 7',   dia: 7,  rttr: 23.364, ratio_tell: 0.394, sentimiento: -0.087, volatilidad: 0.358, palabras: 3570,  lectura: '16m', oraciones: 353,  longitud_media: 10.1, densidad_dialogo: 3.64  },
  { id: 'seccion_07A', nombre: 'Cap. 7A',  dia: 8,  rttr: 23.614, ratio_tell: 0.403, sentimiento:  0.114, volatilidad: 0.426, palabras: 2531,  lectura: '11m', oraciones: 285,  longitud_media:  8.9, densidad_dialogo: 5.53  },
  { id: 'seccion_07B', nombre: 'Cap. 7B',  dia: 8,  rttr: 20.223, ratio_tell: 0.517, sentimiento:  0.108, volatilidad: 0.419, palabras: 2133,  lectura: '9m',  oraciones: 215,  longitud_media:  9.9, densidad_dialogo: 2.95  },
  { id: 'seccion_08',  nombre: 'Cap. 8',   dia: 8,  rttr: 22.096, ratio_tell: 0.458, sentimiento: -0.332, volatilidad: 0.448, palabras: 3531,  lectura: '16m', oraciones: 341,  longitud_media: 10.4, densidad_dialogo: 2.63  },
  { id: 'seccion_08A', nombre: 'Cap. 8A',  dia: 9,  rttr: 29.031, ratio_tell: 0.405, sentimiento: -0.072, volatilidad: 0.506, palabras: 6436,  lectura: '29m', oraciones: 498,  longitud_media: 12.9, densidad_dialogo: 3.05  },
  { id: 'seccion_08B', nombre: 'Cap. 8B',  dia: 9,  rttr: 27.283, ratio_tell: 0.423, sentimiento:  0.010, volatilidad: 0.532, palabras: 5140,  lectura: '23m', oraciones: 412,  longitud_media: 12.5, densidad_dialogo: 3.11  },
  { id: 'seccion_08C', nombre: 'Cap. 8C',  dia: 9,  rttr: 24.524, ratio_tell: 0.380, sentimiento: -0.023, volatilidad: 0.430, palabras: 5133,  lectura: '23m', oraciones: 380,  longitud_media: 13.5, densidad_dialogo: 4.38  },
  { id: 'seccion_09',  nombre: 'Cap. 9',   dia: 9,  rttr: 22.596, ratio_tell: 0.328, sentimiento:  0.089, volatilidad: 0.227, palabras: 3454,  lectura: '15m', oraciones: 242,  longitud_media: 14.3, densidad_dialogo: 5.85  },
  { id: 'seccion_09A', nombre: 'Cap. 9A',  dia: 10, rttr: 24.764, ratio_tell: 0.406, sentimiento: -0.083, volatilidad: 0.373, palabras: 4685,  lectura: '21m', oraciones: 358,  longitud_media: 13.1, densidad_dialogo: 4.65  },
  { id: 'seccion_09B', nombre: 'Cap. 9B',  dia: 10, rttr: 18.153, ratio_tell: 0.524, sentimiento:  0.098, volatilidad: 0.287, palabras: 2297,  lectura: '10m', oraciones: 170,  longitud_media: 13.5, densidad_dialogo: 3.48  },
  { id: 'seccion_10',  nombre: 'Cap. 10',  dia: 11, rttr: 27.210, ratio_tell: 0.400, sentimiento: -0.311, volatilidad: 0.334, palabras: 8280,  lectura: '37m', oraciones: 631,  longitud_media: 13.1, densidad_dialogo: 2.14  },
];

const PRESENCIA_PERSONAJES = {
  labels: ['Cap.1','Cap.2','Cap.3','Cap.3B','Cap.4','Cap.5','Cap.6','Cap.7','Cap.7A','Cap.7B','Cap.8','Cap.8A','Cap.8B','Cap.8C','Cap.9','Cap.9A','Cap.9B','Cap.10'],
  personajes: {
    'Axel':       [36,115,46,119,30,29,44,38,16,18,30,36,28,32,27,30,18,48],
    'Seraphina':  [20, 52,28, 93,18,14,23,27, 8,12,18,26,21,24,21,13,11,49],
    'Ember':      [ 3,  0, 3,  0, 0, 0, 0,30, 9,18,23,37,22,29,19, 0, 1,12],
    'El Erizo':   [ 0,  7, 0,  2, 0, 2, 0, 0, 5, 0, 1, 4, 2, 8, 6, 6, 5,11],
    'Groundbreaker':[0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8,15, 3, 3],
  }
};

const GRAFO_PERSONAJES = {
  nodos: [
    { id: 'Axel',         menciones: 740, color: '#e8c870' },
    { id: 'Seraphina',    menciones: 478, color: '#7bb87b' },
    { id: 'Ember',        menciones: 206, color: '#7098c8' },
    { id: 'El Erizo',     menciones:  59, color: '#b07850' },
    { id: 'Sol',          menciones:  54, color: '#e8a030' },
    { id: 'Luna Suave',   menciones:  41, color: '#a0b8d8' },
    { id: 'Groundbreaker',menciones:  30, color: '#907060' },
    { id: 'Problemas',    menciones:  24, color: '#a0a0a0' },
    { id: 'Eco Pergaminada',menciones:35, color: '#c090c0' },
    { id: 'Sombra',       menciones:  32, color: '#505878' },
  ],
  enlaces: [
    { fuente: 'Axel',      destino: 'Ember',       peso: 24 },
    { fuente: 'Axel',      destino: 'Seraphina',   peso: 22 },
    { fuente: 'Axel',      destino: 'Luna Suave',  peso: 14 },
    { fuente: 'Axel',      destino: 'Sol',         peso: 10 },
    { fuente: 'Axel',      destino: 'Groundbreaker',peso: 10 },
    { fuente: 'Axel',      destino: 'Eco Pergaminada', peso: 6 },
    { fuente: 'Axel',      destino: 'Problemas',   peso: 2  },
    { fuente: 'Seraphina', destino: 'Ember',       peso: 16 },
    { fuente: 'Seraphina', destino: 'Luna Suave',  peso: 10 },
    { fuente: 'Seraphina', destino: 'Sol',         peso: 6  },
    { fuente: 'Seraphina', destino: 'Groundbreaker',peso: 6 },
    { fuente: 'Seraphina', destino: 'Eco Pergaminada',peso: 2},
    { fuente: 'Ember',     destino: 'Luna Suave',  peso: 14 },
    { fuente: 'Ember',     destino: 'Sol',         peso: 10 },
    { fuente: 'Ember',     destino: 'Groundbreaker',peso: 8 },
    { fuente: 'Sol',       destino: 'Luna Suave',  peso: 10 },
    { fuente: 'Sol',       destino: 'Groundbreaker',peso: 6 },
    { fuente: 'Luna Suave',destino: 'Groundbreaker',peso: 6 },
  ]
};
```

---

## Gráficas a generar (8 en total)

### GRÁFICA 1 — Riqueza Léxica por Sección (RTTR)
- **Tipo:** Barras verticales
- **Datos:** `rttr` de cada sección
- **Título:** `Riqueza léxica por sección (RTTR — mayor = vocabulario más variado)`
- **Eje Y label:** `RTTR`
- **Línea de media:** Media de todos los valores, punteada, blanca semitransparente. Mostrar el valor en la leyenda: `media: 24.96`
- **Color de barras por valor:**
  - `rttr < 22` → `#e05252` (rojo)
  - `22 ≤ rttr < 25` → `#e0a030` (naranja/amarillo)
  - `25 ≤ rttr < 29` → `#d4d44a` (amarillo verde)
  - `rttr ≥ 29` → `#4caf50` (verde)
- **Mostrar valor encima de cada barra**

---

### GRÁFICA 2 — Show vs Tell por Sección
- **Tipo:** Barras verticales
- **Datos:** `ratio_tell` de cada sección
- **Título:** `Show vs Tell — ratio adverbios/verbos (menor = más show, mayor = más tell)`
- **Eje Y label:** `ADV/VERB`
- **Línea de media:** Media = 0.41, punteada, blanca semitransparente
- **Color de barras por valor** (aquí MENOR es mejor):
  - `ratio_tell < 0.35` → `#4caf50` (verde — excelente show)
  - `0.35 ≤ ratio_tell < 0.40` → `#d4d44a` (amarillo verde)
  - `0.40 ≤ ratio_tell < 0.46` → `#e0a030` (naranja)
  - `ratio_tell ≥ 0.46` → `#e05252` (rojo — demasiado tell)
- **Mostrar valor encima de cada barra**

---

### GRÁFICA 3 — Arco Emocional de la Historia
- **Tipo:** Combinado: área + línea encima
- **Datos:** `sentimiento` (área rellena) y `volatilidad` (línea separada)
- **Título:** `Arco emocional — sentimiento medio por sección (azul=neg, verde=pos)`
- **Eje Y label:** `Score (-neg / +pos)`
- **Área de sentimiento:**
  - Relleno dinámico: encima de 0 → verde (`#4caf50`) con opacidad 0.4, debajo de 0 → rojo/rosado (`#e05252`) con opacidad 0.4
  - Línea del área: blanca suave
  - Usar `fill: 'origin'`
- **Línea de volatilidad:**
  - Color: `#888888`, opacidad 0.7, punteada
  - Sin relleno
  - Label: `volatilidad emocional`
- **Línea cero:** línea horizontal en y=0, blanca semitransparente punteada
- **Mostrar puntos en cada sección**

---

### GRÁFICA 4 — Palabras por Sección (Extensión)
- **Tipo:** Barras horizontales
- **Datos:** `palabras` de cada sección
- **Título:** `Extensión por sección (palabras)`
- **Eje X label:** `Palabras`
- **Color de barras por valor:**
  - `palabras < 3000` → `#e05252` (rojo — muy corto)
  - `3000 ≤ palabras < 5000` → `#e0a030` (naranja — corto)
  - `5000 ≤ palabras < 8000` → `#d4d44a` (amarillo — medio)
  - `palabras ≥ 8000` → `#4caf50` (verde — extenso)
- **Mostrar etiqueta con lectura estimada** (campo `lectura`) al final de cada barra
- **Orientación:** barras horizontales (secciones en eje Y)

---

### GRÁFICA 5 — Densidad de Diálogo por Sección
- **Tipo:** Barras verticales
- **Datos:** `densidad_dialogo` de cada sección
- **Título:** `Densidad de diálogo por sección (promedio de diálogos cada 100 oraciones)`
- **Eje Y label:** `Diálogos/100 oraciones`
- **Línea de media:** calcularla de los datos, punteada blanca
- **Color de barras:**
  - `< 3.0` → `#e05252` (rojo — poco diálogo)
  - `3.0 – 4.0` → `#d4d44a` (amarillo — normal)
  - `> 4.0` → `#4caf50` (verde — rico en diálogo)
- **Mostrar valor encima de cada barra**

---

### GRÁFICA 6 — Longitud Media de Oraciones
- **Tipo:** Barras verticales
- **Datos:** `longitud_media` de cada sección
- **Título:** `Longitud media de oraciones por sección (palabras/oración)`
- **Eje Y label:** `Palabras/oración`
- **Línea de media:** calcularla, punteada blanca
- **Color de barras:**
  - `< 10` → `#e05252` (rojo — muy cortas, ritmo telegráfico)
  - `10 – 12` → `#4caf50` (verde — ritmo ideal)
  - `12 – 14` → `#d4d44a` (amarillo — un poco largas)
  - `> 14` → `#e05252` (rojo — demasiado largas)
- **Mostrar valor encima de cada barra**

---

### GRÁFICA 7 — Presencia de Personajes por Sección
- **Tipo:** Barras apiladas verticales
- **Datos:** `PRESENCIA_PERSONAJES`
- **Título:** `Presencia de personajes por sección (menciones)`
- **Eje Y label:** `Menciones`
- **Colores por personaje:**
  - Axel: `#e8c870`
  - Seraphina: `#7bb87b`
  - Ember: `#7098c8`
  - El Erizo: `#b07850`
  - Groundbreaker: `#907060`
- **Mostrar leyenda** con los nombres de personajes

---

### GRÁFICA 8 — Red de Interacciones entre Personajes
- **Tipo:** Grafo de red usando D3.js (force-directed graph)
- **Datos:** `GRAFO_PERSONAJES`
- **Título:** `Red de interacciones entre personajes (grosor = frecuencia de co-aparición)`
- **Nodos:**
  - Tamaño proporcional a `menciones` (radio = `Math.sqrt(menciones) * 1.8`)
  - Color según el campo `color` de cada nodo
  - Label con el nombre centrado en el nodo
  - Fondo del label oscuro semitransparente para legibilidad
- **Enlaces:**
  - Grosor proporcional a `peso` (strokeWidth = `peso * 0.4`)
  - Color: `#4a5568`, opacidad 0.6
- **Fuerza:** `d3.forceSimulation` con:
  - `forceLink` con distancia proporcional al peso inverso
  - `forceManyBody` con fuerza -300
  - `forceCenter` al centro del SVG
- **Interactividad:** arrastrar nodos con el mouse
- **Tamaño del SVG:** ancho del contenedor, alto fijo 450px
- **Fondo:** `#161b22`

---

## Layout de la página

```
┌─────────────────────────────────────────────────────────┐
│          EL CAZADOR DE MEDIANOCHE — Análisis            │
│              Narrativo de la Historia                   │
├────────────────────────┬────────────────────────────────┤
│  Gráfica 1 (RTTR)      │  Gráfica 2 (Show vs Tell)      │
├────────────────────────┴────────────────────────────────┤
│              Gráfica 3 (Arco Emocional)                 │  ← ancho completo
├────────────────────────┬────────────────────────────────┤
│  Gráfica 4 (Palabras)  │  Gráfica 5 (Diálogo)          │
├────────────────────────┬────────────────────────────────┤
│  Gráfica 6 (Oraciones) │  Gráfica 7 (Presencia)        │
├────────────────────────┴────────────────────────────────┤
│              Gráfica 8 (Red de personajes)              │  ← ancho completo
└─────────────────────────────────────────────────────────┘
```

- Máximo ancho del contenedor: `1400px`, centrado
- Padding: `24px`
- Gap entre tarjetas: `20px`
- Las tarjetas de lado a lado usan `display: grid; grid-template-columns: 1fr 1fr`
- Las gráficas de ancho completo usan `grid-column: 1 / -1`
- Cada gráfica en una `<div class="card">` con fondo `#161b22`, borde `#30363d`, `border-radius: 12px`, `padding: 20px`
- Cada tarjeta tiene un `<h3>` con el título centrado en blanco y un `<canvas>` o `<div>` para la gráfica

---

## Header de la página

```html
<header>
  <h1>El Cazador de Medianoche</h1>
  <p>Análisis narrativo — 18 secciones · 94,069 palabras · ~424 min lectura</p>
</header>
```

Estilo del header:
- Fondo: `#161b22`
- Borde inferior: `1px solid #30363d`
- Padding: `24px`
- `h1`: blanco, 1.8rem
- `p`: gris `#8b949e`, 0.9rem

---

## Instrucciones adicionales

1. **Todo en un solo archivo HTML.** Sin archivos externos salvo los CDN.
2. **Responsive:** en pantallas menores a 768px, pasar a una columna.
3. **Sin animaciones de entrada** para que cargue rápido.
4. **Tooltips de Chart.js** habilitados con fondo `#1c2128`, texto blanco.
5. **Plugin de datalabels:** para mostrar valores en barras, usar `Chart.js` con el plugin `chartjs-plugin-datalabels` desde CDN: `https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0`
6. Registrar el plugin: `Chart.register(ChartDataLabels);`
7. El plugin de datalabels debe mostrar los valores **encima de las barras** (no adentro), en color blanco, fuente 11px.
8. Para las gráficas de barras horizontales (Gráfica 4), los datalabels van a la **derecha** de la barra.
9. **No usar `import`**. Solo `<script>` con CDN y variables globales.
10. Devuelve el HTML completo, listo para guardar y abrir en el navegador.
