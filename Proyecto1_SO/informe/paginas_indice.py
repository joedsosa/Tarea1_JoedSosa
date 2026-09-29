"""Busca en el PDF la pagina de cada titulo del indice y la guarda en paginas.json."""
import json, os, sys, unicodedata
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
titulos = json.load(open(os.path.join(BASE, ".titulos.json"), encoding="utf-8"))
doc = pymupdf.open(sys.argv[1])

def norm(t):
    return " ".join(unicodedata.normalize("NFC", t).split())

paginas, desde = {}, 2  # la busqueda empieza despues de la portada e indice
textos = [norm(p.get_text()) for p in doc]
indice_fin = next(i for i, t in enumerate(textos) if i > 0 and titulos[0] in t and "Índice" not in t)
desde = indice_fin
for k, t in enumerate(titulos):
    for i in range(desde, len(doc)):
        lineas = [norm(l) for l in doc[i].get_text().split("\n")]
        if norm(t) in lineas or any(l.startswith(norm(t)[:40]) for l in lineas if len(norm(t)) > 40):
            paginas[str(k)] = i + 1
            desde = i
            break
json.dump(paginas, open(os.path.join(BASE, "paginas.json"), "w"), indent=1)
print(paginas, len(paginas), "de", len(titulos))
