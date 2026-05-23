import re

def detectar_gerundios_peligrosos(texto):
    patron = r',\s+(\w+(?:ando|iendo))'
    matches = re.finditer(patron, texto.lower())

    resultados = []
    
    for match in matches:
        gerundio = match.group(1)
        resultados.append(f"🚨 Gerundio sospechoso después de coma: '{gerundio}'")

    if not resultados:
        return "✔️ No se detectaron gerundios problemáticos."
    
    return "\n".join(resultados)


if __name__ == "__main__":
    with open("seccion_01.html", "r", encoding="utf-8") as f:
        texto = f.read()

    print(detectar_gerundios_peligrosos(texto))