# calculadora.py

def calcular_precio_final(precio_original, descuento):
    # R1: Validar que el descuento esté entre 0 y 100
    if not (0 <= descuento <= 100):
        raise ValueError("El descuento debe estar entre 0 y 100")
    
    # R2: Validar que el precio original sea positivo
    if precio_original <= 0:
        raise ValueError("El precio debe ser positivo")
        
    # R3: Calcular precio final estándar
    precio_final = precio_original * (1 - (descuento / 100))
    
    # R5: Si el descuento es >= 80%, aplicar descuento adicional del 5%
    if descuento >= 80:
        precio_final = precio_final * 0.95
        
    # R4: Redondear a 2 decimales
    return round(precio_final, 2)


class MostrarResultado:
    def mostrar(self, resultado):
        print("Precio final:", resultado)


# Programa principal interactivo
if __name__ == "__main__":
    try:
        precio = float(input("Ingrese el precio original: "))
        descuento = float(input("Ingrese el descuento (%): "))
        
        # Ejecutamos la función principal
        precio_final = calcular_precio_final(precio, descuento)
        
        # Mostramos el resultado usando la clase
        mostrar = MostrarResultado()
        mostrar.mostrar(precio_final)
        
    except ValueError as e:
        # Captura errores de validación de R1, R2 y si el usuario ingresa texto
        print(f"Error: {e}")