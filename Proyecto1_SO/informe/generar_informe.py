"""
Construye Informe_Proyecto1_SO.docx con la portada del laboratorio anterior,
las capturas tomadas en Windows (carpeta capturas/) y los CSV de
../resultados_windows.

Uso:  python3 generar_informe.py <plantilla_con_portada.docx> [paginas.json]

Formato: Times New Roman 12, interlineado 1.5, titulos en negrita 14, sin pie
de pagina, indice automatico de Word y referencias en formato APA.
El segundo argumento (opcional) trae los numeros de pagina de cada titulo
para rellenar el indice; se obtiene con paginas_indice.py.
"""
import csv, json, os, re, sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, "..", "resultados_windows")
CAP = os.path.join(BASE, "capturas")
IMG = os.path.join(BASE, "img")
SALIDA = os.path.join(BASE, "Informe_Proyecto1_SO.docx")

FUENTE = "Times New Roman"
NEGRO = RGBColor(0, 0, 0)
ANCHO_TEXTO = 15.5  # cm disponibles entre margenes

PAGINAS = {}
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
    PAGINAS = json.load(open(sys.argv[2], encoding="utf-8"))

# ----------------------------------------------------------------------------
# Datos medidos en la computadora del estudiante
# ----------------------------------------------------------------------------
def leer_csv(nombre):
    with open(os.path.join(RES, nombre)) as f:
        return {int(float(r["N"])): {k: float(v) for k, v in r.items()} for r in csv.DictReader(f)}

M8, M2, M1 = leer_csv("resultados.csv"), leer_csv("r_2nucleos.csv"), leer_csv("r_1nucleo.csv")
TAMANOS = sorted(M8)

def ent(x):
    return f"{int(round(x)):,}"

def ms(x):
    return f"{x:,.3f}"

def fuente_java(nombre):
    with open(os.path.join(RES, nombre), encoding="utf-8") as f:
        return f.read().strip("\n")

# ----------------------------------------------------------------------------
# Portada: se conserva y solo se cambia el titulo
# ----------------------------------------------------------------------------
doc = Document(sys.argv[1])
body = doc.element.body

for t in body.iter(qn("w:t")):
    if t.text == "Laboratorio ":
        t.text = "Proyecto "
    elif t.text == "Pthreads":
        t.text = "#1"
    elif t.text == "Semana: ":
        t.text = "Programación concurrente"
for p in body.iter(qn("w:p")):
    ts = list(p.iter(qn("w:t")))
    for i, t in enumerate(ts):
        if t.text == "Programación concurrente" and i + 1 < len(ts) and ts[i + 1].text.strip().isdigit():
            ts[i + 1].text = ""

# Fecha de entrega: la de hoy
for p in body.iter(qn("w:p")):
    ts = list(p.iter(qn("w:t")))
    if "".join(t.text or "" for t in ts).strip() == "15 de agosto de 2026":
        ts[0].text = "29 de septiembre de 2026"
        for t in ts[1:]:
            t.text = ""

hijos = list(body)
corte = next(i for i, el in enumerate(hijos) if el.tag == qn("w:p")
             and "".join(t.text or "" for t in el.iter(qn("w:t"))).startswith("Parte 1"))
for el in hijos[corte:]:
    if el.tag != qn("w:sectPr"):
        body.remove(el)

usados = set(re.findall(r'r:(?:embed|id)="([^"]+)"', body.xml))
for rid, rel in list(doc.part.rels.items()):
    if "image" in rel.reltype and rid not in usados:
        doc.part.drop_rel(rid)

def forzar_times(elemento):
    for rf in elemento.iter(qn("w:rFonts")):
        for a in list(rf.attrib):
            del rf.attrib[a]
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(a), FUENTE)
    for rpr in elemento.iter(qn("w:rPr")):
        if rpr.find(qn("w:rFonts")) is None:
            rf = OxmlElement("w:rFonts")
            for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
                rf.set(qn(a), FUENTE)
            rpr.insert(0, rf)

forzar_times(body)                      # portada
forzar_times(doc.styles.element)        # estilos y valores por defecto
for st in doc.styles:
    try:
        st.font.name = FUENTE
    except (AttributeError, ValueError):
        pass
dd = doc.styles.element.find(qn("w:docDefaults"))
rpd = dd.find(qn("w:rPrDefault"))
rpr0 = rpd.find(qn("w:rPr"))
if rpr0.find(qn("w:rFonts")) is None:
    rf = OxmlElement("w:rFonts"); rpr0.insert(0, rf)
forzar_times(dd)

# Estilos de titulo: Times New Roman 14 negrita, negro (los usa el indice)
for nombre in ("Heading 1", "Heading 2"):
    st = doc.styles[nombre]
    rpr = st.element.get_or_add_rPr()
    for viejo in rpr.findall(qn("w:rFonts")):
        rpr.remove(viejo)
    rf = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), FUENTE)
    rpr.insert(0, rf)
    st.font.size = Pt(14)
    st.font.bold = True
    st.font.italic = False
    st.font.color.rgb = NEGRO

# ----------------------------------------------------------------------------
# Utilidades de formato
# ----------------------------------------------------------------------------
def fmt(run, size=12, bold=False, italic=False, font=FUENTE):
    run.font.name = font
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    for a in ("w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = NEGRO
    return run

def espaciado(p, interlineado=1.5, antes=0, despues=6):
    pf = p.paragraph_format
    pf.line_spacing = interlineado
    pf.space_before = Pt(antes)
    pf.space_after = Pt(despues)

def salto_pagina():
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)

TITULOS = []  # (nivel, texto) en orden, para el indice

def titulo(texto, nivel=1, nueva_pagina=False):
    p = doc.add_paragraph(style="Heading %d" % nivel)
    espaciado(p, antes=12 if nivel == 1 else 6, despues=6)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.page_break_before = nueva_pagina
    fmt(p.add_run(texto), size=14, bold=True)
    TITULOS.append((nivel, texto))
    return p

def par(texto, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Parrafo normal; **texto** va en negrita. Los `...` solo marcan nombres (misma fuente)."""
    p = doc.add_paragraph()
    p.alignment = align
    espaciado(p)
    for trozo in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", texto):
        if not trozo:
            continue
        if trozo.startswith("**"):
            fmt(p.add_run(trozo[2:-2]), bold=True)
        elif trozo.startswith("`"):
            fmt(p.add_run(trozo[1:-1]))
        else:
            fmt(p.add_run(trozo))
    return p

N_FIG = [0]
N_TAB = [0]

def leyenda_figura(texto):
    N_FIG[0] += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    espaciado(p, interlineado=1.0, antes=4, despues=12)
    fmt(p.add_run(f"Figura {N_FIG[0]}. "), bold=True)
    fmt(p.add_run(texto), italic=True)

def figura(ruta, texto, ancho=ANCHO_TEXTO):
    from PIL import Image
    w_px = Image.open(ruta).size[0]
    ancho = min(ancho, w_px / 96 * 2.54 * 1.25)  # no agrandar capturas pequenas de mas
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    espaciado(p, interlineado=1.0, antes=6, despues=0)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(ruta, width=Cm(ancho))
    leyenda_figura(texto)

def captura(nombre, texto, ancho=ANCHO_TEXTO):
    figura(os.path.join(CAP, nombre), texto, ancho)

def grafica(nombre, texto):
    figura(os.path.join(IMG, nombre), texto, 15)

def espacio_para_captura(nombre, texto):
    """Recuadro para pegar una captura que no llego como archivo."""
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    c.width = Cm(14)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    espaciado(p, interlineado=1.0, antes=40, despues=40)
    fmt(p.add_run(f"[Pegar aquí la captura {nombre}]"), italic=True)
    leyenda_figura(texto)

def leyenda_tabla(texto):
    N_TAB[0] += 1
    p = doc.add_paragraph()
    espaciado(p, interlineado=1.0, antes=6, despues=4)
    p.paragraph_format.keep_with_next = True
    fmt(p.add_run(f"Tabla {N_TAB[0]}. "), bold=True)
    fmt(p.add_run(texto), italic=True)

def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)

def tabla(texto, encabezados, filas, anchos=None, size=10):
    leyenda_tabla(texto)
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, e in enumerate(encabezados):
        c = t.rows[0].cells[i]
        sombrear(c, "D9D9D9")
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        espaciado(p, interlineado=1.0, despues=0)
        fmt(p.add_run(e), size=size, bold=True)
    for fila in filas:
        cells = t.add_row().cells
        for i, v in enumerate(fila):
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            espaciado(p, interlineado=1.0, despues=0)
            fmt(p.add_run(str(v)), size=size)
    if anchos:
        for fila in t.rows:
            for i, w in enumerate(anchos):
                fila.cells[i].width = Cm(w)
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    q = doc.add_paragraph()
    espaciado(q, interlineado=1.0, despues=6)

def codigo(texto):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    sombrear(c, "F2F2F2")
    p = c.paragraphs[0]
    for i, linea in enumerate(texto.split("\n")):
        if i:
            p = c.add_paragraph()
        espaciado(p, interlineado=1.0, despues=0)
        fmt(p.add_run(linea.replace("\t", "    ") or " "), size=10)
    q = doc.add_paragraph()
    espaciado(q, interlineado=1.0, despues=6)

def campo_simple(run, instr):
    for tipo in ("begin", "instr", "separate"):
        if tipo == "instr":
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = instr
        else:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tipo)
        run._r.append(e)

def cerrar_campo(run):
    e = OxmlElement("w:fldChar")
    e.set(qn("w:fldCharType"), "end")
    run._r.append(e)

# ----------------------------------------------------------------------------
# INDICE (tabla de contenido automatica de Word)
# ----------------------------------------------------------------------------
salto_pagina()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
espaciado(p, despues=12)
fmt(p.add_run("Índice"), size=14, bold=True)
marcador_indice = doc.add_paragraph()  # se reemplaza al final por el campo TOC

# ----------------------------------------------------------------------------
# CONTENIDO
# ----------------------------------------------------------------------------
titulo("Introducción", nueva_pagina=True)
par("La programación concurrente reúne las técnicas que permiten que varias partes de un programa avancen al mismo "
    "tiempo. Hoy prácticamente cualquier computadora tiene un procesador con varios núcleos, de modo que un programa "
    "que se ejecuta en un único hilo aprovecha solo una fracción del CPU disponible. Para el sistema operativo este "
    "tema está ligado a la gestión de procesos e hilos, ya que es el planificador (scheduler) quien decide en qué "
    "núcleo y en qué momento se ejecuta cada hilo (Silberschatz et al., 2018).")
par("En este proyecto se parte de un algoritmo sencillo, el Bubble Sort, y se transforma en tres pasos para observar "
    "con datos medidos qué ocurre con el número de intercambios y con el tiempo de ejecución (Pineda, 2026). En el "
    "primer paso se usa el Bubble Sort clásico modificado para contar los intercambios. En el segundo, el arreglo se "
    "divide en dos mitades que se ordenan por separado y luego se mezclan (merge), todavía de forma secuencial. En el "
    "tercero, cada mitad se ordena en un hilo (thread) de Java distinto y, cuando ambos terminan, se hace un único "
    "merge.")

titulo("Objetivos")
par("El objetivo general es dar los primeros pasos en la programación concurrente con los hilos de Java y medir su "
    "efecto real sobre el rendimiento. De forma específica, se busca medir cuántos intercambios realiza el Bubble Sort "
    "para 10, 100, 1,000 y 10,000 elementos y explicar ese comportamiento con la teoría; determinar si dividir el "
    "problema en dos mitades mejora el rendimiento y por qué; implementar la versión con hilos usando Thread, start y "
    "join y compararla con las versiones secuenciales; y analizar cómo se comportaría la versión con hilos en un CPU "
    "de un solo núcleo o de dos núcleos, simulándolo en la práctica al limitar los procesadores que puede usar el "
    "programa.")

titulo("Entorno de trabajo")
par("Todas las pruebas se realizaron en una laptop con Windows 11, usando Visual Studio Code como editor y la "
    "terminal integrada para compilar y ejecutar. Las características del equipo se resumen en la Tabla 1.")
tabla("Entorno en el que se obtuvieron los resultados.", ["Elemento", "Valor"], [
    ["Sistema operativo", "Windows 11 de 64 bits"],
    ["Procesador", "AMD Ryzen 5 7520U, 2.80 GHz base (hasta 4.1 GHz)"],
    ["Núcleos", "4 núcleos físicos, 8 procesadores lógicos (SMT)"],
    ["Memoria caché", "L1: 256 KB, L2: 2 MB, L3: 4 MB"],
    ["Memoria RAM", "7.2 GB"],
    ["Java", "JDK 27 (javac 27)"],
    ["Editor y terminal", "Visual Studio Code con Extension Pack for Java, PowerShell y CMD"],
    ["Datos de prueba", "Enteros aleatorios entre 0 y 99,999 con semilla fija (12345 + N)"],
    ["Medición de tiempo", "System.nanoTime(), mediana de 5 repeticiones con calentamiento previo de la JVM"],
], anchos=[4.5, 11.0], size=11)
par("El proyecto está formado por cuatro programas sin paquete (package), guardados en la misma carpeta: "
    "`bubbleSort.java` para el Paso 1, `bubbleSortDividido.java` para el Paso 2, `bubbleSortHilos.java` para el Paso 3 "
    "y `Comparacion.java`, que ejecuta las tres versiones con exactamente los mismos datos, repite cada medición cinco "
    "veces y guarda los resultados en un archivo CSV que se puede abrir en Excel.")
captura("01_proyecto.png", "Carpeta del proyecto en Visual Studio Code con los archivos fuente y compilados.", 7.5)
par("Para compilar se abrió la terminal integrada de Visual Studio Code en la carpeta del proyecto y se ejecutó "
    "`javac *.java`. Cuando el comando no muestra ningún mensaje significa que los cuatro programas compilaron sin "
    "errores. Después, cada programa se ejecuta con `java` seguido del nombre de la clase y, si se desea, de los "
    "tamaños de arreglo a probar.")
captura("02_compilar.png", "Verificación de la versión del compilador (javac 27) y compilación de los cuatro programas.", 11)
par("Como los datos se generan con una semilla fija, los tres programas ordenan exactamente los mismos números para "
    "cada tamaño N. Por eso el número de intercambios se puede comparar directamente entre pasos y es idéntico en "
    "cualquier computadora, mientras que los tiempos dependen del equipo y varían un poco entre ejecuciones.")

# ---------------------------------------------------------------- PASO 1
titulo("Paso 1: Bubble Sort secuencial con contador de intercambios", nueva_pagina=True)
titulo("Modificación realizada", 2)
par("Se transcribió el programa del enunciado en el archivo `bubbleSort.java`. La modificación pedida consiste en "
    "contar los intercambios, así que dentro del método `bubble_srt` se agregó la variable `intercambios`, que aumenta "
    "en uno cada vez que se ejecuta el bloque de intercambio (swap), y el método ahora devuelve ese total para que el "
    "`main` lo imprima. Se usó el tipo `long` en lugar de `int` porque con arreglos grandes el número de intercambios "
    "puede superar el valor máximo de un `int`, que es 2,147,483,647.")
captura("03_codigo_contador.png", "Método bubble_srt con el contador de intercambios agregado.")
par("Además, el `main` acepta argumentos. Si se ejecuta sin argumentos corre el ejemplo original de ocho números; si "
    "se le pasan tamaños, genera arreglos aleatorios de esos tamaños, los ordena, verifica que quedaron ordenados y "
    "reporta intercambios y tiempo.")

titulo("Ejecución con el ejemplo del enunciado", 2)
captura("06_paso1_ejemplo.png", "Ejecución de java bubbleSort con el arreglo original {12, 9, 4, 99, 120, 1, 3, 10}.")
par("El arreglo de ocho elementos necesitó **16 intercambios**. Ese número coincide exactamente con la cantidad de "
    "inversiones del arreglo, es decir, con las parejas de números que están en el orden incorrecto, como el 12 que "
    "aparece antes que el 9. Cada intercambio del Bubble Sort corrige exactamente una inversión, por lo que el total de "
    "intercambios siempre es igual al número de inversiones (Cormen et al., 2022).")

titulo("Pruebas con 10, 100, 1,000 y 10,000 elementos", 2)
captura("07_paso1_pruebas.png", "Ejecución de java bubbleSort 10 100 1000 10000.")
par("En esta ejecución se obtuvieron 29, 2,450, 245,941 y 24,998,680 intercambios, con tiempos de 0.005 ms, "
    "0.137 ms, 4.560 ms y 88.813 ms respectivamente. Todos los arreglos quedaron ordenados.")

titulo("Resultados con puntos intermedios", 2)
par("Para la gráfica se agregaron puntos intermedios (50, 250, 500, 750, 2,500, 5,000 y 7,500 elementos) usando el "
    "programa `Comparacion`. La Tabla 2 compara los intercambios medidos con el número de inversiones del arreglo, "
    "calculado con otro algoritmo, y con el valor teórico esperado para datos aleatorios, n(n−1)/4.")
filas = []
for n in TAMANOS:
    if n > 10000:
        continue
    r = M8[n]
    filas.append([ent(n), ent(r["intercambios_paso1"]), ent(r["inversiones"]), ent(r["teorico_n(n-1)/4"]),
                  f"{100 * r['intercambios_paso1'] / r['teorico_n(n-1)/4']:.1f} %", ms(r["ms_paso1"])])
tabla("Intercambios y tiempo del Paso 1 (tiempo como mediana de 5 ejecuciones).",
      ["N", "Intercambios medidos", "Inversiones", "Teórico n(n−1)/4", "Medido / teórico", "Tiempo (ms)"], filas,
      anchos=[1.8, 3.2, 2.8, 3.0, 2.4, 2.3])
grafica("paso1_intercambios.png", "Intercambios del Paso 1 según el número de elementos.")
grafica("paso1_tiempo.png", "Tiempo de ejecución del Paso 1 según el número de elementos.")

titulo("Interpretación de los resultados", 2)
r1k, r10k = M8[1000], M8[10000]
par("La curva de intercambios es una parábola y no una recta. Al multiplicar N por 10, los intercambios se "
    f"multiplican aproximadamente por 100: de 10 a 100 elementos pasan de {ent(M8[10]['intercambios_paso1'])} a "
    f"{ent(M8[100]['intercambios_paso1'])}, y de 1,000 a 10,000 pasan de {ent(r1k['intercambios_paso1'])} a "
    f"{ent(r10k['intercambios_paso1'])}. Esto confirma que el Bubble Sort es un algoritmo de orden O(N²).")
par("El valor n(n−1)/4 se explica porque en un arreglo de N elementos existen n(n−1)/2 parejas posibles y, si los "
    "datos son aleatorios, cada pareja tiene la mitad de probabilidad de estar invertida. Como cada intercambio corrige "
    "una inversión, el promedio esperado de intercambios es n(n−1)/4. Con pocos elementos la diferencia puede ser "
    f"grande (con 10 elementos se midieron {ent(M8[10]['intercambios_paso1'])} contra 22.5 esperados), pero a partir "
    "de 1,000 elementos la diferencia es menor al 2 %, porque con más datos el promedio se estabiliza. La columna de "
    "inversiones coincide exactamente con los intercambios en todos los casos.")
par("Aunque el número de intercambios depende de los datos, el Bubble Sort siempre realiza n(n−1)/2 comparaciones, el "
    "doble del promedio de intercambios. Si el arreglo ya estuviera ordenado haría cero intercambios pero seguiría "
    "haciendo todas las comparaciones, y si estuviera en orden inverso haría n(n−1)/2 intercambios, que es el peor "
    "caso.")
par(f"El tiempo también crece de forma cuadrática. Con 1,000 elementos tardó {ms(r1k['ms_paso1'])} ms y con 10,000 "
    f"tardó {ms(r10k['ms_paso1'])} ms, unas {r10k['ms_paso1'] / r1k['ms_paso1']:.0f} veces más con diez veces más datos; "
    f"con 50,000 elementos ya tardó {M8[50000]['ms_paso1'] / 1000:.2f} segundos. El aumento es algo mayor que el factor "
    "100 esperado porque un arreglo de 10,000 enteros ocupa unos 40 KB y ya no cabe en la caché L1 de datos de un "
    "núcleo (32 KB), así que el procesador tiene que ir más veces a memorias más lentas. Para N muy pequeños los "
    "tiempos son de microsegundos y están dominados por el ruido del sistema operativo y por el compilador JIT de "
    "Java; por eso cada medición se repitió cinco veces, se tomó la mediana y se hizo un calentamiento previo de la JVM.")

# ---------------------------------------------------------------- PASO 2
titulo("Paso 2: División del arreglo en dos mitades y mezcla (merge)", nueva_pagina=True)
titulo("Descripción del algoritmo", 2)
par("El programa `bubbleSortDividido.java` hace todo el trabajo en un solo hilo de ejecución. Primero divide el "
    "arreglo original en `left_array`, con la primera mitad, y `right_array`, con la segunda; si N es impar, la mitad "
    "derecha se queda con el elemento sobrante. Luego llama a `bubble_srt` para la mitad izquierda y, cuando termina, "
    "para la mitad derecha. Por último mezcla las dos listas ya ordenadas: compara el primer elemento pendiente de cada "
    "lista, copia el menor al resultado y avanza, hasta agotar ambas. El merge no hace intercambios, solo comparaciones "
    "y copias, y su costo es proporcional a N.")
captura("04_codigo_merge.png", "Método ordenarYReportar de bubbleSortDividido: división, ordenamiento de cada mitad y merge.")

titulo("Ejecución con el ejemplo del enunciado", 2)
captura("08_paso2_ejemplo.png", "Ejecución de java bubbleSortDividido con el arreglo de ocho números.")
par("Con el mismo arreglo de ocho números ahora solo se hicieron **6 intercambios**, tres en cada mitad, en lugar de "
    "16. Las diez inversiones restantes eran entre un número de la mitad izquierda y uno de la derecha, como el 12 y el "
    "1. Esas inversiones cruzadas las resuelve el merge sin hacer ningún intercambio.")

titulo("Pruebas con 10, 100, 1,000 y 10,000 elementos", 2)
captura("09_paso2_pruebas.png", "Ejecución de java bubbleSortDividido 10 100 1000 10000.")
par("En esta ejecución los intercambios totales fueron 9, 1,194, 124,287 y 12,536,532, aproximadamente la mitad que "
    "en el Paso 1, con tiempos de 0.012 ms, 0.075 ms, 2.658 ms y 54.794 ms.")

titulo("Comparación con el Paso 1", 2)
filas = []
for n in TAMANOS:
    r = M8[n]
    filas.append([ent(n), ent(r["intercambios_paso1"]), ent(r["intercambios_paso2"]),
                  f"{100 * (1 - r['intercambios_paso2'] / r['intercambios_paso1']):.1f} %",
                  ms(r["ms_paso1"]), ms(r["ms_paso2"]), f"{r['speedup_p1_vs_p2']:.2f}x"])
tabla("Paso 1 contra Paso 2 con los mismos datos. Una mejora mayor que 1 indica que el Paso 2 fue más rápido.",
      ["N", "Intercambios Paso 1", "Intercambios Paso 2", "Reducción", "ms Paso 1", "ms Paso 2", "Mejora"],
      filas, anchos=[1.6, 2.9, 2.9, 2.0, 2.2, 2.2, 1.7])
grafica("paso2_intercambios.png", "Intercambios del arreglo completo contra el arreglo dividido en dos mitades.")

titulo("Conclusiones del Paso 2", 2)
par("El rendimiento sí mejoró, aunque el programa sigue siendo secuencial. En todos los tamaños los intercambios se "
    "redujeron aproximadamente a la mitad y, a partir de unos 250 elementos, también bajó el tiempo: con 10,000 "
    f"elementos pasó de {ms(M8[10000]['ms_paso1'])} ms a {ms(M8[10000]['ms_paso2'])} ms y con 50,000 de "
    f"{M8[50000]['ms_paso1'] / 1000:.2f} s a {M8[50000]['ms_paso2'] / 1000:.2f} s.")
par("El factor principal es que el costo del Bubble Sort es cuadrático. Ordenar N elementos cuesta un tiempo "
    "proporcional a N², mientras que ordenar dos mitades cuesta 2·(N/2)² = N²/2, es decir, la mitad del trabajo, tanto "
    "en comparaciones como en intercambios. A esto se suma que aproximadamente la mitad de las inversiones son cruzadas, "
    "entre un elemento de la izquierda y uno de la derecha; el Bubble Sort las corregiría una por una, mientras que el "
    "merge las resuelve con solo N comparaciones. El merge, además, es barato: su costo lineal es despreciable frente "
    "al costo cuadrático del ordenamiento cuando N es grande.")
par("También influye la memoria caché. Cada mitad ocupa la mitad de la memoria y cabe mejor en la caché del "
    f"procesador; con 10,000 elementos cada mitad ocupa unos 20 KB y sí entra en la caché L1, por eso la mejora medida "
    f"en ese tamaño fue de {M8[10000]['speedup_p1_vs_p2']:.2f}x, mayor que el 2x teórico. Para tamaños muy grandes la "
    f"mejora se estabiliza cerca de 2x ({M8[50000]['speedup_p1_vs_p2']:.2f}x con 50,000 elementos).")
par("Para N pequeños, entre 10 y 100 elementos, el Paso 2 fue igual o más lento, porque crear los dos arreglos, copiar "
    "los datos y hacer el merge cuesta más que el poco trabajo que se ahorra. Esta misma idea aplicada de forma "
    "recursiva, dividiendo cada mitad una y otra vez, es el algoritmo Merge Sort, que reduce la complejidad a "
    "O(N log N) (Cormen et al., 2022).")

# ---------------------------------------------------------------- PASO 3
titulo("Paso 3: Ordenamiento de las dos mitades en hilos separados", nueva_pagina=True)
titulo("Conceptos de hilos en Java", 2)
par("Un hilo (thread) es una secuencia de instrucciones que el sistema operativo puede planificar de forma "
    "independiente. Todos los hilos de un proceso comparten la misma memoria, pero cada uno tiene su propia pila y su "
    "propio contador de programa (Tanenbaum y Bos, 2015). En Java cada objeto `Thread` corresponde a un hilo real del "
    "sistema operativo, así que, si hay varios núcleos libres, el planificador puede ejecutar dos hilos al mismo tiempo "
    "en núcleos diferentes (Oracle, s.f.-a).")
par("Para crear un hilo se escribe una clase que hereda de `Thread` y se coloca en el método `run` el código que "
    "ejecutará. El método `start` le pide al sistema operativo crear el hilo y ejecutar `run` en paralelo, sin que el "
    "hilo principal espere. El método `join` bloquea al hilo que lo llama hasta que el otro hilo termina, por lo que "
    "funciona como punto de sincronización (Oracle, s.f.-b). Este esquema, en el que el hilo principal reparte el "
    "trabajo, lo pone a correr y luego espera a que todo termine, se conoce como fork–join.")

titulo("Implementación", 2)
par("Se creó la clase interna `HiloOrdenador`, que recibe su mitad del arreglo y la ordena dentro de `run`. Cada hilo "
    "guarda sus intercambios en su propia variable, de modo que los dos hilos nunca escriben en la misma memoria y no "
    "hace falta sincronización. El hilo principal divide el arreglo, crea el hilo izquierdo y el derecho, llama a "
    "`start` en ambos, espera con `join` a que los dos terminen y finalmente hace un único merge.")
captura("05_codigo_hilos.png", "Clase HiloOrdenador, que hereda de Thread y ordena su mitad en el método run.")

titulo("Ejecución", 2)
captura("10_paso3_ejemplo.png", "Ejecución de java bubbleSortHilos con el ejemplo de ocho números.")
captura("11_paso3_pruebas.png", "Ejecución de java bubbleSortHilos 10 100 1000 10000.")
par("Los intercambios son idénticos a los del Paso 2, porque los hilos hacen exactamente el mismo trabajo, solo que "
    "al mismo tiempo. Lo que cambia es el tiempo: con 10,000 elementos la versión con hilos tardó 24.333 ms, menos de "
    "la mitad que el Paso 2 en la ejecución anterior (54.794 ms), pero con 10 elementos tardó 1.252 ms, muchísimo más "
    "que las versiones secuenciales. El programa también informa que la JVM ve 8 procesadores disponibles, que son los "
    "8 procesadores lógicos del Ryzen 5 7520U.")

titulo("Comparación de las tres versiones", 2)
par("Para comparar las tres versiones en igualdad de condiciones se ejecutó `java Comparacion`, que usa los mismos "
    "datos para los tres pasos, repite cada medición cinco veces y reporta la mediana. La Figura 15 muestra una de esas "
    "ejecuciones; los valores de las tablas corresponden a la ejecución guardada en el archivo resultados.csv, por lo "
    "que los tiempos pueden diferir un poco de la captura, mientras que los intercambios son idénticos.")
captura("13_comparacion.png", "Ejecución de java Comparacion con los tres pasos sobre los mismos datos.")
filas = []
for n in TAMANOS:
    r = M8[n]
    filas.append([ent(n), ms(r["ms_paso1"]), ms(r["ms_paso2"]), ms(r["ms_paso3"]),
                  f"{r['speedup_p2_vs_p3']:.2f}x", f"{r['speedup_p1_vs_p3']:.2f}x"])
tabla("Tiempos de las tres versiones con los 8 procesadores lógicos (mediana de 5 ejecuciones). Los valores mayores "
      "que 1 en las dos últimas columnas indican que la versión con hilos fue más rápida.",
      ["N", "ms Paso 1", "ms Paso 2", "ms Paso 3", "Paso 2 / Paso 3", "Paso 1 / Paso 3"], filas,
      anchos=[2.0, 2.6, 2.6, 2.6, 2.8, 2.8])
grafica("tiempos_tres_versiones.png", "Tiempo de las tres versiones en escala logarítmica.")

titulo("Uso de los núcleos durante la ejecución", 2)
par("Mientras se ejecutaban las pruebas se observó el Administrador de tareas de Windows. En la Figura 17, tomada "
    "durante la primera parte de `Comparacion`, el uso total del CPU se mantiene bajo, con picos cercanos al 15 %, "
    "porque la mayor parte del tiempo trabaja un solo hilo. En la Figura 18, al ejecutar `java bubbleSortHilos 100000`, "
    "el uso sube a valores entre 25 % y 35 %. Esto es coherente con lo esperado: el equipo tiene 8 procesadores "
    "lógicos, así que cada hilo que trabaja al 100 % representa aproximadamente un 12.5 % del total, y dos hilos "
    "trabajando a la vez representan alrededor del 25 %. En esa ejecución, ordenar 100,000 elementos con dos hilos "
    "tomó 3,392.665 ms y requirió 1,247,731,272 intercambios.")
captura("14_cpu_paso2.png", "Uso del CPU durante la primera parte de la ejecución de Comparacion.")
captura("15_cpu_paso3.png", "Uso del CPU al ejecutar bubbleSortHilos con 100,000 elementos.")
par("La misma figura muestra que la memoria RAM estaba al 97 % de uso (7.0 de 7.2 GB), un dato que se relaciona con "
    "una de las dificultades descritas más adelante.")

titulo("Simulación de un CPU single-core y dual-core", 2)
par("Para responder cómo operaría la versión con hilos en un CPU de uno o dos núcleos se repitió el experimento "
    "limitando los procesadores lógicos en los que Windows puede ejecutar el programa, lo que se conoce como afinidad "
    "de CPU. Esto se hace con el comando `start /affinity` de CMD (Microsoft, 2023), donde el valor 1 permite usar solo "
    "el procesador lógico 0 y el valor 3 permite usar los procesadores lógicos 0 y 1. Como la terminal de Visual Studio "
    "Code es PowerShell, el comando se ejecutó a través de CMD con `cmd /c \"start /affinity 1 /wait /b java "
    "Comparacion r_1nucleo.csv 5\"` y su equivalente con afinidad 3.")
captura("16_1nucleo.png", "Ejecución de Comparacion limitada a un procesador lógico (afinidad 1).")
captura("17_2nucleos.png", "Ejecución de Comparacion limitada a dos procesadores lógicos (afinidad 3).")
par("Las capturas muestran ejecuciones individuales, por lo que sus tiempos pueden variar un poco respecto a los de "
    "la Tabla 5, que provienen de los archivos r_1nucleo.csv y r_2nucleos.csv. En ambas ejecuciones el programa sigue indicando que la JVM ve 8 procesadores, porque en Windows el método "
    "`availableProcessors` reporta los procesadores del equipo y no la afinidad asignada. Sin embargo, los tiempos "
    "confirman que la restricción sí se aplicó: con un solo procesador lógico la versión con hilos dejó de ganar "
    "tiempo, como se ve en la Tabla 5 y en la Figura 21.")
filas = []
for n in TAMANOS:
    filas.append([ent(n), ms(M1[n]["ms_paso2"]), ms(M1[n]["ms_paso3"]), f"{M1[n]['speedup_p2_vs_p3']:.2f}x",
                  ms(M2[n]["ms_paso2"]), ms(M2[n]["ms_paso3"]), f"{M2[n]['speedup_p2_vs_p3']:.2f}x",
                  f"{M8[n]['speedup_p2_vs_p3']:.2f}x"])
tabla("Paso 2 (secuencial) contra Paso 3 (hilos) con 1, 2 y 8 procesadores lógicos. Speedup = tiempo Paso 2 / tiempo Paso 3.",
      ["N", "1 proc. ms P2", "1 proc. ms P3", "1 proc. speedup", "2 proc. ms P2", "2 proc. ms P3",
       "2 proc. speedup", "8 proc. speedup"], filas, anchos=[1.5, 2.0, 2.0, 1.9, 2.0, 2.0, 1.9, 1.9], size=9)
grafica("speedup_nucleos.png", "Aceleración de la versión con hilos según los procesadores disponibles. Por encima de 1 "
        "los hilos ayudan y por debajo estorban.")

titulo("Conclusiones del Paso 3", 2)
lo1 = [M1[n]["speedup_p2_vs_p3"] for n in TAMANOS if n >= 5000]
par("Con la evidencia del Paso 2 se puede concluir que ejecutar las mitades en hilos es más eficiente, igual o peor "
    "según el tamaño del problema y los núcleos disponibles. Con todos los procesadores disponibles y N a partir de "
    f"unos 2,500 elementos, los hilos fueron más rápidos. Con 50,000 elementos el Paso 3 tardó "
    f"{M8[50000]['ms_paso3']:.0f} ms contra {M8[50000]['ms_paso2']:.0f} ms del Paso 2 "
    f"({M8[50000]['speedup_p2_vs_p3']:.2f}x) y contra {M8[50000]['ms_paso1']:.0f} ms del Paso 1 "
    f"({M8[50000]['speedup_p1_vs_p3']:.2f}x). Es decir, dividir el problema aportó una mejora cercana a 2x y "
    "paralelizarlo aportó otra mejora cercana a 2x, muy próxima al máximo teórico para dos hilos.")
par("Con N pequeño la versión con hilos fue peor. Crear e iniciar un hilo del sistema operativo cuesta del orden de "
    f"décimas de milisegundo; con 10 elementos el Paso 3 tardó {ms(M8[10]['ms_paso3'])} ms, mientras que el Paso 2 "
    f"tardó {ms(M8[10]['ms_paso2'])} ms. El paralelismo solo conviene cuando cada hilo tiene suficiente trabajo para "
    "compensar el costo de crearlo.")
par("En un CPU de un solo núcleo la versión con hilos no mejora. Los dos hilos no pueden correr al mismo tiempo, así "
    "que el planificador los alterna por turnos (time-slicing) con cambios de contexto (Silberschatz et al., 2018). El "
    "trabajo total es el mismo que en el Paso 2, más el costo de crear los hilos y de los cambios de contexto; por eso "
    f"el speedup medido con afinidad 1 quedó entre {min(lo1):.2f}x y {max(lo1):.2f}x para N de 5,000 en adelante, "
    "prácticamente igual que la versión secuencial. Aun así, el Paso 3 en un núcleo sigue siendo más rápido que el "
    "Paso 1, porque conserva la ventaja algorítmica de dividir el arreglo.")
par("En un CPU de dos núcleos reales cada hilo tendría su propio núcleo y la mejora podría acercarse a 2x, como se "
    "observó al usar todos los procesadores. La prueba con afinidad 3 dio una mejora menor, de "
    f"{M2[50000]['speedup_p2_vs_p3']:.2f}x con 50,000 elementos y alrededor de 1x con 10,000. La razón es que en este "
    "procesador los procesadores lógicos 0 y 1 son los dos hilos de hardware (SMT) del mismo núcleo físico; ambos hilos "
    "de Java corrieron en un único núcleo que comparte sus unidades de ejecución y su caché, así que el resultado se "
    "parece más a un single-core con SMT que a un dual-core real. La mejora nunca llega exactamente a 2x porque dividir "
    "el arreglo, crear los hilos y hacer el merge son partes secuenciales, tal como describe la Ley de Amdahl "
    "(Amdahl, 1967), y porque las mitades pueden tener distinta cantidad de inversiones, de modo que un hilo termina "
    "antes y el otro determina el tiempo total.")
par("Tener más de dos núcleos no ayuda más, porque el programa solo crea dos hilos y los demás núcleos quedan sin "
    "trabajo. Para aprovecharlos habría que dividir el arreglo en más partes, por ejemplo en tantas como procesadores "
    "reporte `availableProcessors`.")

titulo("Demostración de una condición de carrera", 2)
par("Durante el desarrollo se probó primero usar un único contador estático compartido por ambos hilos, y el "
    "resultado era incorrecto y cambiaba en cada ejecución. Para demostrarlo, el programa acepta la opción "
    "`--compartido`, que además del contador propio de cada hilo incrementa un contador global sin sincronización.")
captura("12_paso3_carrera.png", "Ejecución de java bubbleSortHilos --compartido 1000 10000.")
par("Con 1,000 elementos el contador compartido marcó 106,823 cuando debía marcar 124,287, y con 10,000 elementos "
    "marcó 7,811,971 cuando debía marcar 12,536,532, es decir, se perdieron 4,724,561 incrementos. La instrucción "
    "`contadorCompartido++` parece una sola operación, pero en realidad son tres: leer el valor, sumarle uno y "
    "escribirlo. Si los dos hilos leen el mismo valor al mismo tiempo, ambos escriben el mismo resultado y se pierde un "
    "incremento. Esto es una condición de carrera sobre una sección crítica (Silberschatz et al., 2018). Se puede "
    "resolver con `synchronized`, con `AtomicLong` o, como se hizo en la versión final, evitando compartir el dato: "
    "cada hilo cuenta en su propia variable y el hilo principal suma los dos resultados después del `join`, lo cual es "
    "correcto y no pierde rendimiento (Goetz et al., 2006).")

# ---------------------------------------------------------------- DIFICULTADES
titulo("Comentarios de implementación y dificultades encontradas", nueva_pagina=True)
par("La primera dificultad apareció al copiar el código del enunciado desde el PDF. El texto \"Values Before the "
    "sort:\\n\" quedó partido en dos líneas, lo cual no es válido para un String en Java, y la instrucción `j++` "
    "aparecía separada en dos renglones. Hubo que reconstruir esas líneas para que el programa compilara.")
par("En el Paso 2 el enunciado sugiere llamar a `bubble_srt` con N/2 elementos para cada mitad, pero cuando N es "
    "impar la división entera redondea hacia abajo y se pierde un elemento. Se resolvió dejando que la mitad derecha "
    "tenga tamaño N − N/2. En el Paso 3 surgió la condición de carrera del contador compartido descrita en la sección "
    "anterior, que se resolvió con un contador por hilo. También se tuvo cuidado de llamar a `start` y no a `run`, "
    "porque `run` ejecuta el código en el hilo principal de forma secuencial y no produce paralelismo, y de no olvidar "
    "`join`, porque sin él el merge se haría mientras los hilos todavía están ordenando. Por eso cada programa verifica "
    "al final que el arreglo quedó ordenado.")
par("Las primeras mediciones de tiempo variaban mucho entre ejecuciones porque Java compila el código mientras se "
    "ejecuta (compilador JIT) y el sistema operativo atiende otros procesos al mismo tiempo. Se resolvió usando "
    "`System.nanoTime`, una fase de calentamiento, cinco repeticiones con mediana y la misma semilla aleatoria para las "
    "tres versiones. Aun así, las Figuras 5, 10 y 14 muestran tiempos distintos a los de las tablas, porque son "
    "ejecuciones individuales sin calentamiento.")
par("Al calcular el valor teórico n(n−1)/4 con el tipo `int`, el resultado para 50,000 elementos salió negativo, "
    "porque 50,000 × 49,999 es cerca de 2,500 millones y no cabe en un `int`. Se corrigió haciendo la operación con "
    "`long`, y por la misma razón todos los contadores de intercambios son `long`.")
par("En cuanto al entorno, al principio el comando `javac` no era reconocido en la terminal, a pesar de que el JDK 27 "
    "estaba instalado, porque su carpeta bin no estaba en la variable PATH; se agregó la ruta del JDK a PATH. Después, "
    "el comando `start /affinity` falló en PowerShell, porque ahí `start` es un alias de otro comando "
    "(Start-Process) con otra sintaxis; se resolvió ejecutándolo a través de CMD con `cmd /c`. Además, el servidor de "
    "lenguaje Java de la extensión de Visual Studio Code se cerró una vez por falta de memoria y generó los archivos "
    "hs_err_pid27628.log y replay_pid27628.log. Esto coincide con el 97 % de uso de RAM observado en el Administrador "
    "de tareas y no afectó a los programas del proyecto, que se compilaron y ejecutaron desde la terminal.")
par("Por último, al simular el single-core y el dual-core se observó que `availableProcessors` seguía reportando 8 "
    "procesadores aunque la afinidad estuviera limitada, por lo que la verificación se hizo con los tiempos medidos. "
    "También se comprobó que la afinidad 3 no equivale a dos núcleos físicos, sino a los dos hilos SMT de un mismo "
    "núcleo; para simular un dual-core real se podría usar una afinidad que tome procesadores lógicos de núcleos "
    "distintos.")

# ---------------------------------------------------------------- CONCLUSIONES
titulo("Conclusiones generales")
par("El Bubble Sort realiza en promedio n(n−1)/4 intercambios, uno por cada inversión del arreglo, y su tiempo crece "
    "de forma cuadrática: multiplicar los datos por 10 multiplica el trabajo por cerca de 100. Dividir el problema en "
    "dos mitades y mezclarlas reduce el trabajo a la mitad aun sin paralelismo, porque 2·(N/2)² = N²/2 y el merge "
    "resuelve las inversiones cruzadas en tiempo lineal; esta es la idea en la que se basa el Merge Sort.")
par("Ejecutar las mitades en hilos separados solo mejora el tiempo si hay núcleos libres para ejecutarlos al mismo "
    "tiempo y si el trabajo de cada hilo es mucho mayor que el costo de crearlo. En este equipo, con todos los "
    "procesadores disponibles, se obtuvo casi el máximo teórico de 2x frente al Paso 2, y la versión final fue unas "
    f"{M8[50000]['speedup_p1_vs_p3']:.0f} veces más rápida que el Bubble Sort original con 50,000 elementos. Con un "
    "solo procesador lógico los hilos no aportaron ninguna mejora.")
par("También quedó claro que los hilos comparten memoria, lo cual es cómodo pero peligroso: cualquier dato que dos "
    "hilos modifiquen a la vez necesita sincronización o, mejor aún, un diseño que evite compartirlo. Todo esto se "
    "conecta con la gestión de procesos del sistema operativo, ya que los hilos de Java son hilos del sistema operativo "
    "y es su planificador el que decide en qué núcleo corre cada uno.")

# ---------------------------------------------------------------- REFERENCIAS
titulo("Referencias", nueva_pagina=True)
referencias = [
    "Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. "
    "En Proceedings of the April 18-20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. "
    "https://doi.org/10.1145/1465482.1465560",
    "Cormen, T. H., Leiserson, C. E., Rivest, R. L., y Stein, C. (2022). Introduction to algorithms (4.ª ed.). MIT Press.",
    "Goetz, B., Peierls, T., Bloch, J., Bowbeer, J., Holmes, D., y Lea, D. (2006). Java concurrency in practice. "
    "Addison-Wesley.",
    "Microsoft. (2023). start. Microsoft Learn. "
    "https://learn.microsoft.com/es-es/windows-server/administration/windows-commands/start",
    "Oracle. (s.f.-a). Lesson: Concurrency. The Java Tutorials. "
    "https://docs.oracle.com/javase/tutorial/essential/concurrency/",
    "Oracle. (s.f.-b). Class Thread. Java SE API Specification. "
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html",
    "Pineda, R. A. (2026). Proyecto #1: Primeros pasos en la programación concurrente [Enunciado de proyecto]. "
    "Universidad Tecnológica Centroamericana.",
    "Silberschatz, A., Galvin, P. B., y Gagne, G. (2018). Operating system concepts (10.ª ed.). Wiley.",
    "Tanenbaum, A. S., y Bos, H. (2015). Modern operating systems (4.ª ed.). Pearson.",
]
for ref in referencias:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    espaciado(p, despues=6)
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.first_line_indent = Cm(-1.27)
    fmt(p.add_run(ref))

# ---------------------------------------------------------------- ANEXO
titulo("Anexo: Código fuente", nueva_pagina=True)
par("A continuación se incluye el código fuente completo de los cuatro programas, tal como se compilaron y "
    "ejecutaron en el equipo de pruebas.")
for archivo, desc in [("bubbleSort.java", "Paso 1"), ("bubbleSortDividido.java", "Paso 2"),
                      ("bubbleSortHilos.java", "Paso 3"), ("Comparacion.java", "experimento comparativo")]:
    titulo(f"{archivo} ({desc})", 2)
    codigo(fuente_java(archivo))

# ----------------------------------------------------------------------------
# Indice: campo TOC de Word con las entradas ya escritas
# ----------------------------------------------------------------------------
sec = doc.sections[0]
tab_pos = sec.page_width - sec.left_margin - sec.right_margin
entradas = []
for k, (nivel, texto) in enumerate(TITULOS):
    q = OxmlElement("w:p")
    entradas.append(q)
    marcador_indice._p.addprevious(q)
from docx.text.paragraph import Paragraph
for k, (nivel, texto) in enumerate(TITULOS):
    p = Paragraph(entradas[k], marcador_indice._parent)
    espaciado(p, interlineado=1.5, despues=0)
    p.paragraph_format.left_indent = Cm(0 if nivel == 1 else 0.75)
    p.paragraph_format.tab_stops.add_tab_stop(tab_pos, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    if k == 0:
        campo_simple(fmt(p.add_run(), bold=(nivel == 1)), 'TOC \\o "1-2" \\h \\z \\u')
    fmt(p.add_run(texto), bold=(nivel == 1))
    fmt(p.add_run("\t" + str(PAGINAS.get(f"{k}", ""))), bold=(nivel == 1))
    if k == len(TITULOS) - 1:
        cerrar_campo(fmt(p.add_run()))
marcador_indice._p.getparent().remove(marcador_indice._p)

json.dump([t for _, t in TITULOS], open(os.path.join(BASE, ".titulos.json"), "w", encoding="utf-8"), ensure_ascii=False)
doc.save(SALIDA)
print("Informe generado:", SALIDA, "| figuras:", N_FIG[0], "| tablas:", N_TAB[0])
