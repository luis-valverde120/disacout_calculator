# calculadora.py
from datetime import date
from typing import Dict, Any, Tuple

# --- EXCEPCIONES ---
class CalculadoraError(Exception):
    pass

class PrecioInvalidoError(CalculadoraError):
    pass

class DescuentoInvalidoError(CalculadoraError):
    pass

class CuponInvalidoError(CalculadoraError):
    pass

# --- VALIDACION ---
class Validador:
    @staticmethod
    def validar_precio(precio: float):
        if precio <= 0:
            raise PrecioInvalidoError("El precio debe ser un valor positivo (mayor a cero).")

    @staticmethod
    def validar_descuento(descuento: float):
        if not (0 <= descuento <= 100):
            raise DescuentoInvalidoError("El descuento debe estar comprendido entre 0 y 100.")

# --- GESTOR DE CUPONES ---
class GestorCupones:
    def __init__(self):
        # Base de datos simulada de cupones:
        # Codigo: (tipo, valor, fecha_expiracion)
        self.cupones = {
            "PROMO10": ("porcentaje", 10.0, date(2099, 12, 31)),
            "FIJO15": ("fijo", 15.0, date(2099, 12, 31)),
            "EXPIRADO": ("porcentaje", 20.0, date(2020, 1, 1))
        }

    def obtener_descuento_cupon(self, codigo: str, fecha_actual: date = None) -> Tuple[str, float]:
        if fecha_actual is None:
            fecha_actual = date.today()

        if codigo not in self.cupones:
            raise CuponInvalidoError(f"El cupón '{codigo}' no existe.")

        tipo, valor, expiracion = self.cupones[codigo]
        
        if fecha_actual > expiracion:
            raise CuponInvalidoError(f"El cupón '{codigo}' ha expirado.")

        return tipo, valor

# --- FIDELIZACION ---
class ServicioFidelizacion:
    NIVELES = {
        "BRONCE": 0.0,
        "PLATA": 3.0,
        "ORO": 5.0,
        "PLATINO": 10.0
    }

    @classmethod
    def obtener_descuento_nivel(cls, nivel: str) -> float:
        return cls.NIVELES.get(nivel.upper(), 0.0)

# --- RECIBO ---
class GeneradorRecibo:
    @staticmethod
    def generar(desglose: Dict[str, Any]) -> str:
        lineas = [
            "--- RECIBO DE COMPRA ---",
            f"Precio original (x{desglose['cantidad']}): ${desglose['subtotal']:.2f}",
            f"Descuento base ({desglose['descuento_base_pct']}%): -${desglose['ahorro_base']:.2f}"
        ]
        if desglose['ahorro_volumen'] > 0:
            lineas.append(f"Descuento por volumen: -${desglose['ahorro_volumen']:.2f}")
        if desglose['ahorro_cupon'] > 0:
            lineas.append(f"Cupón aplicado: -${desglose['ahorro_cupon']:.2f}")
        if desglose['ahorro_fidelidad'] > 0:
            lineas.append(f"Beneficio fidelidad: -${desglose['ahorro_fidelidad']:.2f}")
        if desglose['ahorro_adicional_r5'] > 0:
            lineas.append(f"Descuento especial (>=80%): -${desglose['ahorro_adicional_r5']:.2f}")

        lineas.append("------------------------")
        lineas.append(f"TOTAL A PAGAR: ${desglose['precio_final']:.2f}")
        lineas.append(f"Total ahorrado: ${desglose['ahorro_total']:.2f}")
        lineas.append("========================")
        return "\n".join(lineas)

# --- CALCULADORA PRINCIPAL ---
class CalculadoraDescuento:
    def __init__(self):
        self.validador = Validador()
        self.cupones = GestorCupones()

    def calcular(self, 
                 precio: float, 
                 descuento_base: float, 
                 cantidad: int = 1, 
                 codigo_cupon: str = None, 
                 nivel_fidelidad: str = "BRONCE",
                 fecha_actual_simulada: date = None) -> Dict[str, Any]:
        
        # Validaciones R1 y R2
        self.validador.validar_precio(precio)
        self.validador.validar_descuento(descuento_base)
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser al menos 1.")

        subtotal = precio * cantidad
        precio_actual = subtotal

        # 1. Descuento Base R3
        ahorro_base = precio_actual * (descuento_base / 100)
        precio_actual -= ahorro_base

        # 2. R5: Si el descuento es >= 80%, aplicar 5% adicional
        ahorro_adicional_r5 = 0.0
        if descuento_base >= 80:
            ahorro_adicional_r5 = precio_actual * 0.05
            precio_actual -= ahorro_adicional_r5

        # 3. Descuento por Volumen
        ahorro_volumen = 0.0
        if 5 <= cantidad <= 9:
            ahorro_volumen = precio_actual * 0.05
        elif cantidad >= 10:
            ahorro_volumen = precio_actual * 0.10
        precio_actual -= ahorro_volumen

        # 4. Descuento por Nivel de Fidelidad
        pct_fidelidad = ServicioFidelizacion.obtener_descuento_nivel(nivel_fidelidad)
        ahorro_fidelidad = precio_actual * (pct_fidelidad / 100)
        precio_actual -= ahorro_fidelidad

        # 5. Cupón de Descuento
        ahorro_cupon = 0.0
        if codigo_cupon:
            tipo, valor = self.cupones.obtener_descuento_cupon(codigo_cupon, fecha_actual_simulada)
            if tipo == "porcentaje":
                ahorro_cupon = precio_actual * (valor / 100)
            elif tipo == "fijo":
                ahorro_cupon = min(valor, precio_actual)
            precio_actual -= ahorro_cupon

        # Evitar precios negativos
        precio_actual = max(0.0, precio_actual)
        
        # R4: Redondear a 2 decimales
        precio_final = round(precio_actual, 2)
        ahorro_total = round(subtotal - precio_final, 2)

        return {
            "cantidad": cantidad,
            "subtotal": round(subtotal, 2),
            "descuento_base_pct": descuento_base,
            "ahorro_base": round(ahorro_base, 2),
            "ahorro_adicional_r5": round(ahorro_adicional_r5, 2),
            "ahorro_volumen": round(ahorro_volumen, 2),
            "ahorro_fidelidad": round(ahorro_fidelidad, 2),
            "ahorro_cupon": round(ahorro_cupon, 2),
            "ahorro_total": ahorro_total,
            "precio_final": precio_final
        }


# --- FUNCION ORIGINAL POR COMPATIBILIDAD ---
def calcular_precio_final(precio_original: float, descuento: float) -> float:
    """
    Función heredada que usa la nueva arquitectura para satisfacer R1 a R5.
    Mantiene los ValueError para compatibilidad hacia atrás.
    """
    try:
        calc = CalculadoraDescuento()
        desglose = calc.calcular(precio_original, descuento)
        return desglose["precio_final"]
    except PrecioInvalidoError as e:
        raise ValueError(str(e))
    except DescuentoInvalidoError as e:
        raise ValueError(str(e))

class MostrarResultado:
    def mostrar(self, resultado):
        print("Precio final:", resultado)

if __name__ == "__main__":
    try:
        p = float(input("Ingrese el precio original: "))
        d = float(input("Ingrese el descuento (%): "))
        
        # Imprimir desglose completo usando la nueva arquitectura
        calc = CalculadoraDescuento()
        recibo_dict = calc.calcular(p, d)
        print("\n" + GeneradorRecibo.generar(recibo_dict))
        
    except Exception as e:
        print(f"Error: {e}")