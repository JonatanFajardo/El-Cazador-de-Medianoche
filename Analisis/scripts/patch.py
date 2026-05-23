"""
patch.py — Aplica los cambios del archivo temporal a los HTMLs originales.

Busca párrafos por data-id (huella primaria) o por fingerprint clásico (fallback).
Soporta inserciones: párrafos con data-id="NEW" se insertan usando data-after o data-before.

Uso:
    python patch.py                          # usa story_temp.html por default
    python patch.py --input mi_contexto.html
    python patch.py --input story_temp.html --dry-run
    python patch.py --input story_temp.html --backup

Convención para párrafos NUEVOS (añadidos por la IA):
    <p class="dialogo" data-id="NEW" data-after="a3f2b1c4" ...>contenido nuevo</p>
    <p class="texto-narrativo" data-id="NEW" data-before="9e17d042" ...>contenido nuevo</p>

Convención para párrafos a ELIMINAR:
    <p data-id="ec73e141" data-delete="true"></p>
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString


def timestamp_ahora():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

CLASES = ["dialogo", "texto-narrativo"]


# ── Huella clásica (fallback si no hay data-id) ──────────────────────────────

def construir_huella(tag):
    partes = []
    for attr in ["data-day", "data-scene", "data-type", "data-focus", "data-speaker"]:
        v = tag.get(attr)
        if v:
            partes.append(f"{attr}={v}")
    texto = tag.get_text(strip=True)[:60]
    partes.append(f"texto={texto}")
    return "|".join(partes)


# ── Índices del archivo original ─────────────────────────────────────────────

def indexar_original(soup):
    """Retorna dos dicts: {data-id: tag} y {huella: tag}, y un dict {texto: tag}."""
    por_id = {}
    por_huella = {}
    por_texto = {}
    for tag in soup.find_all("p", class_=CLASES):
        pid = tag.get("data-id")
        if pid and pid != "NEW":
            por_id[pid] = tag
        huella = construir_huella(tag)
        por_huella[huella] = tag
        texto = tag.get_text(strip=True)
        if texto:
            por_texto[texto] = tag
    return por_id, por_huella, por_texto


# ── Aplicar cambios a un archivo ─────────────────────────────────────────────

def aplicar_cambios(html_path, parrafos_nuevos, dry_run=False, backup=False, force=False):
    """
    Procesa la lista de párrafos del story_temp.
    Retorna (modificados, insertados, no_encontrados, nuevos_ids).
    nuevos_ids: lista de UUIDs asignados a los NEW, en orden de aparición.
    """
    content = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(content, "html.parser")
    por_id, por_huella, por_texto = indexar_original(soup)

    modificados = []
    insertados = []
    no_encontrados = []
    nuevos_ids = []  # UUIDs asignados a NEW, en orden
    ultimo_after = {}  # ancla_id -> tag más reciente insertado after ella (para cadenas)

    for tag_nuevo in parrafos_nuevos:
        pid = tag_nuevo.get("data-id", "")

        # ── ELIMINACIÓN ──────────────────────────────────────────────────────
        if tag_nuevo.get("data-delete") == "true":
            if pid and pid in por_id:
                tag_original = por_id[pid]
                if not dry_run:
                    tag_original.decompose()
                modificados.append({
                    "metodo": "DELETE",
                    "id": pid,
                    "antes": str(tag_original)[:120],
                    "despues": "(eliminado)",
                })
            else:
                no_encontrados.append(f"DELETE sin data-id válido: '{pid}'")
            continue

        # ── INSERCIÓN ────────────────────────────────────────────────────────
        if pid == "NEW":
            ancla_id = tag_nuevo.get("data-after") or tag_nuevo.get("data-before")
            modo_insercion = "after" if tag_nuevo.get("data-after") else "before"

            if not ancla_id or ancla_id not in por_id:
                no_encontrados.append(f"NEW sin ancla válida (data-after/before='{ancla_id}')")
                continue

            # Evitar duplicados: si el texto ya existe, reemplazar en lugar de insertar
            texto_nuevo = tag_nuevo.get_text(strip=True)
            if texto_nuevo and texto_nuevo in por_texto:
                tag_existente = por_texto[texto_nuevo]
                # Construir tag_limpio para el reemplazo
                tag_para_reemplazar = BeautifulSoup(str(tag_nuevo), "html.parser").find("p")
                del tag_para_reemplazar["data-id"]
                if tag_para_reemplazar.get("data-after"):
                    del tag_para_reemplazar["data-after"]
                if tag_para_reemplazar.get("data-before"):
                    del tag_para_reemplazar["data-before"]
                tag_para_reemplazar["data-id"] = tag_existente.get("data-id", "")
                if str(tag_existente) != str(tag_para_reemplazar) and not dry_run:
                    if tag_existente.parent is not None:
                        tag_existente.replace_with(tag_para_reemplazar)
                modificados.append({
                    "metodo": "texto-duplicado",
                    "id": tag_existente.get("data-id", "?"),
                    "antes": str(tag_existente)[:120],
                    "despues": str(tag_para_reemplazar)[:120],
                })
                continue

            # Para inserciones "after" consecutivas en la misma ancla,
            # usar el último tag insertado como ancla real para mantener el orden
            if modo_insercion == "after" and ancla_id in ultimo_after:
                ancla_tag = ultimo_after[ancla_id]
            else:
                ancla_tag = por_id[ancla_id]

            # Limpiar atributos de navegación antes de insertar
            tag_limpio = BeautifulSoup(str(tag_nuevo), "html.parser").find("p")
            del tag_limpio["data-id"]
            if tag_limpio.get("data-after"):
                del tag_limpio["data-after"]
            if tag_limpio.get("data-before"):
                del tag_limpio["data-before"]

            # Asignar nuevo data-id único y marcar como nuevo
            import uuid
            new_uuid = uuid.uuid4().hex[:8]
            tag_limpio["data-id"] = new_uuid
            tag_limpio["data-status"] = "new"
            tag_limpio["data-updated"] = timestamp_ahora()
            nuevos_ids.append(new_uuid)

            if not dry_run:
                if modo_insercion == "after":
                    ancla_tag.insert_after(NavigableString("\n          "))
                    ancla_tag.insert_after(tag_limpio)
                    ultimo_after[ancla_id] = tag_limpio  # próximo NEW usa este como ancla
                else:
                    ancla_tag.insert_before(tag_limpio)
                    ancla_tag.insert_before(NavigableString("\n          "))

            insertados.append({
                "ancla": ancla_id,
                "modo": modo_insercion,
                "preview": str(tag_limpio)[:100],
                "new_uuid": new_uuid,
            })
            continue

        # ── MODIFICACIÓN por data-id ─────────────────────────────────────────
        if pid and pid in por_id:
            tag_original = por_id[pid]
            if tag_original.parent is None:
                continue  # Ya fue removido/reemplazado en esta sesión
            # Comparar solo texto: en modo --minimal el original tiene más atributos
            texto_original = tag_original.decode_contents()
            texto_entrante = tag_nuevo.decode_contents()
            if texto_original == texto_entrante:
                if force and not dry_run:
                    tag_original["data-status"] = "modified"
                    tag_original["data-updated"] = timestamp_ahora()
                    modificados.append({
                        "metodo": "force-stamp",
                        "id": pid,
                        "antes": str(tag_original)[:120],
                        "despues": str(tag_original)[:120],
                    })
                continue
            antes = str(tag_original)[:120]
            if not dry_run:
                tag_original.clear()
                for child in BeautifulSoup(texto_entrante, "html.parser").contents:
                    tag_original.append(child.__copy__() if hasattr(child, "__copy__") else NavigableString(str(child)))
                tag_original["data-status"] = "modified"
                tag_original["data-updated"] = timestamp_ahora()
            modificados.append({
                "metodo": "data-id",
                "id": pid,
                "antes": antes,
                "despues": str(tag_original)[:120],
            })
            continue

        # ── MODIFICACIÓN por huella clásica (fallback) ───────────────────────
        huella = construir_huella(tag_nuevo)
        if huella in por_huella:
            tag_original = por_huella[huella]
            if tag_original.parent is None:
                continue  # Ya fue removido/reemplazado en esta sesión
            if str(tag_original) == str(tag_nuevo):
                continue
            if not dry_run:
                tag_clon = BeautifulSoup(str(tag_nuevo), "html.parser").find("p")
                tag_clon["data-status"] = "modified"
                tag_clon["data-updated"] = timestamp_ahora()
                tag_original.replace_with(tag_clon)
            modificados.append({
                "metodo": "huella",
                "id": huella[:60],
                "antes": str(tag_original)[:120],
                "despues": str(tag_nuevo)[:120],
            })
            continue

        # ── NO ENCONTRADO ────────────────────────────────────────────────────
        no_encontrados.append(pid or huella[:60])

    if not dry_run and (modificados or insertados):
        if backup:
            shutil.copy(html_path, str(html_path) + ".bak")
            print(f"   Backup: {html_path.name}.bak")
        html_path.write_text(str(soup), encoding="utf-8")

    return modificados, insertados, no_encontrados, nuevos_ids


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Aplica cambios del HTML temporal a los archivos originales"
    )
    parser.add_argument("--input", default="story_temp.html")
    parser.add_argument("--secciones", default="../../secciones")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--force", action="store_true",
        help="Fuerza data-status=modified y data-updated en parrafos del story_temp aunque el texto no haya cambiado")
    parser.add_argument("--stamp", metavar="SECCION",
        help="Marca todos los parrafos sin data-updated de una seccion como 'original'. Ej: seccion_01.html")
    args = parser.parse_args()

    # ── MODO STAMP ───────────────────────────────────────────────────────────
    if args.stamp:
        carpeta = Path(args.secciones)
        html_path = carpeta / args.stamp
        if not html_path.exists():
            print(f"No existe: {html_path.resolve()}")
            return
        content = html_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        ts = timestamp_ahora()
        count = 0
        for tag in soup.find_all("p", class_=CLASES):
            if not tag.get("data-updated"):
                tag["data-status"] = "original"
                tag["data-updated"] = ts
                count += 1
        html_path.write_text(str(soup), encoding="utf-8")
        print(f"\n[STAMP] {args.stamp}: {count} parrafos marcados como 'original' ({ts})\n")
        return

    input_path = Path(args.input)
    carpeta = Path(args.secciones)

    if not input_path.exists():
        print(f"No se encontro: {input_path.resolve()}")
        return

    modo = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{modo}Aplicando cambios desde: {input_path.name}")
    print(f"  Secciones en: {carpeta.resolve()}\n")

    soup_temp = BeautifulSoup(input_path.read_text(encoding="utf-8"), "html.parser")

    # Agrupar párrafos por sección de origen
    por_seccion = {}
    for section in soup_temp.find_all("section"):
        origen = section.get("data-source")
        if not origen:
            continue
        parrafos = section.find_all("p", class_=CLASES)
        eliminaciones = section.find_all("p", attrs={"data-delete": "true"})
        todos = parrafos + [e for e in eliminaciones if e not in parrafos]
        if todos:
            por_seccion.setdefault(origen, []).extend(todos)

    if not por_seccion:
        print("No se encontraron <section data-source='...'> en el archivo temporal.")
        return

    total_mod = 0
    total_ins = 0
    total_nf = 0

    for seccion, parrafos in sorted(por_seccion.items()):
        html_path = carpeta / seccion
        if not html_path.exists():
            print(f"  No existe: {html_path}")
            continue

        mod, ins, nf, nuevos_ids = aplicar_cambios(
            html_path, parrafos, dry_run=args.dry_run, backup=args.backup, force=args.force
        )

        if mod or ins or nf:
            print(f"  {seccion}")
            for m in mod:
                tag = "[DRY]" if args.dry_run else "EDIT"
                print(f"    {tag} [{m['metodo']}] {m['id'][:40]}")
                print(f"         ANTES  : {m['antes'][:90]}")
                print(f"         DESPUES: {m['despues'][:90]}")
            for i in ins:
                tag = "[DRY]" if args.dry_run else "INSERT"
                print(f"    {tag} {i['modo'].upper()} {i['ancla']} -> {i['preview'][:70]}")
            for h in nf:
                print(f"    NO ENCONTRADO: {h[:70]}")
        else:
            print(f"  OK  {seccion}")

        total_mod += len(mod)
        total_ins += len(ins)
        total_nf += len(nf)

    print(f"\n{modo}Resumen:")
    print(f"  Modificados   : {total_mod}")
    print(f"  Insertados    : {total_ins}")
    print(f"  No encontrados: {total_nf}\n")



if __name__ == "__main__":
    main()
