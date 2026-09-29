# Proyecto #1 – Sistemas Operativos I: Primeros pasos en programación concurrente

**Estudiante:** Joed Francisco Sosa Castellanos (12211012) · **Docente:** Ing. Román Pineda · **Sección:** CCC415

## Contenido

| Carpeta / archivo | Qué es |
|---|---|
| `src/bubbleSort.java` | **Paso 1** – Bubble Sort del enunciado + contador de intercambios |
| `src/bubbleSortDividido.java` | **Paso 2** – divide en `left_array` / `right_array`, ordena cada una y hace merge (secuencial) |
| `src/bubbleSortHilos.java` | **Paso 3** – cada mitad se ordena en su propio `Thread`, `join()` y un único merge |
| `src/Comparacion.java` | Corre los 3 pasos con los mismos datos, 5 repeticiones, y genera un CSV (para Excel) |
| `resultados/` | Salidas de consola (`.txt`) y tablas (`.csv`) usadas en el informe |
| `informe/Informe_Proyecto1_SO.docx` / `.pdf` | Informe final con portada |
| `informe/graficas.py`, `informe/generar_informe.py` | Scripts que generan las gráficas y el informe a partir de los resultados |

## Paso a paso

Requisito: JDK 8 o superior (`java -version`).

```bash
cd Proyecto1_SO/src
javac *.java

# Paso 1
java bubbleSort                            # ejemplo de 8 números -> 16 intercambios
java bubbleSort 10 100 1000 10000          # intercambios y tiempo para cada N

# Paso 2
java bubbleSortDividido                    # ejemplo de 8 números -> 6 intercambios
java bubbleSortDividido 10 100 1000 10000

# Paso 3
java bubbleSortHilos                       # ejemplo de 8 números con 2 hilos
java bubbleSortHilos 10 100 1000 10000
java bubbleSortHilos --compartido 10000    # demo de condición de carrera

# Comparación completa (genera resultados.csv, se abre en Excel)
java Comparacion
java Comparacion mi_archivo.csv 5 10 100 1000 10000   # archivo, repeticiones, tamaños
```

### Simular single-core y dual-core

```bash
# Linux
taskset -c 0   java Comparacion r_1nucleo.csv 5
taskset -c 0,1 java Comparacion r_2nucleos.csv 5
```
```bat
REM Windows (CMD)
start /affinity 1 /wait java Comparacion r_1nucleo.csv 5
start /affinity 3 /wait java Comparacion r_2nucleos.csv 5
```

### Regenerar gráficas e informe

```bash
pip install matplotlib python-docx
python3 informe/graficas.py
python3 informe/generar_informe.py <docx_con_la_portada.docx>
```

## Resultados principales (CPU de 4 núcleos, N = 50,000)

| Versión | Intercambios | Tiempo |
|---|---|---|
| Paso 1 – secuencial | 622,516,767 | ≈ 3.6 s |
| Paso 2 – dos mitades + merge | 311,317,434 | ≈ 1.7 s |
| Paso 3 – dos hilos + merge | 311,317,434 | ≈ 0.9 s |

Con 1 solo núcleo el Paso 3 no mejora respecto al Paso 2 (speedup 0.6x–0.95x); con 2 núcleos llega a ≈2x.
