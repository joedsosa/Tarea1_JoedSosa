import java.util.Random;

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
