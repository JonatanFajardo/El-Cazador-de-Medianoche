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

Usa una "huella" compuesta por:
- `data-day` + `data-scene` + `data-type` + `data-focus` + `data-speaker`
- Primeros 60 caracteres del texto

Si la IA externa cambia estos atributos clave en un párrafo, patch.py puede no encontrarlo en el original y lo reportará como **NO ENCONTRADO**. En ese caso hay que aplicar el cambio manualmente.

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

## Estado del proyecto

- [ ] Secciones anotadas con `data-*`: pendiente confirmar cuáles
- [ ] `index.json` generado: ejecutar `index.py` para crearlo
- [ ] Inconsistencia pendiente: descripción de Lyra (seccion_02 vs referencia canónica)
