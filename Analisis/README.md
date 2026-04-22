# analisis/scripts — Herramientas de filtrado narrativo

## Estructura esperada del proyecto

```
proyecto/
├── secciones/
│   ├── seccion_01.html
│   ├── seccion_02.html
│   └── ...
└── analisis/
    └── scripts/
        ├── index.py
        ├── filter.py
        ├── patch.py
        └── README.md
```

## Dependencias

```bash
pip install beautifulsoup4
```

---

## 1. index.py — Mapa de toda la historia

Genera `index.json` con todos los valores existentes en los HTML, agrupados por sección y globalmente. Úsalo para saber qué existe antes de filtrar.

```bash
python index.py
python index.py --output mi_index.json
python index.py --secciones ../../secciones
```

**Salida:** `index.json`

---

## 2. filter.py — Extrae fragmentos para la IA

Filtra párrafos por cualquier combinación de `data-*` y genera un HTML temporal con contexto (h2/h3). Este archivo es el que le pasas a la IA para que haga cambios.

```bash
# Todos los diálogos de Axel
python filter.py --speaker axel

# Relación Axel-Seraphina en el día 3
python filter.py --relationship axel-seraphina --day 3

# Escenas de miedo o ira
python filter.py --emotion miedo,ira

# Solo en una sección
python filter.py --speaker axel --section seccion_02.html

# Guardar con nombre específico
python filter.py --speaker axel --output axel_dia3.html
```

**Filtros disponibles:**
`--speaker` `--to` `--focus` `--type` `--emotion` `--intensity` `--tension`
`--plot` `--location` `--day` `--scene` `--relationship` `--rel_direction` `--secret`

Múltiples valores con coma: `--emotion miedo,ira` (OR dentro del mismo filtro).
Todos los filtros entre sí son AND.

**Salida:** `story_temp.html` (o el que indiques con `--output`)

---

## 3. patch.py — Aplica los cambios al original

Una vez que la IA editó el `story_temp.html`, este script reemplaza los párrafos en los archivos originales.

```bash
# Aplicar cambios
python patch.py

# Ver qué cambiaría sin modificar nada
python patch.py --dry-run

# Con backup de seguridad (.bak)
python patch.py --backup

# Desde un archivo con nombre diferente
python patch.py --input axel_dia3_editado.html
```

---

## Flujo completo

```
1. python index.py
   → La IA lee index.json y sabe qué filtrar

2. python filter.py --speaker axel --day 3
   → Genera story_temp.html con los párrafos relevantes + contexto h2/h3

3. [IA edita story_temp.html]
   → Solo modifica el contenido de los <p>, nunca la estructura

4. python patch.py --dry-run
   → Verificar cambios antes de aplicar

5. python patch.py --backup
   → Aplica cambios y guarda .bak de seguridad
```

---

## Notas para la IA que edita story_temp.html

- **No eliminar** ni mover etiquetas `<section data-source='...'>`
- **No eliminar** ni mover `<h2>` y `<h3>` (son contexto, no se patchean)
- **Solo modificar** el contenido o atributos dentro de los `<p>`
- Los `data-*` pueden cambiarse si el párrafo fue editado narrativamente
- El texto dentro del `<p>` puede cambiarse libremente
