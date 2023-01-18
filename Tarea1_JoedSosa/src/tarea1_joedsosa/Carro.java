/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package tarea1_joedsosa;

import java.util.Date;

/**
 *
 * @author joeds
 */
public class Carro {
    public Date Creado;
    public Date Venta;
    public String Brand;
    public String Model;
    public String Color;

    public Carro(Date Creado, Date Venta, String Brand, String Model, String Year) {
        this.Creado = Creado;
        this.Venta = Venta;
        this.Brand = Brand;
        this.Model = Model;
        this.Color = Color;
    }

    public Date getCreado() {
        return Creado;
    }

    public void setCreado(Date Creado) {
        this.Creado = Creado;
    }

    public Date getVenta() {
        return Venta;
    }

    public void setVenta(Date Venta) {
        this.Venta = Venta;
    }

    public String getBrand() {
        return Brand;
    }

    public void setBrand(String Brand) {
        this.Brand = Brand;
    }

    public String getModel() {
        return Model;
    }

    public void setModel(String Model) {
        this.Model = Model;
    }

    public String getColor() {
        return Color;
    }

    public void setColor(String Year) {
        this.Color = Color;
    }

    @Override
    public String toString() {
        return "Carro{" + "Creado=" + Creado + ", Venta=" + Venta + ", Brand=" + Brand + ", Model=" + Model + ", Color=" + Color + '}';
    }

   
    }
    
    
    

