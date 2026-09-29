import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;


public class Comparacion {

    static final int[] TAMANOS_DEFECTO = {10, 50, 100, 250, 500, 750, 1000, 2500, 5000, 7500, 10000, 20000, 50000};

    public static void main(String[] args) throws Exception {
        String archivo = args.length > 0 ? args[0] : "resultados.csv";
        int repeticiones = args.length > 1 ? Integer.parseInt(args[1]) : 5;
        int[] tamanos = TAMANOS_DEFECTO;
        if (args.length > 2) {
            tamanos = new int[args.length - 2];
            for (int i = 2; i < args.length; i++) tamanos[i - 2] = Integer.parseInt(args[i]);
        }

        System.out.println("Nucleos disponibles para la JVM: " + Runtime.getRuntime().availableProcessors());
        System.out.println("Repeticiones por medicion: " + repeticiones + " (se reporta la mediana)");
        calentarJVM();

        System.out.printf("%n%7s | %12s | %12s | %12s | %12s | %12s | %10s | %10s | %10s | %8s | %8s%n",
                "N", "inversiones", "n(n-1)/4", "int. Paso1", "int. Paso2", "int. Paso3",
                "ms Paso1", "ms Paso2", "ms Paso3", "P1/P2", "P2/P3");

        try (PrintWriter csv = new PrintWriter(new FileWriter(archivo))) {
            csv.println("N,inversiones,teorico_n(n-1)/4,intercambios_paso1,intercambios_paso2,intercambios_paso3,"
                    + "ms_paso1,ms_paso2,ms_paso3,speedup_p1_vs_p2,speedup_p2_vs_p3,speedup_p1_vs_p3");
            for (int n : tamanos) {
                int[] original = bubbleSort.generarArreglo(n);
                int[] esperado = original.clone();
                Arrays.sort(esperado);

                long inversiones = contarInversiones(original.clone());
                double teorico = n * (n - 1L) / 4.0;

                long[] r1 = new long[1], r2 = new long[1], r3 = new long[1];
                double[] t1 = new double[repeticiones], t2 = new double[repeticiones], t3 = new double[repeticiones];
                for (int k = 0; k < repeticiones; k++) {
                    t1[k] = medirPaso1(original, esperado, r1);
                    t2[k] = medirPaso2(original, esperado, r2);
                    t3[k] = medirPaso3(original, esperado, r3);
                }
                double m1 = mediana(t1), m2 = mediana(t2), m3 = mediana(t3);

                System.out.printf("%7d | %,12d | %,12.0f | %,12d | %,12d | %,12d | %10.3f | %10.3f | %10.3f | %7.2fx | %7.2fx%n",
                        n, inversiones, teorico, r1[0], r2[0], r3[0], m1, m2, m3, m1 / m2, m2 / m3);
                csv.printf(java.util.Locale.US, "%d,%d,%.1f,%d,%d,%d,%.4f,%.4f,%.4f,%.3f,%.3f,%.3f%n",
                        n, inversiones, teorico, r1[0], r2[0], r3[0], m1, m2, m3, m1 / m2, m2 / m3, m1 / m3);
            }
        }
        System.out.println("\nResultados guardados en " + archivo);
    }

    static double medirPaso1(int[] original, int[] esperado, long[] intercambios) {
        int[] a = original.clone();
        long ini = System.nanoTime();
        intercambios[0] = bubbleSort.bubble_srt(a, a.length);
        long fin = System.nanoTime();
        verificar(a, esperado, "Paso 1");
        return (fin - ini) / 1e6;
    }

    static double medirPaso2(int[] original, int[] esperado, long[] intercambios) {
        int[] a = original.clone();
        long ini = System.nanoTime();
        int mitad = a.length / 2;
        int[] left = Arrays.copyOfRange(a, 0, mitad);
        int[] right = Arrays.copyOfRange(a, mitad, a.length);
        long i1 = bubbleSortDividido.bubble_srt(left, left.length);
        long i2 = bubbleSortDividido.bubble_srt(right, right.length);
        int[] res = bubbleSortDividido.merge(left, right);
        long fin = System.nanoTime();
        intercambios[0] = i1 + i2;
        verificar(res, esperado, "Paso 2");
        return (fin - ini) / 1e6;
    }

    static double medirPaso3(int[] original, int[] esperado, long[] intercambios) {
        int[] a = original.clone();
        long ini = System.nanoTime();
        int mitad = a.length / 2;
        int[] left = Arrays.copyOfRange(a, 0, mitad);
        int[] right = Arrays.copyOfRange(a, mitad, a.length);
        bubbleSortHilos.HiloOrdenador h1 = new bubbleSortHilos.HiloOrdenador("Hilo-Izquierdo", left);
        bubbleSortHilos.HiloOrdenador h2 = new bubbleSortHilos.HiloOrdenador("Hilo-Derecho", right);
        h1.start();
        h2.start();
        try {
            h1.join();
            h2.join();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        int[] res = bubbleSortHilos.merge(left, right);
        long fin = System.nanoTime();
        intercambios[0] = h1.intercambios + h2.intercambios;
        verificar(res, esperado, "Paso 3");
        return (fin - ini) / 1e6;
    }

    static void calentarJVM() {
        int[] datos = bubbleSort.generarArreglo(3000);
        int[] esp = datos.clone();
        Arrays.sort(esp);
        long[] dummy = new long[1];
        for (int i = 0; i < 10; i++) {
            medirPaso1(datos, esp, dummy);
            medirPaso2(datos, esp, dummy);
            medirPaso3(datos, esp, dummy);
        }
    }

    static void verificar(int[] obtenido, int[] esperado, String paso) {
        if (!Arrays.equals(obtenido, esperado))
            throw new IllegalStateException(paso + " no ordeno correctamente");
    }

    static double mediana(double[] v) {
        double[] c = v.clone();
        Arrays.sort(c);
        int m = c.length / 2;
        return c.length % 2 == 1 ? c[m] : (c[m - 1] + c[m]) / 2.0;
    }


    static long contarInversiones(int[] a) {
        if (a.length < 2) return 0;
        int mitad = a.length / 2;
        int[] izq = Arrays.copyOfRange(a, 0, mitad);
        int[] der = Arrays.copyOfRange(a, mitad, a.length);
        long inv = contarInversiones(izq) + contarInversiones(der);
        int i = 0, j = 0, k = 0;
        while (i < izq.length && j < der.length) {
            if (izq[i] <= der[j]) a[k++] = izq[i++];
            else {
                a[k++] = der[j++];
                inv += izq.length - i;
            }
        }
        while (i < izq.length) a[k++] = izq[i++];
        while (j < der.length) a[k++] = der[j++];
        return inv;
    }
}
