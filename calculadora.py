class Validacion:

    def validar_precio(self, precio):
        if precio <= 0:
            return False
        return True

    def validar_descuento(self, descuento):
        if descuento < 0 or descuento > 100:
            return False
        return True


class CalculadoraDescuento:

    def calcular_descuento(self, precio, descuento):
        return precio * (1 - descuento / 100)

    def aplicar_descuento_adicional(self, precio, descuento):
        if descuento >= 80:
            precio = precio * 0.95
        return precio

    def redondear_precio(self, precio):
        return round(precio, 2)


class MostrarResultado:

    def mostrar(self, resultado):
        print("Precio final:", resultado)


# Programa principal

precio = float(input("Ingrese el precio original: "))
descuento = float(input("Ingrese el descuento (%): "))

# Objetos
validacion = Validacion()
calculadora = CalculadoraDescuento()
mostrar = MostrarResultado()

# Validaciones
if not validacion.validar_precio(precio):
    print("Error: el precio debe ser positivo")

elif not validacion.validar_descuento(descuento):
    print("Error: el descuento debe estar entre 0 y 100")

else:
    # Calcular descuento
    precio_final = calculadora.calcular_descuento(precio, descuento)

    # Aplicar descuento adicional
    precio_final = calculadora.aplicar_descuento_adicional(precio_final, descuento)

    # Redondear
    precio_final = calculadora.redondear_precio(precio_final)

    # Mostrar resultado
    mostrar.mostrar(precio_final)