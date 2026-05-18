# Práctica de Aula: Calculadora de Descuentos

Este proyecto implementa una función en Python para calcular el precio final de un producto después de aplicar un descuento porcentual. El desarrollo se ha realizado utilizando la metodología **TDD (Test-Driven Development)** y está completamente dockerizado para garantizar la consistencia del entorno entre diferentes desarrolladores.

## Contexto

Una tienda necesita una función `calcular_precio_final(precio_original, descuento)` que calcule el precio final después de aplicar un descuento porcentual. Los requisitos aumentan en complejidad e incluyen validación de datos y reglas de negocio específicas.

## Requisitos (Reglas de Negocio)

La función cumple con los siguientes requisitos (R1 - R5):

* **R1:** El descuento debe estar entre 0 y 100. De lo contrario, levanta un error (`ValueError`).
* **R2:** El precio original debe ser un valor positivo. De lo contrario, levanta un error (`ValueError`).
* **R3:** Calcula el precio final usando la fórmula: `precio_final = precio_original * (1 - descuento/100)`.
* **R4:** El resultado se redondea siempre a 2 decimales.
* **R5:** Si el descuento es $\ge$ 80%, se aplica un descuento adicional del 5% sobre el precio ya descontado.

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.14.5
* **Testing:** `pytest` (Desarrollo guiado por pruebas - TDD)
* **Contenedores:** Docker (Imagen base: `python:3.14.5-alpine`)

## Estructura del Proyecto

```text
.
├── test/
│   └── test_calculadora.py   # Archivos de pruebas unitarias
├── calculadora.py            # Lógica principal de la función
├── Dockerfile                # Configuración del contenedor
├── requirements.txt          # Dependencias del proyecto (pytest)
└── README.md                 # Documentación del proyecto
```

## Instrucciones para Ejejcutar el Proyecto

Gracias a la dockerizacion, puedes ejecutar el proyecto sin preocuparte por las dependencias. Sigue estos pasos:

1. **Construir la imagen de Docker:**
```bash
docker build -t calculadora-tdd.
```
2. **Ejecutar los tests dentro del contenedor:**
```bash
docker run --rm calculadora-tdd pytest
```

