import java.util.Random;

/**
 * PASO 1 - Bubble Sort clasico (secuencial) con contador de intercambios.
 *
 * Uso:
 *   java bubbleSort                   -> ejecuta el ejemplo original de 8 numeros
 *   java bubbleSort 10 100 1000 10000 -> ordena arreglos aleatorios de esos tamanos
 *                                         y reporta intercambios y tiempo
 *
 * Autor: Joed Francisco Sosa Castellanos - 12211012
 */
public class bubbleSort {

    public static void main(String a[]) {
        if (a.length == 0) {
            ejemploOriginal();
        } else {
            for (String arg : a) {
                probarConTamano(Integer.parseInt(arg));
            }
        }
    }

    /** El programa del enunciado, ahora reportando el numero de intercambios. */
    public static void ejemploOriginal() {
        int i;
        int array[] = {12, 9, 4, 99, 120, 1, 3, 10};

        System.out.println("Values Before the sort:\n");
        for (i = 0; i < array.length; i++)
            System.out.print(array[i] + " ");
        System.out.println();

        long intercambios = bubble_srt(array, array.length);

        System.out.print("Values after the sort:\n");
        for (i = 0; i < array.length; i++)
            System.out.print(array[i] + " ");
        System.out.println();
        System.out.println("Numero de intercambios: " + intercambios);
        System.out.println("PAUSE");
    }

    /** Genera un arreglo aleatorio de tamano n, lo ordena y reporta resultados. */
    public static void probarConTamano(int n) {
        int[] array = generarArreglo(n);
        if (n <= 20) imprimir("Antes:   ", array);

        long inicio = System.nanoTime();
        long intercambios = bubble_srt(array, array.length);
        long fin = System.nanoTime();

        if (n <= 20) imprimir("Despues: ", array);
        System.out.printf("N=%6d | intercambios=%,11d | %9.3f ms | ordenado=%s%n",
                n, intercambios, (fin - inicio) / 1e6, estaOrdenado(array));
    }

    /**
     * Bubble sort del enunciado. La unica modificacion es la variable
     * "intercambios", que se incrementa cada vez que se hace un swap.
     */
    public static long bubble_srt(int a[], int n) {
        int i, j, t = 0;
        long intercambios = 0;
        for (i = 0; i < n; i++) {
            for (j = 1; j < (n - i); j++) {
                if (a[j - 1] > a[j]) {
                    /* Inicio del intercambio */
                    t = a[j - 1];
                    a[j - 1] = a[j];
                    a[j] = t;
                    /* Final del intercambio */
                    intercambios++;
                }
            }
        }
        return intercambios;
    }

    /** Arreglo pseudoaleatorio reproducible: la misma n genera siempre los mismos datos. */
    public static int[] generarArreglo(int n) {
        Random r = new Random(12345L + n);
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
        System.out.print(etiqueta);
        for (int x : arr) System.out.print(x + " ");
        System.out.println();
    }
}
