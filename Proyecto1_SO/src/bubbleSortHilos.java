import java.util.Random;

/**
 * PASO 3 - Bubble Sort dividido, con cada mitad ordenada en su PROPIO HILO.
 *
 * Hilo main:  divide el arreglo -> crea hilo izquierdo y hilo derecho ->
 *             start() a ambos -> join() espera a que terminen -> merge.
 *
 * Uso:
 *   java bubbleSortHilos                   -> ejemplo de 8 numeros del enunciado
 *   java bubbleSortHilos 10 100 1000 10000 -> pruebas con arreglos aleatorios
 *   java bubbleSortHilos --compartido 10000 -> ademas usa un contador COMPARTIDO
 *                                              sin sincronizar para mostrar la
 *                                              condicion de carrera
 *
 * Autor: Joed Francisco Sosa Castellanos - 12211012
 */
public class bubbleSortHilos {

    /** Contador global compartido por ambos hilos SIN sincronizacion (solo para la demo). */
    static long contadorCompartido = 0;
    static boolean usarCompartido = false;

    /**
     * Hilo que ordena una mitad del arreglo. Cada hilo guarda sus
     * intercambios en su propia variable, asi no hay datos compartidos.
     */
    static class HiloOrdenador extends Thread {
        private final int[] arreglo;
        long intercambios = 0;

        HiloOrdenador(String nombre, int[] arreglo) {
            super(nombre);
            this.arreglo = arreglo;
        }

        @Override
        public void run() {
            intercambios = bubble_srt(arreglo, arreglo.length);
        }
    }

    public static void main(String a[]) throws InterruptedException {
        int idx = 0;
        if (a.length > 0 && a[0].equals("--compartido")) {
            usarCompartido = true;
            idx = 1;
        }
        System.out.println("Nucleos disponibles para la JVM: " + Runtime.getRuntime().availableProcessors());
        if (idx == a.length) {
            int array[] = {12, 9, 4, 99, 120, 1, 3, 10};
            ordenarYReportar(array, true);
        } else {
            for (int k = idx; k < a.length; k++) {
                int n = Integer.parseInt(a[k]);
                ordenarYReportar(generarArreglo(n), n <= 20);
            }
        }
    }

    public static void ordenarYReportar(int[] array, boolean mostrar) throws InterruptedException {
        int n = array.length;
        contadorCompartido = 0;
        if (mostrar) imprimir("Antes:          ", array);

        long inicio = System.nanoTime();

        // 1) Dividir
        int mitad = n / 2;
        int left_array[] = new int[mitad];
        int right_array[] = new int[n - mitad];
        System.arraycopy(array, 0, left_array, 0, mitad);
        System.arraycopy(array, mitad, right_array, 0, n - mitad);

        // 2) Crear un hilo por mitad y arrancarlos: ahora corren en paralelo
        HiloOrdenador hiloIzq = new HiloOrdenador("Hilo-Izquierdo", left_array);
        HiloOrdenador hiloDer = new HiloOrdenador("Hilo-Derecho", right_array);
        hiloIzq.start();
        hiloDer.start();

        // 3) join(): el hilo main se bloquea hasta que ambos terminen
        hiloIzq.join();
        hiloDer.join();

        // 4) Un unico merge al final
        int[] resultado = merge(left_array, right_array);

        long fin = System.nanoTime();

        if (mostrar) {
            imprimir("Mitad izquierda:", left_array);
            imprimir("Mitad derecha:  ", right_array);
            imprimir("Despues (merge):", resultado);
        }
        long total = hiloIzq.intercambios + hiloDer.intercambios;
        System.out.printf("N=%6d | intercambios izq=%,10d der=%,10d total=%,11d | %9.3f ms | ordenado=%s%n",
                n, hiloIzq.intercambios, hiloDer.intercambios, total, (fin - inicio) / 1e6, estaOrdenado(resultado));
        if (usarCompartido) {
            System.out.printf("         contador COMPARTIDO = %,d (deberia ser %,d; se perdieron %,d)%n",
                    contadorCompartido, total, total - contadorCompartido);
        }
    }

    public static long bubble_srt(int a[], int n) {
        int i, j, t = 0;
        long intercambios = 0;
        for (i = 0; i < n; i++) {
            for (j = 1; j < (n - i); j++) {
                if (a[j - 1] > a[j]) {
                    t = a[j - 1];
                    a[j - 1] = a[j];
                    a[j] = t;
                    intercambios++;
                    if (usarCompartido) contadorCompartido++; // carrera: leer-sumar-escribir no es atomico
                }
            }
        }
        return intercambios;
    }

    public static int[] merge(int[] left, int[] right) {
        int[] res = new int[left.length + right.length];
        int i = 0, j = 0, k = 0;
        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) res[k++] = left[i++];
            else res[k++] = right[j++];
        }
        while (i < left.length) res[k++] = left[i++];
        while (j < right.length) res[k++] = right[j++];
        return res;
    }

    public static int[] generarArreglo(int n) {
        Random r = new Random(12345L + n); // misma semilla que Paso 1 y Paso 2
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = r.nextInt(100000);
        return arr;
    }

    public static boolean estaOrdenado(int[] arr) {
        for (int i = 1; i < arr.length; i++)
            if (arr[i - 1] > arr[i]) return false;
        return true;
    }

    public static void imprimir(String etiqueta, int[] arr) {
        System.out.print(etiqueta + " ");
        for (int x : arr) System.out.print(x + " ");
        System.out.println();
    }
}
