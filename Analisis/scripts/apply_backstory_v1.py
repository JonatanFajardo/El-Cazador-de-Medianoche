"""
apply_backstory_v1.py — Aplica cambios de backstory y problemas narrativos (22-abr-2026).

Cambios:
  1. Lyra descripción corregida en seccion_02
  2. Seccion_08: cuervos muestran imágenes (no declaran hechos), eliminar "6 víctimas"
  3. Seccion_08: flash del padre eligiendo quedarse
  4. Seccion_09B: confesión voluntaria de Seraphina
  5. Seccion_10: 3 momentos de Umbra + resolución (Templo lo silencia)
  6. Luna Platino: 1 línea en secciones 02, 06, 08C
  7. Flauta de Ember: entrega en 09, resonancia en 10
  8. Búho archivo: inscripción en seccion_09A
  9. Eco Pergaminada: mensaje vía mariposas en seccion_09

Uso:
    python apply_backstory_v1.py --dry-run
    python apply_backstory_v1.py --backup
    python apply_backstory_v1.py
"""

import argparse
import shutil
import uuid
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

SECCIONES = Path("../../secciones")


def uid():
    return uuid.uuid4().hex[:8]


def cargar(filename):
    path = SECCIONES / filename
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    return path, soup


def guardar(path, soup, backup, dry_run):
    if dry_run:
        return
    if backup:
        bak = str(path) + ".bak2"
        if not Path(bak).exists():
            shutil.copy(path, bak)
    path.write_text(str(soup), encoding="utf-8")


def por_id(soup, data_id):
    tag = soup.find("p", attrs={"data-id": data_id})
    if tag is None:
        print(f"    WARN: data-id={data_id} no encontrado")
    return tag


def modificar(soup, data_id, nuevo_html, dry_run):
    """Reemplaza el tag preservando su data-id original."""
    tag = por_id(soup, data_id)
    if tag is None:
        return
    nuevo = BeautifulSoup(nuevo_html.strip(), "html.parser").find("p")
    nuevo["data-id"] = data_id  # conservar ID
    if not dry_run:
        tag.replace_with(nuevo)
    print(f"    MOD  {data_id}")


def insertar_despues(soup, ancla_id, nuevo_html, dry_run):
    """Inserta un nuevo párrafo después del ancla."""
    ancla = por_id(soup, ancla_id)
    if ancla is None:
        return
    nuevo = BeautifulSoup(nuevo_html.strip(), "html.parser").find("p")
    nuevo["data-id"] = uid()
    if not dry_run:
        ancla.insert_after(NavigableString("\n          "))
        ancla.insert_after(nuevo)
    print(f"    INS  after:{ancla_id} → {nuevo['data-id']}")


def insertar_antes(soup, ancla_id, nuevo_html, dry_run):
    """Inserta un nuevo párrafo antes del ancla."""
    ancla = por_id(soup, ancla_id)
    if ancla is None:
        return
    nuevo = BeautifulSoup(nuevo_html.strip(), "html.parser").find("p")
    nuevo["data-id"] = uid()
    if not dry_run:
        ancla.insert_before(nuevo)
        ancla.insert_before(NavigableString("\n          "))
    print(f"    INS  before:{ancla_id} → {nuevo['data-id']}")


# ═══════════════════════════════════════════════════════════════════════════════
# CAMBIO 1 — Lyra: descripción correcta en seccion_02
# ID c64db16a: "lince de pelaje rojizo con manchas blancas" → gata montés
# ═══════════════════════════════════════════════════════════════════════════════

def cambio_lyra_descripcion(backup, dry_run):
    print("\n[1] Lyra descripcion — seccion_02")
    path, soup = cargar("seccion_02.html")

    modificar(soup, "c64db16a", """
<p class="texto-narrativo new-content"
   data-day="3" data-emotion="neutral" data-focus="lyra"
   data-intensity="1" data-location="camino" data-plot="setup"
   data-scene="05" data-tension="1" data-type="descripcion">
Desde una cresta elevada pudieron divisar un pequeño claro donde una gata montés de pelaje negro con manchas doradas trabajaba completamente absorta. Se acercaron con cuidado por el sendero serpenteante y la encontraron con pergaminos extendidos sobre una roca plana, una brújula especial de metal brillante, y las puntas de sus garras manchadas de tinta. Murmuraba para sí misma mientras trazaba líneas precisas.
</p>
""", dry_run)

    guardar(path, soup, backup, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CAMBIO 2+3 — Seccion_08: cuervos muestran imágenes + padre elige quedarse
# ═══════════════════════════════════════════════════════════════════════════════

def cambio_s08_cuervos(backup, dry_run):
    print("\n[2+3] Cuervos revelacion + padre — seccion_08")
    path, soup = cargar("seccion_08.html")

    # a6e204df: reemplazar declaración "Mantis de mentiras tejidas / Hermana..."
    # → descripción visual de plumas mostrando imágenes
    modificar(soup, "a6e204df", """
<p class="texto-narrativo"
   data-day="8" data-emotion="asombro" data-focus="cuervo-primario,seraphina"
   data-intensity="5" data-location="bosque-cuervos-espejo" data-plot="revelacion"
   data-scene="02" data-tension="5" data-type="descripcion"
   data-secret="true">
Las plumas del Cuervo Primario comenzaron a cambiar. No el reflejo plateado de antes —algo más profundo, como luz atrapada en agua oscura. Imágenes emergieron en la superficie de cada pluma con la nitidez de un recuerdo que nadie había pedido ver.
</p>
""", dry_run)

    # 65ad58a7: reemplazar narración de "6 gatos / hermana maldecida"
    # → Axel VE a su padre caer y reconoce el arco
    modificar(soup, "65ad58a7", """
<p class="texto-narrativo"
   data-day="8" data-emotion="shock" data-focus="axel,padre-axel"
   data-intensity="5" data-location="bosque-cuervos-espejo" data-plot="revelacion"
   data-reveals="Axel ve a su padre caer en el desfiladero y reconoce el arco"
   data-scene="02" data-tension="5" data-type="flashback"
   data-secret="true">
Axel las vio. No como visión borrosa sino con la claridad brutal de un recuerdo que no era suyo: un desfiladero nevado, una figura que reconoció por la postura antes de reconocer la cara, el arco élfico que ahora cargaba él mismo en el lomo. El destello de algo verde moviéndose entre las piedras. Su padre cayendo.
</p>
""", dry_run)

    # f5c0267b: reemplazar "El sexto fue Flecha Certera..." → solo "Lo que ves es verdad."
    modificar(soup, "f5c0267b", """
<p class="dialogo" data-badge="pronunciado sin elaboracion"
   data-day="8" data-emotion="neutral" data-focus="cuervo-primario"
   data-intensity="4" data-location="bosque-cuervos-espejo" data-plot="revelacion"
   data-scene="02" data-speaker="cuervo-primario" data-tension="5"
   data-to="axel" data-type="dialogo">
—Lo que ves es verdad—
</p>
""", dry_run)

    # 431209a4: reemplazar declaración de la red de 47 mantis
    # → descripción visual de lo que Axel percibe (no declaración explícita)
    modificar(soup, "431209a4", """
<p class="texto-narrativo"
   data-day="8" data-emotion="horror" data-focus="axel,seraphina"
   data-intensity="4" data-location="bosque-cuervos-espejo" data-plot="revelacion"
   data-scene="03" data-tension="5" data-type="introspeccion"
   data-secret="true">
Las plumas siguieron mostrando. Axel dejó de contar. No era un incidente aislado —era un patrón que se repetía con variaciones mínimas, cada iteración más refinada que la anterior, cada recuerdo de Seraphina impregnado de la misma mezcla de dolor y determinación que él había interpretado como desesperación.
</p>
""", dry_run)

    # NUEVO: padre eligiendo quedarse (después de la visión de él cayendo)
    # Insertar después de 65ad58a7 (la visión del padre cayendo)
    insertar_despues(soup, "65ad58a7", """
<p class="texto-narrativo"
   data-day="8" data-emotion="asombro" data-focus="padre-axel,axel"
   data-intensity="4" data-location="bosque-cuervos-espejo" data-plot="revelacion"
   data-reveals="El padre de Axel eligio quedarse voluntariamente, no murio"
   data-scene="02" data-tension="4" data-type="flashback">
Las imágenes continuaron. Su padre en el suelo del desfiladero, herido pero no muerto. El arco a un lado. Una mantis observando desde las piedras. Y entonces algo que Axel no esperaba: la figura incorporándose lentamente, mirando hacia el norte —hacia las montañas, hacia el Templo— recogiendo el arco y dejándolo sobre la piedra de forma deliberada, visible, recuperable, antes de alejarse. Sin que lo obligaran. Eligiendo.
</p>
""", dry_run)

    guardar(path, soup, backup, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CAMBIO 4 — Seccion_09B: confesión voluntaria de Seraphina
# ═══════════════════════════════════════════════════════════════════════════════

def cambio_s09b_confesion(backup, dry_run):
    print("\n[4] Confesion Seraphina — seccion_09B")
    path, soup = cargar("seccion_09B.html")

    # Insertar después de c8df6a04 (Seraphina: "Hay más... Llevo diez días...")
    # y antes de a1a549ff (Axel: "Entonces mañana descubrimos la verdad")
    insertar_despues(soup, "c8df6a04", """
<p class="dialogo" data-badge="dicho sin mirar el fuego"
   data-day="10" data-emotion="culpa" data-focus="seraphina"
   data-intensity="5" data-location="campamento" data-plot="revelacion"
   data-reveals="La madre de Seraphina estuvo presente, el padre de Axel cayo primero, el mago maldijo a la madre"
   data-scene="03" data-speaker="seraphina" data-tension="4"
   data-to="axel" data-type="dialogo" data-secret="false">
—Mi madre fue conmigo— dijo Seraphina. No fue declaración. Fue la clase de frase que se dice cuando ya no queda energía para protegerla. —Estaba ahí cuando tu padre cayó. No tenía que estarlo. Era yo quien había llevado a tu padre hasta el desfiladero, pero ella insistió en acompañarme.— Sus antenas no se movieron. —El mago que los acompañaba la maldijo antes de huir. No a mí. A ella. La maldición no fue consecuencia del accidente —fue una decisión de alguien que quería asegurarse de que yo tuviera algo que perder.— Pausa larga. —Llevamos meses huyendo antes de que llegara hasta ti. Primero buscando la cura. Luego intentando ganar tiempo para encontrarla.
</p>
""", dry_run)

    guardar(path, soup, backup, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CAMBIO 5 — Seccion_10: 3 momentos de Umbra + resolución
# ═══════════════════════════════════════════════════════════════════════════════

def cambio_umbra_s10(backup, dry_run):
    print("\n[5] Umbra momentos — seccion_10")
    path, soup = cargar("seccion_10.html")

    # Momento 1: indecisión con Vex (sc=02, después de bc5f3012)
    # bc5f3012: "Vex lo estudió durante tres segundos. Luego sonrió..."
    insertar_despues(soup, "bc5f3012", """
<p class="texto-narrativo"
   data-day="10" data-emotion="indecision" data-focus="axel,umbra"
   data-intensity="3" data-location="templo-celestial" data-plot="desarrollo"
   data-scene="02" data-tension="4" data-type="introspeccion">
Umbra aprovechó el instante de vacilación —el segundo entre tensar el arco y decidir hacia dónde apuntarlo.

—Ahora. Mientras Vex la distrae. Termina lo que ella empezó antes de que sea más complicado.

Axel bajó el arco un centímetro. Luego lo volvió a subir. El suelo del Templo —piedra lunar, siglos de uso sagrado— pareció absorber algo de la voz antes de que llegara a convertirse en acción. Umbra lo intentó de nuevo y encontró más resistencia de lo esperado.
</p>
""", dry_run)

    # Momento 2: cuando el padre se debilita (sc=03, después de 0a8896a2)
    # 0a8896a2: "El esfuerzo se le notó. La figura del padre parpadeó, se adelgazó..."
    insertar_despues(soup, "0a8896a2", """
<p class="texto-narrativo"
   data-day="10" data-emotion="dolor" data-focus="axel,umbra,padre-axel"
   data-intensity="4" data-location="templo-celestial" data-plot="desarrollo"
   data-scene="03" data-tension="5" data-type="introspeccion">
Umbra surgió con la claridad de siempre en el peor momento posible.

—Ella lo desgastó. Llevó a tu padre hasta aquí igual que te llevó a ti. Deja que caiga. Es lo que merece.

Axel apretó la cuerda del arco hasta que el cuero le marcó la palma. No. Apretó más fuerte todavía. El suelo sagrado filtró parte de la voz, pero no toda —el Templo luchaba contra siglos de resentimiento acumulado y el resultado era imperfecto. Umbra retrocedió. No desapareció.
</p>
""", dry_run)

    # Momento 3 + resolución: cuando el arco arde (sc=06, después de aaf8de83)
    # aaf8de83: "Se giró hacia Axel. El arco ardía con tanta intensidad que Axel tuvo que sostenerlo..."
    insertar_despues(soup, "aaf8de83", """
<p class="texto-narrativo"
   data-day="10" data-emotion="determinacion" data-focus="axel,umbra"
   data-intensity="5" data-location="templo-celestial" data-plot="resolucion"
   data-scene="06" data-tension="4" data-type="introspeccion">
El arco ardía. Umbra intentó hablar por última vez y encontró que las palabras no llegaban —el Templo las absorbía antes de que tomaran forma, la piedra lunar actuando como filtro sobre todo lo que no pertenecía a ese lugar. Axel esperó. La voz no volvió. Sostuvo el arco más tiempo del necesario, buscando el filo familiar de la duda, el comentario lateral, la insinuación. Nada. Solo el peso de la madera ancestral en sus manos y el silencio que ese peso siempre había merecido.
</p>
""", dry_run)

    guardar(path, soup, backup, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CAMBIO 6 — Luna Platino: 1 línea en secciones 02, 06, 08C
# ═══════════════════════════════════════════════════════════════════════════════

def cambio_luna_platino(backup, dry_run):
    print("\n[6] Luna Platino foreshadowing")

    # --- Seccion 02 ---
    # Después de 2803cb92 (Lyra trazando ruta alternativa)
    print("  seccion_02")
    path, soup = cargar("seccion_02.html")
    insertar_despues(soup, "2803cb92", """
<p class="texto-narrativo"
   data-day="3" data-emotion="nostalgia" data-focus="lyra"
   data-intensity="2" data-location="camino" data-plot="foreshadowing"
   data-scene="05" data-tension="1" data-type="introspeccion">
Mientras trazaba, la mano de Lyra se detuvo sobre un punto del mapa sin nombre. Sus dedos lo cubrieron antes de que Axel pudiera leerlo. Cuando levantó la vista, lo que había en sus ojos no era el humor cartográfico de antes —era algo más antiguo, más quieto, que desapareció en el momento en que se dio cuenta de que él la miraba.
</p>
""", dry_run)
    guardar(path, soup, backup, dry_run)

    # --- Seccion 06 ---
    # Después de 9be7b256 (la encontraron sentada sobre formación rocosa)
    print("  seccion_06")
    path, soup = cargar("seccion_06.html")
    insertar_despues(soup, "9be7b256", """
<p class="texto-narrativo"
   data-day="6" data-emotion="tristeza" data-focus="lyra"
   data-intensity="2" data-location="cuevas-brillantes" data-plot="foreshadowing"
   data-scene="06" data-tension="1" data-type="introspeccion">
Había algo en la forma en que Lyra miraba el horizonte antes de que llegaran —un peso detrás de la concentración profesional, como alguien que rastrea en un paisaje que ya conoce demasiado bien y por eso duele. Lo perdió cuando los vio acercarse. La cartógrafa reemplazó a la otra sin pausa visible.
</p>
""", dry_run)
    guardar(path, soup, backup, dry_run)

    # --- Seccion 08C ---
    # Después de 9ff4cd9e (Axel tomó el mensaje, resina olía a pino)
    print("  seccion_08C")
    path, soup = cargar("seccion_08C.html")
    insertar_despues(soup, "9ff4cd9e", """
<p class="texto-narrativo"
   data-day="9" data-emotion="tristeza" data-focus="lyra"
   data-intensity="2" data-location="valle-mariposas" data-plot="foreshadowing"
   data-scene="07" data-tension="1" data-type="introspeccion">
Axel notó que Lyra leía el mensaje por encima de su hombro antes de apartar la vista. Tocó una cicatriz que llevaba en el costado izquierdo —un gesto que duró menos de un segundo y que no repitió. —Alguien que habría querido saber que eres de los que reciben mensajes así— dijo, casi sin voz, sin aclarar a quién se refería ni completar la frase.
</p>
""", dry_run)
    guardar(path, soup, backup, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CAMBIO 7 — Flauta de Ember: entrega en 09, resonancia en 10
# ═══════════════════════════════════════════════════════════════════════════════

def cambio_flauta(backup, dry_run):
    print("\n[7] Flauta de Ember")

    # Seccion 09: Ember entrega la flauta durante el abrazo
    # Después de 194221c2 (Con Axel fue distinto: los hermanos se abrazaron)
    print("  seccion_09 — entrega")
    path, soup = cargar("seccion_09.html")
    insertar_despues(soup, "194221c2", """
<p class="texto-narrativo"
   data-day="9" data-emotion="ternura" data-focus="ember,axel"
   data-intensity="3" data-location="camino" data-plot="setup"
   data-reveals="Ember entrega la flauta elfica a Axel"
   data-scene="04" data-tension="1" data-type="accion"
   data-relationship="axel-ember" data-rel-direction="positiva">
Antes de soltarlo, Ember metió la mano en su bolsa y sacó la flauta élfica. La madera tenía el mismo lustre antiguo que el arco de Axel —la misma procedencia, la misma mano que la talló décadas atrás.
</p>
""", dry_run)
    insertar_despues(soup, "194221c2", """
<p class="dialogo" data-badge="dicho con la voz de quien no improvisa estas cosas"
   data-day="9" data-emotion="ternura" data-focus="ember"
   data-intensity="3" data-location="camino" data-plot="setup"
   data-scene="04" data-speaker="ember" data-tension="1"
   data-to="axel" data-type="dialogo"
   data-relationship="axel-ember" data-rel-direction="positiva">
—Llévala tú— dijo. —No sé si voy a necesitarla donde voy. Pero siento que tú sí.
</p>
""", dry_run)
    guardar(path, soup, backup, dry_run)

    # Seccion 10: la flauta resuena sola cuando el padre aparece
    # Después de c7297eb3 (padre-axel: —Axel.)
    print("  seccion_10 — resonancia")
    path, soup = cargar("seccion_10.html")
    insertar_despues(soup, "c7297eb3", """
<p class="texto-narrativo"
   data-day="10" data-emotion="asombro" data-focus="padre-axel,axel,arco"
   data-intensity="3" data-location="templo-celestial" data-plot="payoff"
   data-reveals="La flauta de Ember resuena sola al reconocer al padre — el arco y la flauta se reconocen"
   data-scene="01" data-tension="2" data-type="descripcion">
La flauta en el lomo de Axel resonó. Una sola nota —no tocada, no intencionada— que el Templo amplificó hasta hacerla visible como vibración en el aire. El arco respondió al instante con el mismo tono. Dos instrumentos de la misma madera, en el mismo espacio, reconociéndose después de años separados.
</p>
""", dry_run)
    guardar(path, soup, backup, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CAMBIO 8 — Búho archivo: inscripción en seccion_09A
# ═══════════════════════════════════════════════════════════════════════════════

def cambio_buho_s09a(backup, dry_run):
    print("\n[8] Buho archivo — seccion_09A")
    path, soup = cargar("seccion_09A.html")

    # Después de e79a3a5d (Groundbreaker: "El guardián que encontrarán lleva aproximadam...")
    insertar_despues(soup, "e79a3a5d", """
<p class="texto-narrativo"
   data-day="10" data-emotion="asombro" data-focus="axel,groundbreaker,padre-axel"
   data-intensity="2" data-location="laberinto-tejones" data-plot="payoff"
   data-reveals="El buho archivo registro el paso del padre de Axel hace 3 años"
   data-scene="08" data-tension="2" data-type="descripcion">
Groundbreaker señaló una inscripción en la pared del túnel —un símbolo circular con marcas de vuelo talladas en la piedra con precisión no tejonera.
</p>
""", dry_run)
    insertar_despues(soup, "e79a3a5d", """
<p class="dialogo" data-badge="reportado como dato estructural"
   data-day="10" data-emotion="neutral" data-focus="groundbreaker"
   data-intensity="2" data-location="laberinto-tejones" data-plot="payoff"
   data-scene="08" data-speaker="groundbreaker" data-tension="2"
   data-to="axel" data-type="dialogo">
—El archivo del bosque confirmó su paso hace aproximadamente tres años. La criatura que llevaba ese símbolo cruzó esta ruta. Dejó registro. Los archivos de búho son meticulosos en ese sentido.
</p>
""", dry_run)
    insertar_despues(soup, "e79a3a5d", """
<p class="texto-narrativo"
   data-day="10" data-emotion="nostalgia" data-focus="axel,padre-axel"
   data-intensity="3" data-location="laberinto-tejones" data-plot="payoff"
   data-scene="08" data-tension="2" data-type="introspeccion">
Axel miró el símbolo. Era el mismo que Problemas trazaba en la madera cuando creía que nadie lo observaba.
</p>
""", dry_run)

    guardar(path, soup, backup, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# CAMBIO 9 — Eco Pergaminada: mensaje vía mariposas en seccion_09
# ═══════════════════════════════════════════════════════════════════════════════

def cambio_eco_s09(backup, dry_run):
    print("\n[9] Eco Pergaminada mensaje — seccion_09")
    path, soup = cargar("seccion_09.html")

    # Después de bbb83fcd (Axel miró a Lyra / Lyra miraba el ángulo de la entrada)
    insertar_despues(soup, "bbb83fcd", """
<p class="texto-narrativo"
   data-day="9" data-emotion="alivio" data-focus="eco-pergaminada,axel,lyra"
   data-intensity="2" data-location="laberinto-tejones" data-plot="payoff"
   data-reveals="Eco destruyo el mapa de piel y entrego el cristal de memoria a archivos neutrales"
   data-scene="06" data-tension="2" data-type="accion">
Una mariposa de alas translúcidas aterrizó en el hombro de Axel. Llevaba un mensaje sellado con resina de árbol —el sello de Eco Pergaminada, inconfundible.
</p>
""", dry_run)
    insertar_despues(soup, "bbb83fcd", """
<p class="dialogo" data-badge="leido en voz baja por Axel"
   data-day="9" data-emotion="alivio" data-focus="eco-pergaminada"
   data-intensity="2" data-location="laberinto-tejones" data-plot="payoff"
   data-scene="06" data-speaker="eco-pergaminada" data-tension="2"
   data-to="axel" data-type="dialogo">
—Cristal de memoria entregado a archivos neutrales. Mapa de piel destruido antes de que llegaran a mí. La ruta al Templo no está en ningún registro que puedan encontrar. Eco.—
</p>
""", dry_run)
    insertar_despues(soup, "bbb83fcd", """
<p class="dialogo" data-badge="dicho con algo que en otra persona habría sido alivio"
   data-day="9" data-emotion="alivio" data-focus="lyra"
   data-intensity="2" data-location="laberinto-tejones" data-plot="payoff"
   data-scene="06" data-speaker="lyra" data-tension="2"
   data-to="grupo" data-type="dialogo">
—Eficiente— dijo Lyra, sin levantar los ojos del mapa.
</p>
""", dry_run)

    guardar(path, soup, backup, dry_run)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Aplica cambios de backstory v1")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup", action="store_true")
    args = parser.parse_args()

    modo = "[DRY RUN]" if args.dry_run else "[APLICANDO]"
    print(f"\n{modo} apply_backstory_v1.py")
    print("=" * 50)

    cambio_lyra_descripcion(args.backup, args.dry_run)
    cambio_s08_cuervos(args.backup, args.dry_run)
    cambio_s09b_confesion(args.backup, args.dry_run)
    cambio_umbra_s10(args.backup, args.dry_run)
    cambio_luna_platino(args.backup, args.dry_run)
    cambio_flauta(args.backup, args.dry_run)
    cambio_buho_s09a(args.backup, args.dry_run)
    cambio_eco_s09(args.backup, args.dry_run)

    print("\n" + "=" * 50)
    if args.dry_run:
        print("DRY RUN completado — ningun archivo fue modificado.\n")
    else:
        print("Cambios aplicados.\n")


if __name__ == "__main__":
    main()
