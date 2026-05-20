# test_calculadora.py
# Pruebas unitarias para calculadora.py usando la librería unittest
import unittest
import sys
import os
from datetime import date

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculadora import (
    CalculadoraError,
    PrecioInvalidoError,
    DescuentoInvalidoError,
    CuponInvalidoError,
    Validador,
    GestorCupones,
    ServicioFidelizacion,
    GeneradorRecibo,
    CalculadoraDescuento,
    calcular_precio_final,
    MostrarResultado,
)


# ============================================================
# 1. PRUEBAS PARA LA CLASE Validador
# ============================================================
class TestValidador(unittest.TestCase):
    """Pruebas para la clase Validador."""

    # --- validar_precio ---
    def test_precio_positivo_no_lanza_excepcion(self):
        """R1: Un precio positivo no debe lanzar excepción."""
        try:
            Validador.validar_precio(100.0)
        except PrecioInvalidoError:
            self.fail("validar_precio lanzó PrecioInvalidoError con un precio válido.")

    def test_precio_cero_lanza_excepcion(self):
        """R1: Un precio igual a cero debe lanzar PrecioInvalidoError."""
        with self.assertRaises(PrecioInvalidoError):
            Validador.validar_precio(0)

    def test_precio_negativo_lanza_excepcion(self):
        """R1: Un precio negativo debe lanzar PrecioInvalidoError."""
        with self.assertRaises(PrecioInvalidoError):
            Validador.validar_precio(-50.0)

    # --- validar_descuento ---
    def test_descuento_valido_no_lanza_excepcion(self):
        """R2: Un descuento entre 0 y 100 no debe lanzar excepción."""
        try:
            Validador.validar_descuento(50.0)
        except DescuentoInvalidoError:
            self.fail("validar_descuento lanzó excepción con descuento válido.")

    def test_descuento_cero_es_valido(self):
        """R2: Un descuento de 0% es válido (sin descuento)."""
        try:
            Validador.validar_descuento(0)
        except DescuentoInvalidoError:
            self.fail("validar_descuento lanzó excepción con descuento 0.")

    def test_descuento_cien_es_valido(self):
        """R2: Un descuento de 100% es válido (gratis)."""
        try:
            Validador.validar_descuento(100)
        except DescuentoInvalidoError:
            self.fail("validar_descuento lanzó excepción con descuento 100.")

    def test_descuento_negativo_lanza_excepcion(self):
        """R2: Un descuento negativo debe lanzar DescuentoInvalidoError."""
        with self.assertRaises(DescuentoInvalidoError):
            Validador.validar_descuento(-1)

    def test_descuento_mayor_a_100_lanza_excepcion(self):
        """R2: Un descuento mayor a 100 debe lanzar DescuentoInvalidoError."""
        with self.assertRaises(DescuentoInvalidoError):
            Validador.validar_descuento(101)


# ============================================================
# 2. PRUEBAS PARA LA CLASE GestorCupones
# ============================================================
class TestGestorCupones(unittest.TestCase):
    """Pruebas para la clase GestorCupones."""

    def setUp(self):
        self.gestor = GestorCupones()

    def test_cupon_porcentaje_valido(self):
        """Un cupón de porcentaje válido devuelve tipo y valor correctos."""
        tipo, valor = self.gestor.obtener_descuento_cupon("PROMO10", date(2025, 6, 1))
        self.assertEqual(tipo, "porcentaje")
        self.assertEqual(valor, 10.0)

    def test_cupon_fijo_valido(self):
        """Un cupón de valor fijo válido devuelve tipo y valor correctos."""
        tipo, valor = self.gestor.obtener_descuento_cupon("FIJO15", date(2025, 6, 1))
        self.assertEqual(tipo, "fijo")
        self.assertEqual(valor, 15.0)

    def test_cupon_inexistente_lanza_excepcion(self):
        """Un código de cupón inexistente debe lanzar CuponInvalidoError."""
        with self.assertRaises(CuponInvalidoError):
            self.gestor.obtener_descuento_cupon("NOEXISTE", date(2025, 6, 1))

    def test_cupon_expirado_lanza_excepcion(self):
        """Un cupón expirado debe lanzar CuponInvalidoError."""
        with self.assertRaises(CuponInvalidoError):
            self.gestor.obtener_descuento_cupon("EXPIRADO", date(2025, 6, 1))

    def test_cupon_en_fecha_limite(self):
        """Un cupón usado en su fecha exacta de expiración es válido."""
        tipo, valor = self.gestor.obtener_descuento_cupon("PROMO10", date(2099, 12, 31))
        self.assertEqual(tipo, "porcentaje")

    def test_cupon_un_dia_despues_de_expiracion(self):
        """Un cupón usado un día después de expirar debe lanzar excepción."""
        with self.assertRaises(CuponInvalidoError):
            self.gestor.obtener_descuento_cupon("EXPIRADO", date(2020, 1, 2))


# ============================================================
# 3. PRUEBAS PARA LA CLASE ServicioFidelizacion
# ============================================================
class TestServicioFidelizacion(unittest.TestCase):
    """Pruebas para la clase ServicioFidelizacion."""

    def test_nivel_bronce(self):
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel("BRONCE"), 0.0)

    def test_nivel_plata(self):
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel("PLATA"), 3.0)

    def test_nivel_oro(self):
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel("ORO"), 5.0)

    def test_nivel_platino(self):
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel("PLATINO"), 10.0)

    def test_nivel_minusculas(self):
        """El nivel debe funcionar sin importar mayúsculas/minúsculas."""
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel("oro"), 5.0)

    def test_nivel_desconocido(self):
        """Un nivel no registrado devuelve 0.0 de descuento."""
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel("DIAMANTE"), 0.0)


# ============================================================
# 4. PRUEBAS PARA LA CLASE GeneradorRecibo
# ============================================================
class TestGeneradorRecibo(unittest.TestCase):
    """Pruebas para la clase GeneradorRecibo."""

    def test_recibo_basico(self):
        """Genera un recibo sin descuentos opcionales."""
        desglose = {
            "cantidad": 1,
            "subtotal": 100.0,
            "descuento_base_pct": 10,
            "ahorro_base": 10.0,
            "ahorro_volumen": 0.0,
            "ahorro_cupon": 0.0,
            "ahorro_fidelidad": 0.0,
            "ahorro_adicional_r5": 0.0,
            "precio_final": 90.0,
            "ahorro_total": 10.0,
        }
        recibo = GeneradorRecibo.generar(desglose)
        self.assertIn("RECIBO DE COMPRA", recibo)
        self.assertIn("$90.00", recibo)
        self.assertNotIn("Cupón aplicado", recibo)
        self.assertNotIn("Beneficio fidelidad", recibo)

    def test_recibo_con_todos_los_descuentos(self):
        """Genera un recibo con todos los descuentos presentes."""
        desglose = {
            "cantidad": 10,
            "subtotal": 1000.0,
            "descuento_base_pct": 80,
            "ahorro_base": 800.0,
            "ahorro_adicional_r5": 10.0,
            "ahorro_volumen": 19.0,
            "ahorro_fidelidad": 5.13,
            "ahorro_cupon": 16.59,
            "precio_final": 149.28,
            "ahorro_total": 850.72,
        }
        recibo = GeneradorRecibo.generar(desglose)
        self.assertIn("Descuento por volumen", recibo)
        self.assertIn("Cupón aplicado", recibo)
        self.assertIn("Beneficio fidelidad", recibo)
        self.assertIn("Descuento especial", recibo)


# ============================================================
# 5. PRUEBAS PARA LA CLASE CalculadoraDescuento
# ============================================================
class TestCalculadoraDescuento(unittest.TestCase):
    """Pruebas para la clase CalculadoraDescuento (lógica principal)."""

    def setUp(self):
        self.calc = CalculadoraDescuento()

    # --- R1: Precio inválido ---
    def test_precio_cero_lanza_excepcion(self):
        with self.assertRaises(PrecioInvalidoError):
            self.calc.calcular(0, 10)

    def test_precio_negativo_lanza_excepcion(self):
        with self.assertRaises(PrecioInvalidoError):
            self.calc.calcular(-100, 10)

    # --- R2: Descuento inválido ---
    def test_descuento_negativo_lanza_excepcion(self):
        with self.assertRaises(DescuentoInvalidoError):
            self.calc.calcular(100, -5)

    def test_descuento_mayor_100_lanza_excepcion(self):
        with self.assertRaises(DescuentoInvalidoError):
            self.calc.calcular(100, 150)

    # --- Cantidad inválida ---
    def test_cantidad_cero_lanza_excepcion(self):
        with self.assertRaises(ValueError):
            self.calc.calcular(100, 10, cantidad=0)

    def test_cantidad_negativa_lanza_excepcion(self):
        with self.assertRaises(ValueError):
            self.calc.calcular(100, 10, cantidad=-1)

    # --- R3: Cálculo de descuento base ---
    def test_descuento_base_simple(self):
        """Precio 200, descuento 10% => final 180."""
        resultado = self.calc.calcular(200, 10)
        self.assertEqual(resultado["precio_final"], 180.0)
        self.assertEqual(resultado["ahorro_base"], 20.0)

    def test_sin_descuento(self):
        """Descuento 0% => precio final igual al original."""
        resultado = self.calc.calcular(100, 0)
        self.assertEqual(resultado["precio_final"], 100.0)

    def test_descuento_total(self):
        """Descuento 100% => precio final 0."""
        resultado = self.calc.calcular(100, 100)
        self.assertEqual(resultado["precio_final"], 0.0)

    # --- R4: Redondeo a 2 decimales ---
    def test_redondeo_a_dos_decimales(self):
        """El precio final debe estar redondeado a 2 decimales."""
        resultado = self.calc.calcular(99.99, 33.33)
        precio = resultado["precio_final"]
        self.assertEqual(precio, round(precio, 2))

    # --- R5: Descuento adicional si >= 80% ---
    def test_descuento_adicional_con_80_porciento(self):
        """Con descuento >= 80% se aplica un 5% adicional."""
        resultado = self.calc.calcular(100, 80)
        # Precio tras 80%: 20.0  →  5% adicional de 20 = 1.0  →  final = 19.0
        self.assertEqual(resultado["ahorro_adicional_r5"], 1.0)
        self.assertEqual(resultado["precio_final"], 19.0)

    def test_sin_descuento_adicional_con_79_porciento(self):
        """Con descuento < 80% NO se aplica el 5% adicional."""
        resultado = self.calc.calcular(100, 79)
        self.assertEqual(resultado["ahorro_adicional_r5"], 0.0)

    # --- Descuento por volumen ---
    def test_volumen_sin_descuento_cantidad_1(self):
        """Cantidad 1: sin descuento por volumen."""
        resultado = self.calc.calcular(100, 10, cantidad=1)
        self.assertEqual(resultado["ahorro_volumen"], 0.0)

    def test_volumen_sin_descuento_cantidad_4(self):
        """Cantidad 4: sin descuento por volumen."""
        resultado = self.calc.calcular(100, 10, cantidad=4)
        self.assertEqual(resultado["ahorro_volumen"], 0.0)

    def test_volumen_5_unidades(self):
        """Cantidad 5: 5% de descuento por volumen."""
        resultado = self.calc.calcular(100, 10, cantidad=5)
        # Subtotal=500, ahorro_base=50, precio_actual=450
        # 5% de 450 = 22.5
        self.assertEqual(resultado["ahorro_volumen"], 22.5)

    def test_volumen_9_unidades(self):
        """Cantidad 9: 5% de descuento por volumen."""
        resultado = self.calc.calcular(100, 0, cantidad=9)
        # Subtotal=900, ahorro_base=0, precio_actual=900
        # 5% de 900 = 45.0
        self.assertEqual(resultado["ahorro_volumen"], 45.0)

    def test_volumen_10_unidades(self):
        """Cantidad 10: 10% de descuento por volumen."""
        resultado = self.calc.calcular(100, 0, cantidad=10)
        # Subtotal=1000, precio_actual=1000
        # 10% de 1000 = 100
        self.assertEqual(resultado["ahorro_volumen"], 100.0)

    # --- Fidelidad ---
    def test_fidelidad_bronce_sin_descuento(self):
        """Nivel BRONCE: 0% de descuento por fidelidad."""
        resultado = self.calc.calcular(100, 10, nivel_fidelidad="BRONCE")
        self.assertEqual(resultado["ahorro_fidelidad"], 0.0)

    def test_fidelidad_platino(self):
        """Nivel PLATINO: 10% de descuento por fidelidad."""
        resultado = self.calc.calcular(100, 0, nivel_fidelidad="PLATINO")
        # precio_actual=100, 10% = 10
        self.assertEqual(resultado["ahorro_fidelidad"], 10.0)

    # --- Cupones ---
    def test_cupon_porcentaje(self):
        """Cupón PROMO10 aplica un 10% adicional."""
        resultado = self.calc.calcular(
            100, 0, codigo_cupon="PROMO10",
            fecha_actual_simulada=date(2025, 1, 1)
        )
        self.assertEqual(resultado["ahorro_cupon"], 10.0)

    def test_cupon_fijo(self):
        """Cupón FIJO15 aplica $15 de descuento fijo."""
        resultado = self.calc.calcular(
            100, 0, codigo_cupon="FIJO15",
            fecha_actual_simulada=date(2025, 1, 1)
        )
        self.assertEqual(resultado["ahorro_cupon"], 15.0)

    def test_cupon_fijo_no_supera_precio(self):
        """Si el cupón fijo es mayor al precio actual, solo descuenta lo restante."""
        resultado = self.calc.calcular(
            10, 0, codigo_cupon="FIJO15",
            fecha_actual_simulada=date(2025, 1, 1)
        )
        self.assertEqual(resultado["ahorro_cupon"], 10.0)
        self.assertEqual(resultado["precio_final"], 0.0)

    def test_cupon_expirado_lanza_excepcion(self):
        """Un cupón expirado lanza CuponInvalidoError."""
        with self.assertRaises(CuponInvalidoError):
            self.calc.calcular(
                100, 0, codigo_cupon="EXPIRADO",
                fecha_actual_simulada=date(2025, 1, 1)
            )

    def test_cupon_inexistente_lanza_excepcion(self):
        """Un cupón inexistente lanza CuponInvalidoError."""
        with self.assertRaises(CuponInvalidoError):
            self.calc.calcular(
                100, 0, codigo_cupon="FALSO",
                fecha_actual_simulada=date(2025, 1, 1)
            )

    # --- Precio final no negativo ---
    def test_precio_final_nunca_negativo(self):
        """El precio final nunca puede ser negativo."""
        resultado = self.calc.calcular(100, 100)
        self.assertGreaterEqual(resultado["precio_final"], 0.0)

    # --- Cálculo combinado ---
    def test_calculo_combinado_completo(self):
        """Prueba integral: descuento base + R5 + volumen + fidelidad + cupón."""
        resultado = self.calc.calcular(
            precio=100,
            descuento_base=80,
            cantidad=10,
            codigo_cupon="PROMO10",
            nivel_fidelidad="ORO",
            fecha_actual_simulada=date(2025, 1, 1),
        )
        # Subtotal = 1000
        # Descuento base 80%: 800 → precio_actual = 200
        # R5 (>=80%): 5% de 200 = 10 → precio_actual = 190
        # Volumen (>=10): 10% de 190 = 19 → precio_actual = 171
        # Fidelidad ORO 5%: 5% de 171 = 8.55 → precio_actual = 162.45
        # Cupón PROMO10 10%: 10% de 162.45 = 16.245 → precio_actual = 146.205
        # Redondeado: 146.21
        self.assertEqual(resultado["subtotal"], 1000.0)
        self.assertEqual(resultado["ahorro_base"], 800.0)
        self.assertEqual(resultado["ahorro_adicional_r5"], 10.0)
        self.assertEqual(resultado["ahorro_volumen"], 19.0)
        self.assertEqual(resultado["ahorro_fidelidad"], 8.55)
        self.assertEqual(resultado["precio_final"], 146.2)

    # --- Estructura del diccionario de respuesta ---
    def test_estructura_resultado(self):
        """El resultado debe contener todas las claves esperadas."""
        resultado = self.calc.calcular(100, 10)
        claves_esperadas = [
            "cantidad", "subtotal", "descuento_base_pct",
            "ahorro_base", "ahorro_adicional_r5", "ahorro_volumen",
            "ahorro_fidelidad", "ahorro_cupon", "ahorro_total",
            "precio_final",
        ]
        for clave in claves_esperadas:
            self.assertIn(clave, resultado, f"Falta la clave '{clave}' en el resultado.")


# ============================================================
# 6. PRUEBAS PARA LA FUNCIÓN calcular_precio_final
# ============================================================
class TestCalcularPrecioFinal(unittest.TestCase):
    """Pruebas para la función heredada calcular_precio_final."""

    def test_calculo_simple(self):
        """Precio 200, descuento 10% => 180."""
        self.assertEqual(calcular_precio_final(200, 10), 180.0)

    def test_precio_cero_lanza_valueerror(self):
        """Mantiene compatibilidad: precio 0 lanza ValueError."""
        with self.assertRaises(ValueError):
            calcular_precio_final(0, 10)

    def test_precio_negativo_lanza_valueerror(self):
        """Mantiene compatibilidad: precio negativo lanza ValueError."""
        with self.assertRaises(ValueError):
            calcular_precio_final(-50, 10)

    def test_descuento_negativo_lanza_valueerror(self):
        """Mantiene compatibilidad: descuento negativo lanza ValueError."""
        with self.assertRaises(ValueError):
            calcular_precio_final(100, -5)

    def test_descuento_mayor_100_lanza_valueerror(self):
        """Mantiene compatibilidad: descuento > 100 lanza ValueError."""
        with self.assertRaises(ValueError):
            calcular_precio_final(100, 150)

    def test_descuento_cero(self):
        """Sin descuento devuelve el precio original."""
        self.assertEqual(calcular_precio_final(100, 0), 100.0)

    def test_descuento_100(self):
        """Descuento 100% devuelve 0."""
        self.assertEqual(calcular_precio_final(100, 100), 0.0)

    def test_r5_aplicado_en_funcion_heredada(self):
        """Con 80% de descuento se aplica el 5% adicional (R5)."""
        # Precio 100, descuento 80%: precio_actual = 20
        # R5: 5% de 20 = 1 → precio_final = 19
        self.assertEqual(calcular_precio_final(100, 80), 19.0)


# ============================================================
# 7. PRUEBAS PARA LA CLASE MostrarResultado
# ============================================================
class TestMostrarResultado(unittest.TestCase):
    """Pruebas para la clase MostrarResultado."""

    def test_mostrar_imprime_resultado(self):
        """Verifica que mostrar() imprime el resultado."""
        import io
        from contextlib import redirect_stdout

        mostrador = MostrarResultado()
        f = io.StringIO()
        with redirect_stdout(f):
            mostrador.mostrar(90.0)
        salida = f.getvalue()
        self.assertIn("90.0", salida)


# ============================================================
# 8. PRUEBAS DE HERENCIA DE EXCEPCIONES
# ============================================================
class TestExcepciones(unittest.TestCase):
    """Verifica la jerarquía de excepciones."""

    def test_precio_invalido_es_calculadora_error(self):
        self.assertTrue(issubclass(PrecioInvalidoError, CalculadoraError))

    def test_descuento_invalido_es_calculadora_error(self):
        self.assertTrue(issubclass(DescuentoInvalidoError, CalculadoraError))

    def test_cupon_invalido_es_calculadora_error(self):
        self.assertTrue(issubclass(CuponInvalidoError, CalculadoraError))

    def test_calculadora_error_es_exception(self):
        self.assertTrue(issubclass(CalculadoraError, Exception))


if __name__ == "__main__":
    unittest.main()
