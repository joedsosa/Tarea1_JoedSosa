/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Main.java to edit this template
 */
package tarea1_joedsosa;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.Scanner;

/**
 *
 * @author joeds
 */
public class Tarea1_JoedSosa {

    /**
     * @param args the command line arguments
     */
    static ArrayList<Carro> car = new ArrayList<>();
    public static void main(String[] args) {
        // TODO code application logic here
        Menu();
    }

    public static void Menu() {
        Scanner cathy = new Scanner(System.in);
      

        int opc;
        do {
            System.out.println("##############################");
            System.out.println("#############MENU#############");
            System.out.println("####Ingrese la Opcion que desea#####");
            System.out.println("1. Anadir Vehiculo");
            System.out.println("2. Mostrar Vehiculos");
            System.out.println("3. Modificar Fecha Creacion");
            System.out.println("4. Modificar Minutos");
            System.out.println("5. Eliminar Vehiculo");
            System.out.println("6. Salir");
            opc = cathy.nextInt();
            switch (opc) {

                case 1:addCar(car);{
                    break;
                }
                
                case 2: System.out.println(car); {
                    break;
                }
                
                case 3: System.out.println(modificarDate(car));{
                    break;
                }
                case 4: System.out.println(modificarMin(car));{
                    break;
                }
                case 5: removeCar(car);{
                    break;
                }
                case 6: System.out.println("Esta fuera");
                     break;
                
            }
            
            
        } while (opc <= 5);
    }

    public static void addCar(ArrayList carList) {
        Scanner cathy2 = new Scanner(System.in);
        
            System.out.println("Ingrese la marca del carro:");
            String brand = cathy2.nextLine();
            System.out.println("Ingrese el modelo del carro:");
            String model = cathy2.nextLine();
            System.out.println("Ingrese el color del carro:");
            String color = cathy2.nextLine();
            System.out.println("Ingrese la fecha de creación:");
            Date creation = Dategen();
            Date sold = new Date();
        Carro car = 
                new Carro(creation, sold, brand, model, color);
                carList.add(car);

    }
    
    public static void removeCar(ArrayList carList) {
        Scanner sc = new Scanner(System.in);
        System.out.println("Ingrese el que desea remover/eliminar");
         int numero = sc.nextInt();
            int posiLista = numero - 1;
                carList.remove(posiLista);
    }

    public static Date Dategen() {
        Scanner sc1 = new Scanner(System.in);
        System.out.println("Ingrese la fecha  en el siguiente formato dd/MM/yyyy");
        System.out.println("dd: ");
            int d = sc1.nextInt();
        System.out.println("MM: ");
            int m = sc1.nextInt() - 1;
        System.out.println("yyyy: ");
            int y = sc1.nextInt();
        System.out.println("Ingrese la hora de creacion: ");
        
        Calendar calendario = new GregorianCalendar(y, m, d);
        Date date = calendario.getTime();
                return date;
    }

    public static String modificarDate(ArrayList carList) {
        Scanner entrada = new Scanner(System.in);
        System.out.println("Ingrese cual desea modificar:");
        System.out.println(car);
         int num = entrada.nextInt();
            int numLista = num - 1;
        Carro car = (Carro) carList.get(numLista);
            car.setCreado(Dategen());
            System.out.println(car.getCreado());
            System.out.println(car.getBrand());
                return "Fecha modificada a: " + car.getCreado();
    }

    public static String modificarMin(ArrayList carList) {
        Scanner cathy3 = new Scanner(System.in);
        System.out.println("Ingrese cual desea modificar :");
        System.out.println(car);
            int num = cathy3.nextInt();
            int posiLista = num - 1;
        System.out.println("Ingrese el minuto a modificar:  ");
            int min = cathy3.nextInt();
        Carro car = (Carro) carList.get(posiLista);
        car.getVenta().setMinutes(min);
                return "La nueva hora es:  " + car.getVenta();
    }

    

}
