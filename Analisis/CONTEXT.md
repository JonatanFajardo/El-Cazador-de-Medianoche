# CONTEXT — Sistema de edición narrativa asistida por IA

## ¿Qué es esto?

Sistema de scripts para editar una novela de fantasía (*El Cazador de Medianoche*) de forma quirúrgica, extrayendo solo los fragmentos relevantes para que una IA los analice y modifique, minimizando el uso de tokens.

---

## Estructura del proyecto

```
proyecto/
├── secciones/                      ← HTMLs de la novela (fuente de verdad)
│   ├── seccion_01.html
│   ├── seccion_02.html
│   └── ...
└── analisis/
    ├── CONTEXT.md                  ← este archivo
    ├── index.json                  ← generado por index.py (mapa de la historia)
    ├── story_temp.html             ← generado por filter.py (fragmento para IA)
    └── scripts/
        ├── index.py
        ├── filter.py
        ├── patch.py
        └── README.md
```

---

## Los 3 scripts

| Script | Qué hace |
|---|---|
| `index.py` | Lee todos los HTMLs y genera `index.json` con todos los `data-*` únicos por sección y globalmente |
| `filter.py` | Filtra párrafos por `data-*` y genera `story_temp.html` con contexto h2/h3 para la IA |
| `patch.py` | Aplica los cambios del `story_temp.html` editado de vuelta a los HTMLs originales |

### Flags especiales de filter.py

| Flag | Efecto | Cuándo usarla |
|---|---|---|
| `--text "palabra"` | Filtra párrafos cuyo texto contenga esa cadena (case-insensitive, sin acentos). AND con otros filtros. | Buscar ocurrencias de un término específico sin escribir scripts ad-hoc |
| `--minimal` | Output solo con `data-id` + texto. Sin atributos `data-*`. **60% menos tokens.** | Siempre que el objetivo sea edición narrativa |
| `--section seccion_XX.html` | Limita la búsqueda a una sección específica. Solo con este flag ya es filtro suficiente (extrae todos los párrafos de esa sección). | Cuando se quiere exportar una sección completa |
| `--output ruta.html` | Ruta de salida del archivo generado. Default: `story_temp.html` en la carpeta scripts/. | Usar `--output ../story_temp.html` para guardar en Analisis/ |

---

## Flujo completo

### Participantes
- **Claude Code** — ejecuta scripts, aplica patch final, conoce este contexto
- **Claude web (cuenta externa)** — recibe `story_temp.html`, analiza y devuelve el HTML modificado

---

### Paso a paso

```
1. USUARIO define qué quiere cambiar en la historia
        ↓
2. CLAUDE CODE lee index.json y decide los parámetros de filtrado
        ↓
3. CLAUDE CODE ejecuta filter.py con esos parámetros
   → genera analisis/story_temp.html
        ↓
4. USUARIO copia el contenido de story_temp.html
   y se lo pasa a CLAUDE WEB (cuenta externa)
   junto con las instrucciones de cambio
        ↓
5. CLAUDE WEB analiza y devuelve el HTML modificado
        ↓
6. USUARIO guarda el resultado como story_temp.html
   (sobreescribe el anterior)
        ↓
7. CLAUDE CODE ejecuta patch.py --dry-run para verificar
        ↓
8. CLAUDE CODE ejecuta patch.py --backup para aplicar
```

---

## Qué contiene story_temp.html

El archivo generado por `filter.py` incluye:
- Solo los `<p>` que cumplen los filtros
- `<h2>` y `<h3>` de contexto para que la IA sepa en qué escena está
- `<section data-source='seccion_XX.html'>` que indica el archivo de origen

**La IA externa (Claude web) solo debe modificar el contenido o atributos de los `<p>`.  
Nunca debe eliminar ni mover los `<section>`, `<h2>` ni `<h3>`.**

---

## Cómo patch.py identifica cada párrafo

Usa `data-id` como huella primaria (8 caracteres hex únicos por párrafo). Fallback: huella compuesta por `data-day` + `data-scene` + `data-type` + `data-focus` + `data-speaker` + primeros 60 chars del texto.

**Comparación por texto:** patch.py compara solo el contenido interno del párrafo, no los atributos. Esto permite usar `--minimal` en filter.py sin borrar los atributos `data-*` del original.

### Convenciones en story_temp.html

| Convención | Efecto |
|---|---|
| `data-id="NEW" data-after="xxxx"` | Insertar párrafo nuevo después de `xxxx` |
| `data-id="NEW" data-before="xxxx"` | Insertar párrafo nuevo antes de `xxxx` |
| `data-id="xxxx" data-delete="true"` | Eliminar el párrafo con ese id |

**Anti-duplicados:** si un párrafo NEW tiene el mismo texto que uno ya existente, patch.py lo reemplaza en lugar de insertar un duplicado.

### Flags especiales de patch.py

| Flag | Efecto |
|---|---|
| `--dry-run` | Muestra qué haría sin modificar nada |
| `--backup` | Crea `.bak` del archivo antes de modificar |
| `--stamp seccion_XX.html` | Marca todos los párrafos sin `data-updated` como `data-status="original"` con timestamp actual |
| `--force` | Fuerza `data-status="modified"` y `data-updated` en párrafos del story_temp aunque el texto no haya cambiado |

---

## Metadatos HTML (`data-*`)

Cada `<p>` en los HTMLs tiene atributos que describen su contenido narrativo:

| Atributo | Ejemplo | Descripción |
|---|---|---|
| `data-speaker` | `axel` | Quién habla |
| `data-to` | `seraphina` | A quién va dirigido |
| `data-focus` | `axel,seraphina` | Personaje(s) protagonistas del párrafo |
| `data-type` | `dialogo` | Tipo: dialogo, accion, descripcion, introspeccion, flashback, profecia, transicion |
| `data-emotion` | `miedo` | Emoción dominante |
| `data-intensity` | `3` | Intensidad emocional 1–5 |
| `data-tension` | `4` | Nivel de tensión 1–5 |
| `data-plot` | `revelacion` | Función narrativa |
| `data-location` | `montanas-heladas` | Lugar donde ocurre |
| `data-day` | `1` | Día cronológico (1–11) |
| `data-scene` | `04` | Escena dentro de la sección |
| `data-relationship` | `axel-seraphina` | Relación que se desarrolla |
| `data-rel-direction` | `tensa` | Dirección: positiva, negativa, tensa, neutral |
| `data-secret` | `true` | Contiene engaño o info oculta al lector |
| `data-reveals` | `seraphina conoce al padre` | Qué se revela en este párrafo |

---

## Personajes principales

- `axel` — Gato montés arquero, protagonista
- `seraphina` — Mantis religiosa, deuteragonista/antagonista
- `ember` — Hermano menor de Axel
- `lyra` — Gata montés rastreadora
- `lumina` — Luciérnaga guardiana
- `piedra-vieja` — Tejón comerciante
- `groundbreaker` — Líder de tejones mineros
- `luna-suave` — Esposa de Ember
- `sol` / `sombra` — Hijos gemelos de Ember
- `problemas` — Búho nival rescatado por Axel
- `padre-axel` — Espíritu del padre de Axel
- `madre-seraphina` — Madre de Seraphina

---

## Ejemplos de uso frecuente

```bash
# Regenerar el índice después de anotar nuevas secciones
python scripts/index.py

# Extraer todos los diálogos entre Axel y Seraphina
python scripts/filter.py --speaker axel,seraphina --relationship axel-seraphina

# Extraer escenas de un día específico
python scripts/filter.py --day 3

# Extraer párrafos con secretos o revelaciones
python scripts/filter.py --secret true
python scripts/filter.py --plot revelacion

# Verificar patch sin modificar nada
python scripts/patch.py --dry-run

# Aplicar patch con backup de seguridad
python scripts/patch.py --backup
```

---

## Dependencias

```bash
pip install beautifulsoup4
```

---

## Estrategia de filtrado

### Cómo elegir los parámetros correctos para filter.py

**Paso 1 — Leer index.json para saber qué valores existen**

Antes de filtrar, consulta `index.json` → sección `"por_seccion"` para ver qué atributos
tiene la sección que te interesa. Así evitas filtros que devuelvan 0 resultados.

```python
# Ver qué speakers/focus existen en una sección concreta
import json
idx = json.load(open("index.json", encoding="utf-8"))
print(idx["por_seccion"]["seccion_08.html"]["data-speaker"])
print(idx["por_seccion"]["seccion_08.html"]["data-focus"])
```

**Paso 2 — Elegir el atributo más preciso según lo que buscas**

| Qué quieres encontrar | Atributo recomendado | Motivo |
|---|---|---|
| Diálogos de un personaje específico | `--speaker nombre` | Solo captura cuando ese personaje habla |
| Escenas donde aparece un personaje (habla o no) | `--focus nombre` | Más amplio, incluye narrativa |
| Escenas de un lugar concreto | `--location nombre` | Útil para escenas de ambiente |
| Momentos de tensión/giro | `--plot revelacion,climax` | Filtra por función narrativa |
| Secretos u info oculta al lector | `--secret true` | Solo párrafos con `data-secret="true"` |
| Escenas de un día cronológico | `--day 8` | Útil para bloques temporales |
| Una escena específica dentro de una sección | `--scene 03` | Muy preciso, combinar con `--section` |
| Párrafos que contienen una palabra específica | `--text "palabra"` | Reemplaza búsquedas ad-hoc con Python |

**Paso 3 — Usar `--section` para acotar cuando el atributo aparece en muchas secciones**

```bash
# Sin acotar → trae Lyra de las 18 secciones (ruido)
python filter.py --focus lyra

# Acotado → solo Lyra en seccion_02
python filter.py --focus lyra --section seccion_02.html
```

**Paso 4 — Combinar atributos con AND para máxima precisión**

Todos los filtros se combinan con AND. Ejemplo: párrafos donde Axel habla
a Seraphina en el bosque de cuervos espejo:

```bash
python filter.py --speaker axel --to seraphina --location bosque-cuervos-espejo
```

**Paso 5 — Iterar si hay demasiado ruido o pocos resultados**

- Demasiados párrafos → agregar más filtros o `--section`
- Cero párrafos → revisar index.json, el valor puede tener typo o no existir en esa sección
- Resultados de escenas incorrectas → agregar `--scene` o `--day`

### Ejemplos reales usados en este proyecto

```bash
# Escena de cuervos en seccion_08 (cuervo es el foco)
python filter.py --focus cuervo-primario --section seccion_08.html

# Despedida de Ember + puntos de Lyra en seccion_09 (dos focos en una extracción)
python filter.py --focus ember,lyra --section seccion_09.html

# Confesión de Seraphina — solo sus diálogos directos
python filter.py --speaker seraphina --section seccion_09B.html

# Escenas del padre + arco + Vex en seccion_10 (tres focos)
python filter.py --focus padre-axel,vex-sangrante,arco --section seccion_10.html

# Todos los párrafos con secretos revelados
python filter.py --secret true

# Párrafos de foreshadowing en todas las secciones
python filter.py --plot foreshadowing

# ── Nuevas flags ──────────────────────────────────────────────────────────

# Buscar párrafos con la palabra "lince" donde Lyra es foco (sin scripts ad-hoc)
python filter.py --text "lince" --focus lyra

# Buscar todos los párrafos con "entrenamiento" en los diálogos de Seraphina
python filter.py --text "entrenamiento" --speaker seraphina

# Extraer para edición narrativa en Claude Web: modo minimal (60% menos tokens)
python filter.py --focus seraphina --section seccion_01.html --minimal

# Combinado: buscar texto específico + minimal para envío directo a Claude Web
python filter.py --text "lince" --focus lyra --minimal
```

### Regla general

```
Específico primero → ampliar solo si faltan resultados
Siempre usar --section cuando el personaje/lugar aparece en más de 3 secciones
```

---

## Sistema de tracking visual de cambios (mark-changes.js)

Cada párrafo modificado o insertado por patch.py recibe automáticamente:
- `data-status="new"` / `"modified"` / `"original"`
- `data-updated="2026-04-24T19:05:44"` (timestamp con segundos)

El archivo `mark-changes.js` (raíz del proyecto) lee estos atributos y aplica bordes de color en el browser:
- **Verde** — párrafo nuevo
- **Dorado** — párrafo modificado (brillo según antigüedad)
- **Gris sutil** — párrafo original sin editar

Todas las secciones tienen `<script src="../mark-changes.js"></script>` al final del `<body>`.

**Flujo para sellar una sección nueva:**
```bash
python patch.py --stamp seccion_XX.html
```

---

## Estado del proyecto

- [x] Secciones anotadas con `data-*`: 17/18 completas (seccion_03B pendiente — 388 párrafos sin anotar)
- [x] `index.json` generado
- [x] `data-id` únicos asignados a 2,729 párrafos en 18 secciones (`stamp.py`)
- [x] `patch.py` actualizado: data-id primario, inserciones NEW, eliminaciones, anti-duplicados, timestamps
- [x] `filter.py` actualizado: búsqueda sin acentos, --section sin filtro adicional, --output configurable
- [x] `mark-changes.js` creado: tracking visual de cambios por color en el browser
- [x] Backstory v2 aplicado (24-abr-2026): nuevo canon Kira/madre/padre de Axel en seccion_01
- [x] seccion_01: 191 párrafos sellados con --stamp
