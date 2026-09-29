import java.util.Random;

public class bubbleSortDividido {

    public static void main(String a[]) {
        if (a.length == 0) {
            int array[] = {12, 9, 4, 99, 120, 1, 3, 10};
            ordenarYReportar(array, true);
        } else {
            for (String arg : a) {
                int n = Integer.parseInt(arg);
                ordenarYReportar(generarArreglo(n), n <= 20);
            }
        }
    }

    public static void ordenarYReportar(int[] array, boolean mostrar) {
        int n = array.length;
        if (mostrar) imprimir("Antes:          ", array);

        long inicio = System.nanoTime();
        int mitad = n / 2;
        int left_array[] = new int[mitad];
        int right_array[] = new int[n - mitad];
        System.arraycopy(array, 0, left_array, 0, mitad);
        System.arraycopy(array, mitad, right_array, 0, n - mitad);

        long intIzq = bubble_srt(left_array, left_array.length);
        long intDer = bubble_srt(right_array, right_array.length);

        int[] resultado = merge(left_array, right_array);

        long fin = System.nanoTime();

        if (mostrar) {
            imprimir("Mitad izquierda:", left_array);
            imprimir("Mitad derecha:  ", right_array);
            imprimir("Despues (merge):", resultado);
        }
        System.out.printf("N=%6d | intercambios izq=%,10d der=%,10d total=%,11d | %9.3f ms | ordenado=%s%n",
                n, intIzq, intDer, intIzq + intDer, (fin - inicio) / 1e6, estaOrdenado(resultado));
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
        Random r = new Random(12345L + n); // misma semilla que el Paso 1 -> mismos datos
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
