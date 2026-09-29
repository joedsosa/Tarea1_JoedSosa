"""
Construye Informe_Proyecto1_SO.docx usando la portada del laboratorio anterior.

Uso:  python3 generar_informe.py <plantilla_con_portada.docx>

Toma la portada de la plantilla, le cambia el titulo a "Proyecto #1", borra el
resto del contenido y escribe el informe con los resultados de ../resultados.
"""
import csv, os, re, sys, copy
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(BASE, "..")
RES = os.path.join(RAIZ, "resultados")
SRC = os.path.join(RAIZ, "src")
IMG = os.path.join(BASE, "img")
SALIDA = os.path.join(BASE, "Informe_Proyecto1_SO.docx")

AZUL_OSCURO = "1F3864"
NEGRO = RGBColor(0, 0, 0)

# ----------------------------------------------------------------------------
# Datos
# ----------------------------------------------------------------------------
def leer_csv(nombre):
    with open(os.path.join(RES, nombre)) as f:
        return {int(float(r["N"])): {k: float(v) for k, v in r.items()} for r in csv.DictReader(f)}

M4, M2, M1 = leer_csv("resultados_multicore.csv"), leer_csv("resultados_2nucleos.csv"), leer_csv("resultados_1nucleo.csv")
TAMANOS = sorted(M4)

def txt(nombre):
    with open(os.path.join(RES, nombre), encoding="utf-8") as f:
        return f.read().rstrip("\n")

def fuente(nombre):
    with open(os.path.join(SRC, nombre), encoding="utf-8") as f:
        return f.read().rstrip("\n")

def f_ent(x):
    return f"{int(round(x)):,}"

def f_ms(x):
    return f"{x:,.3f}"

# ----------------------------------------------------------------------------
# Portada
# ----------------------------------------------------------------------------
doc = Document(sys.argv[1])
body = doc.element.body

# 1) Cambiar el titulo del cuadro azul (esta dos veces: version moderna y VML de respaldo)
for t in body.iter(qn("w:t")):
    if t.text == "Laboratorio ":
        t.text = "Proyecto "
    elif t.text == "Pthreads":
        t.text = "#1"
    elif t.text == "Semana: ":
        t.text = "Programación concurrente"
for p in body.iter(qn("w:p")):
    # el numero de semana va en un run aparte justo despues de "Semana:"
    ts = [t for t in p.iter(qn("w:t"))]
    for i, t in enumerate(ts):
        if t.text == "Programación concurrente" and i + 1 < len(ts) and ts[i + 1].text.strip().isdigit():
            ts[i + 1].text = ""

# 2) Borrar todo lo que viene despues de la portada (desde "Parte 1 ...")
hijos = list(body)
corte = None
for i, el in enumerate(hijos):
    if el.tag == qn("w:p") and "".join(t.text or "" for t in el.iter(qn("w:t"))).startswith("Parte 1"):
        corte = i
        break
assert corte is not None, "No se encontro el inicio del contenido del laboratorio"
for el in hijos[corte:]:
    if el.tag != qn("w:sectPr"):
        body.remove(el)

# 3) Quitar imagenes del laboratorio viejo que ya no se usan (para no inflar el archivo)
usados = set(re.findall(r'r:(?:embed|id)="([^"]+)"', body.xml))
for rid, rel in list(doc.part.rels.items()):
    if "image" in rel.reltype and rid not in usados:
        doc.part.drop_rel(rid)

# ----------------------------------------------------------------------------
# Utilidades de formato
# ----------------------------------------------------------------------------
def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)

def margenes_celda(celda, cm=0.25):
    tcPr = celda._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for lado in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:w"), str(int(cm * 567)))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tcPr.append(mar)

def run_fmt(run, size=11, bold=False, italic=False, color=NEGRO, font="Calibri"):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:hAnsi"), font)
    run._element.rPr.rFonts.set(qn("w:cs"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    return run

def salto_pagina():
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)

def h1(texto):
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    run_fmt(p.add_run(texto), size=16, bold=True, color=RGBColor.from_string(AZUL_OSCURO))
    return p

def h2(texto):
    p = doc.add_paragraph(style="Heading 2")
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run_fmt(p.add_run(texto), size=13, bold=True, color=RGBColor.from_string("2F5496"))
    return p

def par(texto, after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Parrafo normal. Soporta **negritas** y `codigo` en linea."""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.15
    for trozo in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", texto):
        if not trozo:
            continue
        if trozo.startswith("**"):
            run_fmt(p.add_run(trozo[2:-2]), bold=True)
        elif trozo.startswith("`"):
            run_fmt(p.add_run(trozo[1:-1]), size=10, font="Consolas", color=RGBColor.from_string("C7254E"))
        else:
            run_fmt(p.add_run(trozo))
    return p

def vinetas(items, numerada=False):
    for i, it in enumerate(items, 1):
        p = par(("%d. " % i if numerada else "•  ") + it, after=3, align=WD_ALIGN_PARAGRAPH.LEFT)
        p.paragraph_format.left_indent = Cm(0.9)
        p.paragraph_format.first_line_indent = Cm(-0.5)

def bloque(texto, oscuro=False, size=8.5):
    """Bloque de codigo (gris claro) o de consola (fondo oscuro) en una tabla de una celda."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    sombrear(c, "1E1E1E" if oscuro else "F3F3F3")
    margenes_celda(c)
    color = RGBColor(0xE6, 0xE6, 0xE6) if oscuro else RGBColor(0x1E, 0x1E, 0x1E)
    lineas = texto.split("\n")
    p = c.paragraphs[0]
    for i, linea in enumerate(lineas):
        if i > 0:
            p = c.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        es_prompt = oscuro and linea.startswith("$ ")
        run_fmt(p.add_run(linea if linea else " "), size=size, font="Consolas",
                color=RGBColor(0x7C, 0xD9, 0x7C) if es_prompt else color, bold=es_prompt)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)

def leyenda(texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    run_fmt(p.add_run(texto), size=9, italic=True)

def imagen(nombre, texto, ancho=15.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(IMG, nombre), width=Cm(ancho))
    leyenda(texto)

def tabla(encabezados, filas, anchos=None, size=9):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, e in enumerate(encabezados):
        c = t.rows[0].cells[i]
        sombrear(c, AZUL_OSCURO)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_fmt(c.paragraphs[0].add_run(e), size=size, bold=True, color=RGBColor(255, 255, 255))
    for k, fila in enumerate(filas):
        cells = t.add_row().cells
        for i, v in enumerate(fila):
            if k % 2 == 1:
                sombrear(cells[i], "E9EEF7")
            cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_fmt(cells[i].paragraphs[0].add_run(str(v)), size=size)
    if anchos:
        for fila in t.rows:
            for i, w in enumerate(anchos):
                fila.cells[i].width = Cm(w)
    # repetir encabezado si la tabla cruza de pagina
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    return t

# ----------------------------------------------------------------------------
# Numero de pagina en el pie (sin numero en la portada)
# ----------------------------------------------------------------------------
sec = doc.sections[0]
sec.different_first_page_header_footer = True
fp = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
def campo(p, instr):
    r = p.add_run()
    for tipo, val in (("begin", None), ("instr", instr), ("separate", None), ("text", "1"), ("end", None)):
        if tipo == "instr":
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = val
        elif tipo == "text":
            e = OxmlElement("w:t"); e.text = val
        else:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tipo)
        r._r.append(e)
    run_fmt(r, size=9, color=RGBColor(0x59, 0x59, 0x59))
run_fmt(fp.add_run("Proyecto #1 – Sistemas Operativos I  |  Página "), size=9, color=RGBColor(0x59, 0x59, 0x59))
campo(fp, "PAGE")

# ----------------------------------------------------------------------------
# CONTENIDO
# ----------------------------------------------------------------------------
salto_pagina()

h1("Índice")
indice = [
    "1. Introducción y objetivos",
    "2. Entorno de trabajo y estructura del proyecto",
    "3. Paso 1 – Bubble Sort secuencial con contador de intercambios",
    "4. Paso 2 – Dividir el arreglo en dos mitades y mezclar (merge)",
    "5. Paso 3 – Ordenar las dos mitades en hilos (threads) separados",
    "6. Comentarios de implementación y dificultades encontradas",
    "7. Conclusiones generales",
    "8. Guía para demostrar el proyecto paso a paso",
    "Anexo A – Código fuente completo",
    "Anexo B – Salida completa de los experimentos",
]
for linea in indice:
    par(linea, after=2, align=WD_ALIGN_PARAGRAPH.LEFT)

# ---------------------------------------------------------------- 1
h1("1. Introducción y objetivos")
par("La programación concurrente agrupa las técnicas que permiten que varias partes de un programa avancen al "
    "mismo tiempo. Hoy casi cualquier computadora de escritorio o laptop tiene varios núcleos, así que un programa "
    "que corre en un solo hilo de ejecución está desperdiciando la mayor parte del CPU. Para el sistema operativo "
    "esto se relaciona directamente con la gestión de procesos e hilos: el planificador (scheduler) decide en qué "
    "núcleo y en qué momento corre cada hilo.")
par("En este proyecto se parte de un algoritmo muy sencillo, el **Bubble Sort**, y se va transformando en tres "
    "pasos para observar, con datos medidos, qué pasa con el número de intercambios y con el tiempo de ejecución:")
vinetas([
    "**Paso 1:** Bubble Sort clásico (un solo hilo), modificado para contar los intercambios.",
    "**Paso 2:** el arreglo se divide en dos mitades, cada mitad se ordena por separado y al final se mezclan "
    "(merge). Sigue siendo un programa secuencial.",
    "**Paso 3:** las dos mitades se ordenan en dos hilos (threads) de Java que corren en paralelo; al terminar "
    "ambos se hace un join y un único merge.",
])
par("**Objetivos:**", after=2)
vinetas([
    "Medir cuántos intercambios hace Bubble Sort para 10, 100, 1,000 y 10,000 elementos (y puntos intermedios) "
    "y explicar el comportamiento con la teoría.",
    "Determinar si dividir el problema en dos mitades mejora el rendimiento y por qué.",
    "Usar hilos en Java (Thread, start, join) y comparar el tiempo contra la versión secuencial.",
    "Analizar cómo se comportaría la versión con hilos en un CPU single-core y en uno dual-core, "
    "simulándolo en la práctica al limitar los núcleos que puede usar el programa.",
], numerada=True)

# ---------------------------------------------------------------- 2
h1("2. Entorno de trabajo y estructura del proyecto")
h2("2.1 Entorno de pruebas")
tabla(["Elemento", "Valor"], [
    ["Sistema operativo", "Linux (kernel 6.x, 64 bits)"],
    ["Java", "OpenJDK 21.0.10 (javac + java)"],
    ["Procesador", "Intel Xeon @ 2.10 GHz, 4 núcleos"],
    ["Herramienta para limitar núcleos", "taskset (Linux) – en Windows: start /affinity"],
    ["Datos de prueba", "Enteros aleatorios entre 0 y 99,999 con semilla fija (12345 + N)"],
    ["Medición de tiempo", "System.nanoTime(), mediana de 5 repeticiones, con calentamiento previo de la JVM"],
], anchos=[5.5, 10.5])
leyenda("Tabla 1. Entorno en el que se obtuvieron los resultados de este informe.")
par("Como los datos se generan con una **semilla fija**, los tres programas ordenan exactamente los mismos números "
    "para cada tamaño N. Por eso los números de intercambios se pueden comparar directamente entre pasos, y "
    "cualquier persona que corra el programa obtiene los mismos intercambios (los tiempos sí cambian según la "
    "computadora).")

h2("2.2 Estructura del proyecto")
bloque("""Proyecto1_SO/
|-- src/
|   |-- bubbleSort.java          Paso 1: bubble sort + contador
|   |-- bubbleSortDividido.java  Paso 2: dos mitades + merge
|   |-- bubbleSortHilos.java     Paso 3: dos hilos + join + merge
|   `-- Comparacion.java         los 3 pasos con los mismos datos -> CSV
|-- resultados/                  salidas de consola (.txt) y tablas (.csv)
`-- informe/                     informe, gráficas y scripts""")
leyenda("Figura 1. Organización de los archivos del proyecto.")

h2("2.3 Compilación y ejecución")
par("Los programas no usan paquetes (package), por lo que se compilan y ejecutan directamente desde la terminal "
    "(CMD/PowerShell en Windows o Terminal en Linux/Mac). También se pueden abrir en NetBeans o IntelliJ y "
    "ejecutar con el botón Run, pasando los tamaños como argumentos del programa.")
bloque("""$ cd Proyecto1_SO/src
$ javac *.java                                 (compila los 4 programas)
$ java bubbleSort                              (Paso 1 - ejemplo de 8 números)
$ java bubbleSort 10 100 1000 10000            (Paso 1 - pruebas)
$ java bubbleSortDividido 10 100 1000 10000    (Paso 2)
$ java bubbleSortHilos 10 100 1000 10000       (Paso 3)
$ java Comparacion                             (los 3 pasos -> resultados.csv)""", oscuro=True)
leyenda("Figura 2. Comandos para compilar y ejecutar cada paso.")

# ---------------------------------------------------------------- 3
h1("3. Paso 1 – Bubble Sort secuencial con contador de intercambios")
h2("3.1 Modificación realizada")
par("Se transcribió el programa `bubbleSort.java` del enunciado. La modificación pedida es contar los intercambios: "
    "se agregó una variable `long intercambios` dentro de `bubble_srt`, que se incrementa cada vez que se "
    "ejecuta el bloque de intercambio (swap), y el método ahora la devuelve para que `main` la imprima. Se usó "
    "`long` y no `int` porque para N grandes el número de intercambios puede pasar de 2,147,483,647.")
bloque("""public static long bubble_srt(int a[], int n) {
    int i, j, t = 0;
    long intercambios = 0;                 // <-- NUEVO: contador
    for (i = 0; i < n; i++) {
        for (j = 1; j < (n - i); j++) {
            if (a[j - 1] > a[j]) {
                /* Inicio del intercambio */
                t = a[j - 1];
                a[j - 1] = a[j];
                a[j] = t;
                /* Final del intercambio */
                intercambios++;            // <-- NUEVO: cuenta cada swap
            }
        }
    }
    return intercambios;                   // <-- NUEVO: se devuelve el total
}""")
leyenda("Figura 3. Método bubble_srt con el contador de intercambios.")
par("Además, el `main` acepta argumentos: si se ejecuta sin argumentos corre el ejemplo original de 8 números; si "
    "se le pasan tamaños (por ejemplo `java bubbleSort 10 100 1000 10000`) genera arreglos aleatorios de esos "
    "tamaños, los ordena, verifica que quedaron ordenados y reporta intercambios y tiempo.")

h2("3.2 Ejecución con el ejemplo del enunciado")
bloque(txt("paso1_ejemplo.txt"), oscuro=True)
leyenda("Figura 4. Salida del Paso 1 con el arreglo original {12, 9, 4, 99, 120, 1, 3, 10}.")
par("El arreglo de 8 elementos necesitó **16 intercambios**. Ese número no es casualidad: es exactamente la "
    "cantidad de **inversiones** del arreglo, es decir, de parejas de números que están en el orden incorrecto "
    "(por ejemplo 12 antes que 9). Cada intercambio de Bubble Sort arregla exactamente una inversión, así que "
    "el total de intercambios siempre es igual al número de inversiones.")

h2("3.3 Pruebas con 10, 100, 1,000 y 10,000 elementos")
bloque(txt("paso1_pruebas.txt"), oscuro=True)
leyenda("Figura 5. Salida del Paso 1 con 10, 100, 1,000 y 10,000 elementos aleatorios.")

h2("3.4 Resultados con puntos intermedios")
par("Para la gráfica se usaron también puntos intermedios (50, 250, 500, 750, 2,500, 5,000 y 7,500). La tabla "
    "compara los intercambios medidos con dos referencias: el número de inversiones del arreglo (calculado con "
    "otro algoritmo, en `Comparacion.java`) y el valor teórico esperado para datos aleatorios, **n(n−1)/4**.")
filas = []
for n in TAMANOS:
    if n > 10000:
        continue
    r = M4[n]
    filas.append([f_ent(n), f_ent(r["intercambios_paso1"]), f_ent(r["inversiones"]),
                  f_ent(r["teorico_n(n-1)/4"]), f"{100 * r['intercambios_paso1'] / r['teorico_n(n-1)/4']:.1f} %",
                  f_ms(r["ms_paso1"])])
tabla(["N", "Intercambios medidos", "Inversiones", "Teórico n(n−1)/4", "Medido / teórico", "Tiempo (ms)"], filas,
      anchos=[1.8, 3.2, 3.0, 3.0, 2.5, 2.5])
leyenda("Tabla 2. Intercambios y tiempo del Paso 1 (tiempo = mediana de 5 ejecuciones).")

imagen("paso1_intercambios.png", "Figura 6. Intercambios del Paso 1 vs. N. La línea punteada es la curva teórica n(n−1)/4.")
imagen("paso1_tiempo.png", "Figura 7. Tiempo de ejecución del Paso 1 vs. N.")

h2("3.5 Interpretación de los resultados")
r1k, r10k = M4[1000], M4[10000]
par("**La curva es una parábola, no una recta.** Al multiplicar N por 10, los intercambios se multiplican "
    f"aproximadamente por 100: de 10 a 100 elementos pasan de {f_ent(M4[10]['intercambios_paso1'])} a "
    f"{f_ent(M4[100]['intercambios_paso1'])}; de 1,000 a 10,000 pasan de {f_ent(r1k['intercambios_paso1'])} a "
    f"{f_ent(r10k['intercambios_paso1'])}. Esto confirma que Bubble Sort es un algoritmo **O(N²)**.")
par("**¿Por qué exactamente n(n−1)/4?** En un arreglo de N elementos existen n(n−1)/2 parejas posibles. Si los "
    "datos son aleatorios, cada pareja tiene 50 % de probabilidad de estar invertida, así que en promedio hay "
    "n(n−1)/4 inversiones, y como vimos, intercambios = inversiones. La tabla muestra que los valores medidos "
    f"quedan cerca del teórico: con N muy pequeño la diferencia puede ser grande (con 10 elementos se midieron "
    f"{f_ent(M4[10]['intercambios_paso1'])} contra 22.5 esperados, porque depende mucho de cómo salieron esos pocos "
    "números), pero para N ≥ 1,000 la diferencia es menor al 2 %, porque con más datos el promedio se "
    "estabiliza. La columna de inversiones coincide exactamente con los intercambios en todos los casos.")
par("**Comparaciones vs. intercambios.** Aunque el número de intercambios depende de los datos, Bubble Sort "
    "siempre hace n(n−1)/2 comparaciones (dos veces más que los intercambios promedio). Si el arreglo ya "
    "estuviera ordenado haría 0 intercambios pero seguiría haciendo todas las comparaciones; si estuviera "
    "en orden inverso haría n(n−1)/2 intercambios (el peor caso).")
par(f"**Tiempos.** El tiempo también crece de forma cuadrática: con 1,000 elementos tarda {f_ms(r1k['ms_paso1'])} ms "
    f"y con 10,000 tarda {f_ms(r10k['ms_paso1'])} ms (≈{r10k['ms_paso1'] / r1k['ms_paso1']:.0f} veces más para 10 "
    f"veces más datos). Con 50,000 elementos ya tarda {M4[50000]['ms_paso1'] / 1000:.1f} segundos. Para N muy "
    "pequeños (10–100) los tiempos son de microsegundos y están dominados por ruido del sistema (el "
    "planificador, el recolector de basura y el compilador JIT de Java), por lo que no son representativos; "
    "por eso cada medición se repitió 5 veces y se tomó la mediana, después de \"calentar\" la JVM.")

# ---------------------------------------------------------------- 4
h1("4. Paso 2 – Dividir el arreglo en dos mitades y mezclar (merge)")
h2("4.1 Descripción del algoritmo")
par("El programa `bubbleSortDividido.java` hace lo siguiente, todo en un solo hilo de ejecución:")
vinetas([
    "Divide el arreglo original en `left_array` (primera mitad) y `right_array` (segunda mitad). Si N es impar, "
    "la mitad derecha se queda con el elemento sobrante.",
    "Llama `bubble_srt(left_array, N/2)` y luego `bubble_srt(right_array, N − N/2)`, una después de la otra.",
    "Mezcla (merge) las dos listas ya ordenadas: compara el primer elemento de cada lista, copia el menor al "
    "resultado y avanza, hasta terminar ambas. El merge no hace intercambios, solo comparaciones y copias, y "
    "cuesta O(N).",
], numerada=True)
bloque("""// 1) Dividir el arreglo en dos partes
int mitad = n / 2;
int left_array[]  = new int[mitad];
int right_array[] = new int[n - mitad];
System.arraycopy(array, 0,     left_array,  0, mitad);
System.arraycopy(array, mitad, right_array, 0, n - mitad);

// 2) Ordenar cada mitad por separado (secuencial: primero una, luego la otra)
long intIzq = bubble_srt(left_array,  left_array.length);
long intDer = bubble_srt(right_array, right_array.length);

// 3) Mezclar las dos listas ordenadas
int[] resultado = merge(left_array, right_array);

public static int[] merge(int[] left, int[] right) {
    int[] res = new int[left.length + right.length];
    int i = 0, j = 0, k = 0;
    while (i < left.length && j < right.length) {
        if (left[i] <= right[j]) res[k++] = left[i++];
        else                     res[k++] = right[j++];
    }
    while (i < left.length)  res[k++] = left[i++];
    while (j < right.length) res[k++] = right[j++];
    return res;
}""")
leyenda("Figura 8. Parte central del Paso 2: dividir, ordenar cada mitad y mezclar.")

h2("4.2 Ejecución con el ejemplo del enunciado")
bloque(txt("paso2_ejemplo.txt"), oscuro=True, size=6.8)
leyenda("Figura 9. Salida del Paso 2 con el arreglo de 8 números: 6 intercambios en lugar de 16.")
par("Con el mismo arreglo de 8 números, ahora solo se hicieron **6 intercambios** (3 en cada mitad) en lugar de "
    "16. Las 10 inversiones restantes eran entre un número de la mitad izquierda y uno de la derecha (por "
    "ejemplo 12 y 1); esas \"inversiones cruzadas\" las resuelve el merge sin hacer ningún intercambio.")

h2("4.3 Pruebas con 10, 100, 1,000 y 10,000 elementos")
bloque(txt("paso2_pruebas.txt"), oscuro=True, size=6.8)
leyenda("Figura 10. Salida del Paso 2 con 10, 100, 1,000 y 10,000 elementos.")

filas = []
for n in TAMANOS:
    r = M4[n]
    filas.append([f_ent(n), f_ent(r["intercambios_paso1"]), f_ent(r["intercambios_paso2"]),
                  f"{100 * (1 - r['intercambios_paso2'] / r['intercambios_paso1']):.1f} %",
                  f_ms(r["ms_paso1"]), f_ms(r["ms_paso2"]), f"{r['speedup_p1_vs_p2']:.2f}x"])
tabla(["N", "Intercambios Paso 1", "Intercambios Paso 2", "Reducción", "ms Paso 1", "ms Paso 2", "Mejora (P1/P2)"],
      filas, anchos=[1.7, 2.8, 2.8, 2.0, 2.2, 2.2, 2.2])
leyenda("Tabla 3. Paso 1 vs. Paso 2 con los mismos datos. \"Mejora\" > 1 significa que el Paso 2 fue más rápido.")
imagen("paso2_intercambios.png", "Figura 11. Intercambios del arreglo completo vs. dividido en dos mitades.")

h2("4.4 Conclusiones e interpretación del Paso 2")
par("**Sí se mejoró el rendimiento**, aunque el programa sigue siendo secuencial. Para todos los tamaños los "
    "intercambios se redujeron aproximadamente a la **mitad** (≈50 %), y a partir de unos 250 elementos el "
    f"tiempo también bajó: con 10,000 elementos pasó de {f_ms(M4[10000]['ms_paso1'])} ms a "
    f"{f_ms(M4[10000]['ms_paso2'])} ms y con 50,000 de {M4[50000]['ms_paso1'] / 1000:.2f} s a "
    f"{M4[50000]['ms_paso2'] / 1000:.2f} s. Los principales factores de la mejora son:")
vinetas([
    "**El costo es cuadrático.** Ordenar N elementos cuesta proporcional a N². Ordenar dos mitades cuesta "
    "2·(N/2)² = N²/2, o sea la mitad del trabajo. Aplica a comparaciones (de n(n−1)/2 a ≈n²/4) y a "
    "intercambios (de ≈n²/4 a ≈n²/8).",
    "**Las inversiones cruzadas se resuelven gratis.** Aproximadamente la mitad de las inversiones son entre "
    "un elemento de la izquierda y uno de la derecha. Bubble Sort las resolvería una por una con intercambios; "
    "el merge las resuelve con solo N comparaciones.",
    "**El merge es barato.** Cuesta O(N), que es despreciable frente al O(N²) del ordenamiento cuando N es grande.",
    "**Mejor uso de la memoria caché.** Cada mitad ocupa la mitad de memoria, así que cabe mejor en la caché "
    "del CPU. Por eso en algunos tamaños (5,000–10,000) la mejora medida fue incluso mayor a 2x; para N muy "
    "grandes la mejora se estabiliza cerca de 2x, que es lo que predice la teoría.",
])
par("**Cuándo no conviene:** para N pequeños (10–100) el Paso 2 fue igual o más lento, porque crear los dos "
    "arreglos, copiar los datos y hacer el merge cuesta más que el poco trabajo que se ahorra. Esta misma idea, "
    "aplicada de forma recursiva (dividir cada mitad otra vez, y otra vez…), es exactamente el algoritmo "
    "**Merge Sort**, que baja la complejidad hasta O(N log N).")

# ---------------------------------------------------------------- 5
h1("5. Paso 3 – Ordenar las dos mitades en hilos (threads) separados")
h2("5.1 Conceptos de hilos en Java")
par("Un **hilo (thread)** es una secuencia de instrucciones que el sistema operativo puede planificar de forma "
    "independiente. Todos los hilos de un proceso comparten la misma memoria (los mismos objetos y arreglos), "
    "pero cada uno tiene su propia pila y su propio contador de programa. En Java cada objeto `Thread` "
    "corresponde a un hilo real del sistema operativo, así que si hay varios núcleos, el planificador del SO "
    "puede ejecutar dos hilos al mismo tiempo en núcleos diferentes. Los métodos que se usaron son:")
tabla(["Método", "Qué hace"], [
    ["extends Thread / run()", "Se crea una clase que hereda de Thread y en run() se pone el código que ejecutará el hilo."],
    ["start()", "Le pide al sistema operativo crear el hilo y ejecutar run() en paralelo. El hilo main sigue sin esperar."],
    ["join()", "El hilo que lo llama (main) se bloquea hasta que ese hilo termina. Es el punto de sincronización."],
    ["Runtime.availableProcessors()", "Indica cuántos núcleos puede usar la JVM."],
], anchos=[5.0, 11.0])
leyenda("Tabla 4. Elementos de la API de hilos de Java usados en el Paso 3.")

h2("5.2 Implementación")
par("Se creó la clase interna `HiloOrdenador`, que recibe su mitad del arreglo y la ordena dentro de `run()`. "
    "Cada hilo guarda sus intercambios en su **propia variable**, así los dos hilos nunca escriben en la misma "
    "memoria y no hace falta sincronización. El hilo principal sigue el modelo **fork–join**:")
bloque("""              main: divide el arreglo en left_array y right_array
                                  |
                +-----------------+-----------------+
                | start()                   start() |
                v                                   v
     Hilo-Izquierdo                        Hilo-Derecho
     bubble_srt(left_array)                bubble_srt(right_array)
                |                                   |
                +------------> join() <-------------+
                                  |
                   main: merge(left_array, right_array)
                                  |
                                 fin""", size=8.5)
leyenda("Figura 12. Modelo fork–join del Paso 3: el main crea dos hilos, espera con join() y hace un único merge.")
bloque("""static class HiloOrdenador extends Thread {
    private final int[] arreglo;
    long intercambios = 0;            // contador propio de cada hilo

    HiloOrdenador(String nombre, int[] arreglo) {
        super(nombre);
        this.arreglo = arreglo;
    }

    @Override
    public void run() {               // esto corre en el hilo nuevo
        intercambios = bubble_srt(arreglo, arreglo.length);
    }
}

// ----- en el hilo main -----
HiloOrdenador hiloIzq = new HiloOrdenador("Hilo-Izquierdo", left_array);
HiloOrdenador hiloDer = new HiloOrdenador("Hilo-Derecho",   right_array);
hiloIzq.start();                      // ambos hilos empiezan a ordenar en paralelo
hiloDer.start();

hiloIzq.join();                       // main espera a que terminen los dos
hiloDer.join();

int[] resultado = merge(left_array, right_array);   // un único merge al final""")
leyenda("Figura 13. Clase HiloOrdenador y secuencia start/join/merge del Paso 3.")

h2("5.3 Ejecución")
bloque(txt("paso3_ejemplo.txt"), oscuro=True, size=6.8)
leyenda("Figura 14. Salida del Paso 3 con el ejemplo de 8 números.")
bloque(txt("paso3_pruebas.txt"), oscuro=True, size=6.8)
leyenda("Figura 15. Salida del Paso 3 con 10, 100, 1,000 y 10,000 elementos.")
par("Los intercambios son **idénticos** a los del Paso 2 (los hilos hacen exactamente el mismo trabajo, solo que "
    "al mismo tiempo). Lo que cambia es el **tiempo**: con 10,000 elementos el Paso 3 fue claramente más "
    "rápido que el Paso 2, pero con 10 y 100 elementos tardó entre 0.5 y 1 ms, mucho más que las versiones secuenciales.")

h2("5.4 Comparación de las tres versiones (CPU de 4 núcleos)")
filas = []
for n in TAMANOS:
    r = M4[n]
    filas.append([f_ent(n), f_ms(r["ms_paso1"]), f_ms(r["ms_paso2"]), f_ms(r["ms_paso3"]),
                  f"{r['speedup_p2_vs_p3']:.2f}x", f"{r['speedup_p1_vs_p3']:.2f}x"])
tabla(["N", "ms Paso 1", "ms Paso 2", "ms Paso 3 (hilos)", "Paso 2 / Paso 3", "Paso 1 / Paso 3"], filas,
      anchos=[2.0, 2.6, 2.6, 3.0, 2.8, 2.8])
leyenda("Tabla 5. Tiempos (mediana de 5) de las tres versiones. Valores > 1 en las dos últimas columnas indican "
        "que la versión con hilos fue más rápida.")
imagen("tiempos_tres_versiones.png", "Figura 16. Tiempo de las tres versiones en escala logarítmica.")

h2("5.5 ¿Cómo operaría en un CPU single-core o dual-core? (experimento)")
par("Para no quedarse solo en la teoría, se repitió el experimento completo limitando los núcleos que el sistema "
    "operativo le permite usar al programa (afinidad de CPU). En Linux se hace con `taskset` y en Windows con "
    "`start /affinity`:")
bloque("""$ taskset -c 0   java Comparacion resultados_1nucleo.csv 5    (single-core)
$ taskset -c 0,1 java Comparacion resultados_2nucleos.csv 5   (dual-core)
$ java Comparacion resultados_multicore.csv 5                 (4 núcleos)

REM Equivalente en Windows (CMD):
C:\\> start /affinity 1 /wait java Comparacion resultados_1nucleo.csv 5
C:\\> start /affinity 3 /wait java Comparacion resultados_2nucleos.csv 5""", oscuro=True)
leyenda("Figura 17. Comandos para simular CPUs de 1 y 2 núcleos.")
par("Al correr con `taskset -c 0` el programa confirma que la JVM solo ve un procesador "
    "(\"Nucleos disponibles para la JVM: 1\"). La tabla muestra el speedup del Paso 3 respecto al Paso 2 "
    "(tiempo Paso 2 ÷ tiempo Paso 3) en cada caso:")
filas = []
for n in TAMANOS:
    filas.append([f_ent(n),
                  f_ms(M1[n]["ms_paso2"]), f_ms(M1[n]["ms_paso3"]), f"{M1[n]['speedup_p2_vs_p3']:.2f}x",
                  f_ms(M2[n]["ms_paso2"]), f_ms(M2[n]["ms_paso3"]), f"{M2[n]['speedup_p2_vs_p3']:.2f}x",
                  f"{M4[n]['speedup_p2_vs_p3']:.2f}x"])
tabla(["N", "1 núcleo\nms P2", "1 núcleo\nms P3", "1 núcleo\nspeedup", "2 núcleos\nms P2", "2 núcleos\nms P3",
       "2 núcleos\nspeedup", "4 núcleos\nspeedup"], filas, anchos=[1.6, 2.0, 2.0, 1.9, 2.0, 2.0, 1.9, 1.9], size=8)
leyenda("Tabla 6. Paso 2 (secuencial) vs. Paso 3 (hilos) con 1, 2 y 4 núcleos disponibles.")
imagen("speedup_nucleos.png", "Figura 18. Speedup de la versión con hilos según el número de núcleos. "
       "Por encima de 1 los hilos ayudan; por debajo, estorban.")

h2("5.6 Conclusiones del Paso 3")
par("Comparando con la evidencia del Paso 2, la respuesta a si ejecutar con hilos es más eficiente, igual o peor "
    "es: **depende del tamaño del problema y del número de núcleos**.")
vinetas([
    f"**Multinúcleo y N grande → más eficiente.** Con 2 o más núcleos y N ≥ ~2,500 los hilos son más rápidos. "
    f"Para N = 50,000 el Paso 3 tardó {M4[50000]['ms_paso3']:.0f} ms contra {M4[50000]['ms_paso2']:.0f} ms del "
    f"Paso 2 (≈{M4[50000]['speedup_p2_vs_p3']:.1f}x) y contra {M4[50000]['ms_paso1']:.0f} ms del Paso 1 "
    f"(≈{M4[50000]['speedup_p1_vs_p3']:.1f}x). Es decir: dividir el problema da ≈2x y paralelizarlo da otro ≈2x.",
    "**N pequeño → peor.** Crear e iniciar un hilo del sistema operativo cuesta del orden de 0.2–0.4 ms. Con "
    "10–1,000 elementos ordenar tarda menos que eso, así que la versión con hilos llega a ser más de 100 veces más lenta. "
    "El paralelismo solo conviene cuando cada hilo tiene suficiente trabajo para compensar el costo de crearlo.",
    "**Single-core → no mejora (igual o un poco peor).** Con un solo núcleo los dos hilos no pueden correr al "
    "mismo tiempo: el planificador del SO los alterna (time-slicing) con cambios de contexto. El trabajo total "
    f"es el mismo que en el Paso 2, más el costo de crear hilos y de los cambios de contexto; por eso el speedup "
    f"medido quedó entre {min(M1[n]['speedup_p2_vs_p3'] for n in TAMANOS if n >= 5000):.2f}x y "
    f"{max(M1[n]['speedup_p2_vs_p3'] for n in TAMANOS if n >= 5000):.2f}x para N ≥ 5,000. Aun así, el Paso 3 "
    "en un solo núcleo sigue siendo más rápido que el Paso 1, porque conserva la ventaja algorítmica de dividir.",
    "**Dual-core → hasta ≈2x.** Con dos núcleos cada hilo tiene su propio núcleo y ambas mitades se ordenan "
    f"realmente al mismo tiempo. Para N = 50,000 el speedup fue {M2[50000]['speedup_p2_vs_p3']:.2f}x, muy cerca "
    "del máximo teórico de 2x. No llega exactamente a 2 porque dividir, crear hilos y el merge son partes "
    "secuenciales (Ley de Amdahl) y porque las mitades pueden tener distinta cantidad de inversiones, entonces un "
    "hilo termina antes y el otro marca el tiempo.",
    "**Más de 2 núcleos no ayuda más.** Con 4 núcleos el speedup fue prácticamente el mismo que con 2, porque el "
    "programa solo crea 2 hilos: los otros núcleos quedan sin trabajo. Para aprovecharlos habría que dividir en "
    "más partes (por ejemplo, tantas como `availableProcessors()`).",
    "Los valores mayores a 2x en algunos tamaños intermedios (5,000–10,000) se explican porque cada núcleo tiene "
    "su propia caché L1/L2: al repartir las mitades en dos núcleos, cada mitad cabe mejor en caché. También hay "
    "variación normal entre mediciones.",
])

h2("5.7 Demostración de una condición de carrera")
par("Durante el desarrollo se probó primero usar un **único contador estático compartido** por ambos hilos. El "
    "resultado era incorrecto y cambiaba en cada ejecución. Para demostrarlo se dejó la opción `--compartido`, "
    "que además del contador propio de cada hilo incrementa un contador global sin sincronizar:")
bloque(txt("paso3_carrera.txt"), oscuro=True, size=6.8)
leyenda("Figura 19. El contador compartido pierde millones de incrementos por la condición de carrera.")
par("La instrucción `contadorCompartido++` parece una sola operación, pero en realidad son tres: leer el valor, "
    "sumarle 1 y escribirlo. Si los dos hilos leen el mismo valor al mismo tiempo, los dos escriben el mismo "
    "resultado y se pierde un incremento. Esto es una **condición de carrera** sobre una **sección crítica**, "
    "el mismo problema que se estudia en la teoría del curso. Las soluciones posibles son `synchronized`, "
    "`AtomicLong` o, la que se usó aquí, **no compartir el dato**: cada hilo cuenta en su propia variable y el "
    "main suma los dos resultados después del `join()`, lo cual es correcto y además no pierde rendimiento.")

# ---------------------------------------------------------------- 6
h1("6. Comentarios de implementación y dificultades encontradas")
vinetas([
    "**Código del enunciado con saltos de línea rotos.** Al copiar el código desde el PDF, el texto "
    "\"Values Before the sort:\\n\" quedó partido en dos líneas (un String no puede tener un salto de línea "
    "real en Java) y `j++` aparecía como `j+` y `+` en líneas separadas. Hubo que reconstruir esas líneas para "
    "que compilara.",
    "**Tamaño impar.** El enunciado sugiere llamar `bubble_srt(right, N/2)` y `bubble_srt(left, N/2)`, pero si N "
    "es impar, N/2 redondea hacia abajo y se pierde un elemento. Se resolvió dejando la mitad derecha con "
    "tamaño N − N/2.",
    "**Condición de carrera con el contador** (sección 5.7). Se solucionó con un contador por hilo.",
    "**start() vs. run().** Si se llama `hilo.run()` en lugar de `hilo.start()`, el código se ejecuta en el hilo "
    "main de forma secuencial y no hay paralelismo (el programa funciona, pero no mejora). Es un error fácil de "
    "cometer y difícil de notar sin medir el tiempo.",
    "**Olvidar join().** Sin `join()`, el main hace el merge mientras los hilos todavía están ordenando y el "
    "resultado sale desordenado. Por eso cada programa verifica al final que el arreglo quedó ordenado.",
    "**Medición de tiempos poco confiable.** Las primeras mediciones variaban mucho entre ejecuciones porque "
    "Java compila el código \"en caliente\" (JIT) y el sistema operativo tiene otros procesos. Se resolvió con: "
    "`System.nanoTime()` en lugar de `currentTimeMillis()`, una fase de calentamiento, 5 repeticiones con "
    "mediana y la misma semilla aleatoria para las tres versiones.",
    "**Desbordamiento de enteros.** Al calcular el valor teórico n(n−1)/4 con `int`, para N = 50,000 el resultado "
    "salió negativo, porque 50,000 × 49,999 ≈ 2,500 millones no cabe en un `int` (máximo ≈ 2,147 millones). Se "
    "corrigió usando `long` (`n * (n - 1L) / 4.0`). Por la misma razón los contadores de intercambios son `long`.",
    "**Simular single-core/dual-core.** No se contaba con máquinas de 1 y 2 núcleos, así que se usó la afinidad de "
    "CPU (`taskset` en Linux, `start /affinity` en Windows) para que el sistema operativo solo planifique el "
    "proceso en esos núcleos. Se verificó con `Runtime.getRuntime().availableProcessors()`.",
])

# ---------------------------------------------------------------- 7
h1("7. Conclusiones generales")
vinetas([
    "Bubble Sort hace en promedio n(n−1)/4 intercambios (uno por cada inversión) y su tiempo crece de forma "
    "cuadrática: multiplicar los datos por 10 multiplica el trabajo por ~100.",
    "Dividir el problema en dos mitades y mezclarlas reduce el trabajo a la mitad aun sin paralelismo, porque "
    "2·(N/2)² = N²/2 y el merge resuelve las inversiones cruzadas en tiempo lineal. Es la base de Merge Sort.",
    "Ejecutar las mitades en hilos separados solo mejora el tiempo si existen núcleos libres para ejecutarlos al "
    "mismo tiempo y si el trabajo de cada hilo es mucho mayor que el costo de crearlo. En este experimento, con "
    "2 núcleos se obtuvo casi el máximo teórico de 2x; con 1 núcleo, ninguna mejora.",
    "Combinando las dos ideas (dividir + paralelizar) la versión final fue ≈4 veces más rápida que el Bubble Sort "
    "original para N grandes.",
    "Los hilos comparten memoria, lo que es cómodo pero peligroso: cualquier dato que dos hilos modifiquen a la vez "
    "necesita sincronización o, mejor aún, diseñarse para no compartirse.",
    "Esto conecta con la gestión de procesos del sistema operativo: los hilos de Java son hilos del SO y es el "
    "planificador del sistema operativo quien decide en qué núcleo corre cada uno.",
])

# ---------------------------------------------------------------- 8
h1("8. Guía para demostrar el proyecto paso a paso")
par("Orden sugerido para presentar el proyecto en vivo (toma unos 5 minutos):")
vinetas([
    "Abrir una terminal en la carpeta `src` y compilar: `javac *.java`.",
    "**Paso 1:** `java bubbleSort` → mostrar el arreglo antes/después y los 16 intercambios. Luego "
    "`java bubbleSort 10 100 1000 10000` → señalar que ×10 datos ≈ ×100 intercambios.",
    "**Paso 2:** `java bubbleSortDividido` → mostrar las dos mitades ordenadas, el merge y que ahora son 6 "
    "intercambios. Luego `java bubbleSortDividido 10 100 1000 10000` → los intercambios bajan a la mitad.",
    "**Paso 3:** `java bubbleSortHilos 10 100 1000 10000` → mismos intercambios que el Paso 2, pero menos tiempo "
    "para 10,000 y más tiempo para 10.",
    "Abrir el Administrador de tareas (Windows) o `htop` (Linux) y correr `java bubbleSortDividido 50000` y luego "
    "`java bubbleSortHilos 50000`: con el Paso 2 se ve un solo núcleo al 100 %, con el Paso 3 se ven dos.",
    "**Comparación completa:** `java Comparacion` → tabla con los tres pasos y archivo `resultados.csv` "
    "(se abre en Excel para hacer las gráficas).",
    "**Single-core:** `taskset -c 0 java Comparacion r1.csv 3` (Linux) o `start /affinity 1 /wait java "
    "Comparacion r1.csv 3` (Windows) → los hilos ya no ayudan.",
    "**Condición de carrera:** `java bubbleSortHilos --compartido 10000` → el contador compartido pierde "
    "incrementos y el valor cambia en cada ejecución.",
], numerada=True)

# ---------------------------------------------------------------- Anexos
salto_pagina()
h1("Anexo A – Código fuente completo")
for archivo, desc in [("bubbleSort.java", "Paso 1"), ("bubbleSortDividido.java", "Paso 2"),
                      ("bubbleSortHilos.java", "Paso 3"), ("Comparacion.java", "Experimento comparativo")]:
    h2(f"{archivo}  ({desc})")
    bloque(fuente(archivo), size=7.5)

h1("Anexo B – Salida completa de los experimentos")
for archivo, desc in [("comparacion_multicore.txt", "4 núcleos"), ("comparacion_2nucleos.txt", "2 núcleos (taskset -c 0,1)"),
                      ("comparacion_1nucleo.txt", "1 núcleo (taskset -c 0)")]:
    h2(f"Comparación con {desc}")
    bloque(txt(archivo), oscuro=True, size=5.5)

doc.save(SALIDA)
print("Informe generado:", SALIDA)
