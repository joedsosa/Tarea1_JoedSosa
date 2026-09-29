"""Genera las graficas del informe a partir de los CSV que produce Comparacion.java."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, "..", "resultados")
OUT = os.path.join(BASE, "img")
os.makedirs(OUT, exist_ok=True)

def leer(nombre):
    with open(os.path.join(RES, nombre)) as f:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]

multi, dos, uno = leer("resultados_multicore.csv"), leer("resultados_2nucleos.csv"), leer("resultados_1nucleo.csv")
col = lambda d, k: [r[k] for r in d]
miles = FuncFormatter(lambda x, _: f"{x:,.0f}")
AZUL, NARANJA, VERDE, GRIS = "#2F5496", "#E07B39", "#3A9D5D", "#888888"

def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, nombre), dpi=160)
    plt.close(fig)

# --- Paso 1: intercambios vs N (hasta 10,000, escala lineal) ---
hasta = [r for r in multi if r["N"] <= 10000]
N = col(hasta, "N")
fig, ax = plt.subplots(figsize=(7.5, 4.3))
ax.plot(N, col(hasta, "intercambios_paso1"), "o-", color=AZUL, label="Intercambios medidos (Paso 1)")
ax.plot(N, col(hasta, "teorico_n(n-1)/4"), "--", color=GRIS, label="Teórico  n(n−1)/4")
for n, y in zip(N, col(hasta, "intercambios_paso1")):
    if n in (1000, 5000, 10000):
        ax.annotate(f"{y:,.0f}", (n, y), textcoords="offset points", xytext=(-8, -4), ha="right", va="bottom", fontsize=8)
ax.set_xlabel("Número de elementos (N)"); ax.set_ylabel("Intercambios")
ax.set_title("Paso 1 – Intercambios del Bubble Sort vs. tamaño del arreglo")
ax.yaxis.set_major_formatter(miles); ax.xaxis.set_major_formatter(miles)
ax.grid(alpha=.3); ax.legend()
guardar(fig, "paso1_intercambios.png")

# --- Paso 1: tiempo vs N ---
fig, ax = plt.subplots(figsize=(7.5, 4.3))
ax.plot(N, col(hasta, "ms_paso1"), "o-", color=AZUL)
ax.set_xlabel("Número de elementos (N)"); ax.set_ylabel("Tiempo (ms, mediana de 5)")
ax.set_title("Paso 1 – Tiempo de ejecución del Bubble Sort")
ax.xaxis.set_major_formatter(miles); ax.grid(alpha=.3)
guardar(fig, "paso1_tiempo.png")

# --- Paso 2: intercambios Paso 1 vs Paso 2 ---
fig, ax = plt.subplots(figsize=(7.5, 4.3))
ax.plot(N, col(hasta, "intercambios_paso1"), "o-", color=AZUL, label="Paso 1 – arreglo completo")
ax.plot(N, col(hasta, "intercambios_paso2"), "s-", color=NARANJA, label="Paso 2 – dos mitades + merge")
ax.set_xlabel("Número de elementos (N)"); ax.set_ylabel("Intercambios")
ax.set_title("Paso 2 – Intercambios: arreglo completo vs. dividido en dos")
ax.yaxis.set_major_formatter(miles); ax.xaxis.set_major_formatter(miles)
ax.grid(alpha=.3); ax.legend()
guardar(fig, "paso2_intercambios.png")

# --- Tiempos de las 3 versiones (4 nucleos), log-log ---
Nall = col(multi, "N")
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.loglog(Nall, col(multi, "ms_paso1"), "o-", color=AZUL, label="Paso 1 – secuencial")
ax.loglog(Nall, col(multi, "ms_paso2"), "s-", color=NARANJA, label="Paso 2 – dividido (secuencial)")
ax.loglog(Nall, col(multi, "ms_paso3"), "^-", color=VERDE, label="Paso 3 – dividido con 2 hilos")
ax.set_xlabel("Número de elementos (N) – escala log"); ax.set_ylabel("Tiempo (ms) – escala log")
ax.set_title("Tiempo de ejecución de las tres versiones (CPU de 4 núcleos)")
ax.grid(alpha=.3, which="both"); ax.legend()
guardar(fig, "tiempos_tres_versiones.png")

# --- Speedup de hilos (Paso2/Paso3) segun nucleos ---
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.semilogx(Nall, col(uno, "speedup_p2_vs_p3"), "o-", color="#C0392B", label="1 núcleo (single-core)")
ax.semilogx(Nall, col(dos, "speedup_p2_vs_p3"), "s-", color=NARANJA, label="2 núcleos (dual-core)")
ax.semilogx(Nall, col(multi, "speedup_p2_vs_p3"), "^-", color=VERDE, label="4 núcleos")
ax.axhline(1, color=GRIS, ls="--", lw=1); ax.axhline(2, color=GRIS, ls=":", lw=1)
ax.text(Nall[0], 1.04, "igual que secuencial", fontsize=8, color=GRIS)
ax.text(Nall[0], 2.04, "máximo teórico con 2 hilos", fontsize=8, color=GRIS)
ax.set_xlabel("Número de elementos (N) – escala log"); ax.set_ylabel("Speedup = tiempo Paso 2 / tiempo Paso 3")
ax.set_title("Paso 3 – Aceleración obtenida con hilos según núcleos disponibles")
ax.set_ylim(0, 3.4); ax.grid(alpha=.3, which="both"); ax.legend(loc="upper left", ncol=3, fontsize=8)
guardar(fig, "speedup_nucleos.png")
print("Graficas generadas en", OUT)
