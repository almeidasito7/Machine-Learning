package com.agro.commodity.model;

public enum CommodityType {
    GRAOS("Grãos"),
    FIBRAS("Fibras"),
    ACUCAR_ALCOOL("Açúcar e Álcool"),
    CARNES("Carnes"),
    CAFE("Café"),
    FRUTAS("Frutas e Vegetais"),
    OLEOS("Óleos Vegetais"),
    OUTROS("Outros");

    private final String label;

    CommodityType(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }
}
