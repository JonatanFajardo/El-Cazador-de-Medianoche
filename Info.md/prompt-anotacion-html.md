# PROMPT PARA ANOTAR SECCIONES HTML CON METADATA DE PERSONAJES

## Tu tarea

Vas a recibir un archivo HTML de una sección de una novela de fantasía. Tu trabajo es **agregar atributos `data-*` a cada etiqueta `<p>`** sin modificar el texto ni la estructura existente. No cambies clases, no cambies el contenido, no cambies el `data-badge` si ya existe. Solo agrega los nuevos atributos.

---

## Atributos a agregar

Agrega estos atributos a **cada `<p>` que tenga clase `dialogo` o `texto-narrativo`**. No toques `<h2>`, `<h3>`, `<div>`, `<img>`, ni ningún otro elemento.

### Lista completa de atributos:

| Atributo | Obligatorio | Valores posibles | Descripción |
|---|---|---|---|
| `data-speaker` | Solo en diálogos | nombre en minúscula | Quién dice este diálogo |
| `data-to` | Solo en diálogos | nombre(s) separados por coma, o `grupo`, `si-mismo`, `nadie` | A quién va dirigido |
| `data-focus` | Siempre | nombre(s) separados por coma, o `ambiente` | Personaje(s) sobre quien trata este párrafo narrativo |
| `data-type` | Siempre | Ver lista abajo | Tipo de contenido |
| `data-emotion` | Siempre | Ver lista abajo | Emoción dominante |
| `data-intensity` | Siempre | `1`, `2`, `3`, `4`, `5` | Intensidad emocional (1=sutil, 5=extrema) |
| `data-tension` | Siempre | `1`, `2`, `3`, `4`, `5` | Nivel de tensión/suspense |
| `data-plot` | Siempre | Ver lista abajo | Función narrativa |
| `data-location` | Siempre | Ver lista abajo | Lugar donde ocurre |
| `data-day` | Siempre | `1` a `11` | Día cronológico de la historia |
| `data-scene` | Siempre | `01`, `02`, `03`... | Número de escena dentro de la sección (cambia con cada `<h3>` o cambio de escena claro) |
| `data-relationship` | Si aplica, sino omitir | `personaje1-personaje2` (orden alfabético) | Qué relación se desarrolla |
| `data-rel-direction` | Si hay `data-relationship` | `positiva`, `negativa`, `tensa`, `neutral` | Dirección de la relación en este momento |
| `data-secret` | Solo si aplica | `true` | Marcar SOLO si el párrafo contiene engaño activo o información que el lector desconoce |
| `data-reveals` | Solo si aplica | texto breve | Qué información nueva se revela aquí |

---

## Valores permitidos

### `data-type` (tipo de contenido):
- `dialogo` — Personaje hablando
- `accion` — Movimiento físico, combate, persecución
- `descripcion` — Paisaje, ambiente, escenario
- `introspeccion` — Pensamientos internos, reflexiones del personaje
- `flashback` — Recuerdo de evento pasado
- `profecia` — Profecía, visión o predicción
- `transicion` — Párrafo que conecta escenas o marca paso del tiempo

### `data-emotion` (emoción dominante):
- `miedo` — Temor, ansiedad, pánico
- `ira` — Enojo, frustración, rabia
- `tristeza` — Melancolía, pena, duelo
- `alegria` — Felicidad, satisfacción, alivio
- `ternura` — Cariño, empatía, calidez
- `culpa` — Remordimiento, vergüenza
- `desconfianza` — Sospecha, cautela, recelo
- `esperanza` — Optimismo, anticipación positiva
- `determinacion` — Resolución, firmeza, coraje
- `humor` — Diversión, ironía, comicidad
- `nostalgia` — Añoranza del pasado
- `asombro` — Sorpresa, maravilla
- `neutral` — Sin carga emocional dominante

### `data-plot` (función narrativa):
- `setup` — Establece información, contexto o reglas del mundo
- `desarrollo` — Avanza la trama o profundiza personajes
- `climax` — Punto de máxima tensión en la escena
- `resolucion` — Cierre o alivio de tensión
- `foreshadowing` — Pista sobre eventos futuros
- `payoff` — Recompensa de algo establecido antes
- `revelacion` — Se descubre información importante
- `gancho` — Genera curiosidad o suspense para lo que viene

### `data-location` (lugares de la historia):
- `montanas-heladas` — Montañas Heladas, hogar de Axel
- `cabana-axel` — Cabaña familiar de Axel
- `cueva-refugio` — Cueva de emergencia de Axel
- `puesto-comercial` — Puesto comercial de montaña
- `valle-susurradores` — Valle de los Susurradores
- `bosque-cuervos-espejo` — Bosque de los Cuervos Espejo
- `cuevas-brillantes` — Cuevas Brillantes / Santuario de Osos de Cristal
- `aldea-zorros-plateros` — Aldea de los Zorros Plateros
- `jardin-intenciones` — Jardín de Intenciones
- `valle-tranquilo` — Valle Tranquilo (hogar de Ember)
- `rio-nutrias` — Río de las Nutrias Velocistas
- `cueva-murcielagos` — Cueva de los Murciélagos Críticos
- `valle-mariposas` — Valle de las Mariposas Mensajeras
- `laberinto-tejones` — Laberinto de los Tejones Excavadores
- `templo-celestial` — Templo Celestial
- `campamento` — Campamento temporal en el camino
- `camino` — En tránsito entre ubicaciones
- `otro` — Ubicación no listada (especificar en el valor)

---

## Personajes principales (usar estos nombres exactos en los atributos):

- `axel` — Gato montés arquero, protagonista
- `seraphina` — Mantis religiosa, deuteragonista/antagonista
- `ember` — Hermano menor de Axel
- `lyra` — Gata montés rastreadora
- `lumina` — Luciérnaga guardiana
- `piedra-vieja` — Tejón comerciante
- `groundbreaker` — Líder de tejones mineros
- `luna-suave` — Esposa de Ember
- `sol` — Hija de Ember
- `sombra` — Hijo de Ember
- `problemas` — Búho nival rescatado por Axel
- `padre-axel` — Padre/espíritu del padre de Axel
- `madre-seraphina` — Madre de Seraphina

Si aparece un personaje no listado, usa su nombre en minúscula sin acentos, con guiones en vez de espacios.

---

## Reglas críticas

### 1. Identificación de hablante implícito
Cuando un `<p class="dialogo">` NO menciona quién habla, debes deducirlo del contexto:
- El párrafo narrativo inmediatamente anterior o posterior suele indicar quién habla
- Si dos personajes dialogan, los turnos alternan
- Verbos como "murmuró", "dijo", "respondió" en párrafos narrativos adyacentes indican el hablante del diálogo previo o siguiente

### 2. Párrafos narrativos que son acotaciones de diálogo
En este HTML, muchos diálogos están seguidos de un `<p class="texto-narrativo">` que es realmente la acotación del diálogo (quién lo dijo, cómo lo dijo). Ejemplo:

```html
<p class="dialogo"> —Por favor....— </p>
<p class="texto-narrativo"> su voz se quebró, mientras sus antenas temblaban. </p>
```

Ese segundo `<p>` es una **acotación del diálogo de Seraphina**. Debe llevar:
- `data-focus="seraphina"` (no `ambiente`)
- `data-type="dialogo"` (porque funciona como parte del diálogo, no como narración independiente)

### 3. No modificar nada existente
- NO cambies el texto dentro de los `<p>`
- NO cambies las clases (`dialogo`, `texto-narrativo`)
- NO cambies ni elimines `data-badge` existentes
- NO cambies la estructura HTML (divs, sections, headers, imágenes)
- SOLO agrega los nuevos atributos `data-*`

### 4. Orden de atributos
Mantén este orden dentro de cada `<p>`:
```
class → data-badge (si existe) → data-speaker → data-to → data-focus → data-type → data-emotion → data-intensity → data-tension → data-plot → data-location → data-day → data-scene → data-relationship → data-rel-direction → data-secret → data-reveals
```

### 5. Escenas
Incrementa el número de `data-scene` cada vez que:
- Aparece un nuevo `<h3>`
- Hay un cambio claro de ubicación
- Hay un salto temporal significativo
- Hay un comentario HTML separador (como `<!-- ===== NUEVA ESCENA ===== -->`)

---

## Ejemplo completo de entrada y salida

### ENTRADA:
```html
<h3>El Encuentro Fatídico</h3>
<p class="texto-narrativo">Las huellas conducían hacia el paso del este.</p>

<p class="texto-narrativo">Al bordear las rocas nevadas, la encontró.</p>

<p class="texto-narrativo">La mantis religiosa yacía entre las piedras como una escultura rota.</p>

<p class="dialogo"> —Por favor....— </p>

<p class="texto-narrativo"> su voz se quebró, mientras sus antenas temblaban. </p>

<p class="dialogo"> —Necesito.... necesito ayuda— </p>
```

### SALIDA:
```html
<h3>El Encuentro Fatídico</h3>
<p class="texto-narrativo" data-focus="axel" data-type="accion" data-emotion="desconfianza" data-intensity="2" data-tension="3" data-plot="desarrollo" data-location="montanas-heladas" data-day="1" data-scene="04">Las huellas conducían hacia el paso del este.</p>

<p class="texto-narrativo" data-focus="axel" data-type="accion" data-emotion="asombro" data-intensity="3" data-tension="4" data-plot="desarrollo" data-location="montanas-heladas" data-day="1" data-scene="04">Al bordear las rocas nevadas, la encontró.</p>

<p class="texto-narrativo" data-focus="seraphina" data-type="descripcion" data-emotion="tristeza" data-intensity="3" data-tension="4" data-plot="setup" data-location="montanas-heladas" data-day="1" data-scene="04">La mantis religiosa yacía entre las piedras como una escultura rota.</p>

<p class="dialogo" data-speaker="seraphina" data-to="axel" data-focus="seraphina" data-type="dialogo" data-emotion="miedo" data-intensity="4" data-tension="4" data-plot="desarrollo" data-location="montanas-heladas" data-day="1" data-scene="04" data-relationship="axel-seraphina" data-rel-direction="neutral"> —Por favor....— </p>

<p class="texto-narrativo" data-focus="seraphina" data-type="dialogo" data-emotion="miedo" data-intensity="4" data-tension="4" data-plot="desarrollo" data-location="montanas-heladas" data-day="1" data-scene="04"> su voz se quebró, mientras sus antenas temblaban. </p>

<p class="dialogo" data-speaker="seraphina" data-to="axel" data-focus="seraphina" data-type="dialogo" data-emotion="tristeza" data-intensity="4" data-tension="4" data-plot="desarrollo" data-location="montanas-heladas" data-day="1" data-scene="04" data-relationship="axel-seraphina" data-rel-direction="neutral"> —Necesito.... necesito ayuda— </p>
```

---

## Instrucción final

Procesa el archivo HTML completo que te proporcionaré. Devuelve el HTML completo con todos los atributos agregados. No omitas ningún `<p>`. No resumas. No expliques. Solo devuelve el HTML anotado.
