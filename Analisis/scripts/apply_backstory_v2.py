"""
apply_backstory_v2.py — Correcciones de descripción de Lyra
Reemplaza referencias "lince" → "gata montés" en párrafos identificados.
Soporta --dry-run y --backup.

Uso:
    python apply_backstory_v2.py
    python apply_backstory_v2.py --dry-run
    python apply_backstory_v2.py --backup
"""
import sys
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

DRY_RUN = "--dry-run" in sys.argv
BACKUP = "--backup" in sys.argv

SECCIONES = Path(__file__).parent.parent.parent / "secciones"

# Cambios: (data-id, texto_viejo, texto_nuevo, descripcion)
CAMBIOS = [
    (
        "3d5aa0b6",
        "La lince lo miró con la ceja levantada y la boca torcida en algo que no era del todo una sonrisa.",
        "La gata montés lo miró con la ceja levantada y la boca torcida en algo que no era del todo una sonrisa.",
        "sec02: 'La lince' → 'La gata montés'"
    ),
    (
        "55d7efd4",
        "la lince comenzó a recoger sus pergaminos manchados.",
        "la gata montés comenzó a recoger sus pergaminos manchados.",
        "sec02: 'la lince comenzó' → 'la gata montés comenzó'"
    ),
    (
        "15d6abba",
        "La lince se volteó.",
        "La gata montés se volteó.",
        "sec04: 'La lince se volteó' → 'La gata montés se volteó'"
    ),
    (
        "03a6dd3e",
        "esa lince cartógrafa,",
        "esa gata montés cartógrafa,",
        "sec07A: 'esa lince cartógrafa' → 'esa gata montés cartógrafa'"
    ),
    (
        "aef46199",
        "La cartógrafa lince no",
        "La cartógrafa gata montés no",
        "sec07A: 'La cartógrafa lince' → 'La cartógrafa gata montés'"
    ),
    (
        "431d0819",
        "esa cartógrafa lince que",
        "esa cartógrafa gata montés que",
        "sec07A: 'esa cartógrafa lince' → 'esa cartógrafa gata montés'"
    ),
]


def aplicar(secciones_dir: Path):
    # Indexar todos los párrafos por data-id a través de todos los HTMLs
    idx = {}  # data-id -> (Path, tag, soup)
    archivos = {}  # Path -> soup

    for html in sorted(secciones_dir.glob("seccion_*.html")):
        content = html.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        archivos[html] = soup
        for p in soup.find_all("p"):
            did = p.get("data-id")
            if did:
                idx[did] = (html, p, soup)

    modificados = 0
    no_encontrados = []

    for did, viejo, nuevo, desc in CAMBIOS:
        if did not in idx:
            print(f"  NO ENCONTRADO [{did}] — {desc}")
            no_encontrados.append(did)
            continue

        html_path, tag, soup = idx[did]
        html_text = str(tag)

        if viejo not in html_text:
            # Intento parcial: buscar en texto del tag
            tag_txt = tag.get_text()
            if viejo not in tag_txt:
                print(f"  TEXTO NO COINCIDE [{did}] — {desc}")
                print(f"    Esperado: {viejo!r}")
                print(f"    Actual:   {tag_txt[:100]!r}")
                no_encontrados.append(did)
                continue

        if DRY_RUN:
            print(f"  [DRY-RUN] MOD [{did}] — {desc}")
            modificados += 1
            continue

        # Aplicar: reemplazar en el HTML serializado del tag
        nuevo_html = html_text.replace(viejo, nuevo, 1)
        nuevo_tag = BeautifulSoup(nuevo_html, "html.parser").find("p")
        tag.replace_with(nuevo_tag)
        print(f"  MOD [{did}] — {desc}")
        modificados += 1

    if not DRY_RUN and modificados > 0:
        # Guardar archivos modificados
        archivos_modificados = set()
        for did, _, _, _ in CAMBIOS:
            if did in idx:
                archivos_modificados.add(idx[did][0])

        for html_path in archivos_modificados:
            if BACKUP:
                bak = html_path.with_suffix(".html.bak3")
                shutil.copy2(html_path, bak)
                print(f"  Backup: {bak.name}")
            soup = archivos[html_path]
            html_path.write_text(str(soup), encoding="utf-8")
            print(f"  Guardado: {html_path.name}")

    print(f"\nResumen: {modificados} modificados, {len(no_encontrados)} no encontrados")
    if no_encontrados:
        print(f"  No encontrados: {no_encontrados}")


if __name__ == "__main__":
    print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Aplicando correcciones de descripcion de Lyra...")
    aplicar(SECCIONES)
