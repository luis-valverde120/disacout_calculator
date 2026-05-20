# test_calculadora.py
# Pruebas unitarias para calculadora.py usando la librería unittest
import unittest
import sys
import os
from datetime import date
from faker import Faker

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


class FakerTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.faker = Faker()
        self.faker.seed_instance(12345)


# ============================================================
# 1. PRUEBAS PARA LA CLASE Validador
# ============================================================
class TestValidador(FakerTestCase):
    """Pruebas para la clase Validador."""

    # --- validar_precio ---
    def test_precio_positivo_no_lanza_excepcion(self):
        """R1: Un precio positivo no debe lanzar excepción."""
        try:
            Validador.validar_precio(self.faker.pyfloat(min_value=0.01, max_value=1000.0, right_digits=2))
        except PrecioInvalidoError:
            self.fail("validar_precio lanzó PrecioInvalidoError con un precio válido.")

    def test_precio_cero_lanza_excepcion(self):
        """R1: Un precio igual a cero debe lanzar PrecioInvalidoError."""
        with self.assertRaises(PrecioInvalidoError):
            Validador.validar_precio(0.0) # Usamos el valor exacto

    def test_precio_negativo_lanza_excepcion(self):
        """R1: Un precio negativo debe lanzar PrecioInvalidoError."""
        with self.assertRaises(PrecioInvalidoError):
            Validador.validar_precio(self.faker.pyfloat(min_value=-1000.0, max_value=-0.01, right_digits=2))

    # --- validar_descuento ---
    def test_descuento_valido_no_lanza_excepcion(self):
        """R2: Un descuento entre 0 y 100 no debe lanzar excepción."""
        try:
            Validador.validar_descuento(self.faker.pyfloat(min_value=0.0, max_value=100.0, right_digits=2))
        except DescuentoInvalidoError:
            self.fail("validar_descuento lanzó excepción con descuento válido.")

    def test_descuento_cero_es_valido(self):
        """R2: Un descuento de 0% es válido (sin descuento)."""
        try:
            Validador.validar_descuento(0.0) # Usamos el valor exacto
        except DescuentoInvalidoError:
            self.fail("validar_descuento lanzó excepción con descuento 0.")

    def test_descuento_cien_es_valido(self):
        """R2: Un descuento de 100% es válido (gratis)."""
        try:
            Validador.validar_descuento(100.0) # Usamos el valor exacto
        except DescuentoInvalidoError:
            self.fail("validar_descuento lanzó excepción con descuento 100.")

    def test_descuento_negativo_lanza_excepcion(self):
        """R2: Un descuento negativo debe lanzar DescuentoInvalidoError."""
        with self.assertRaises(DescuentoInvalidoError):
            Validador.validar_descuento(self.faker.pyfloat(min_value=-100.0, max_value=-0.01, right_digits=2))

    def test_descuento_mayor_a_100_lanza_excepcion(self):
        """R2: Un descuento mayor a 100 debe lanzar DescuentoInvalidoError."""
        with self.assertRaises(DescuentoInvalidoError):
            Validador.validar_descuento(self.faker.pyfloat(min_value=100.01, max_value=200.0, right_digits=2))


# ============================================================
# 2. PRUEBAS PARA LA CLASE GestorCupones
# ============================================================
class TestGestorCupones(FakerTestCase):
    """Pruebas para la clase GestorCupones."""

    def setUp(self):
        super().setUp()
        self.gestor = GestorCupones()

    def test_cupon_porcentaje_valido(self):
        """Un cupón de porcentaje válido devuelve tipo y valor correctos."""
        fecha = self.faker.date_between_dates(date(2025, 1, 1), date(2090, 1, 1))
        tipo, valor = self.gestor.obtener_descuento_cupon("PROMO10", fecha)
        self.assertEqual(tipo, "porcentaje")
        self.assertEqual(valor, 10.0)

    def test_cupon_fijo_valido(self):
        """Un cupón de valor fijo válido devuelve tipo y valor correctos."""
        fecha = self.faker.date_between_dates(date(2025, 1, 1), date(2090, 1, 1))
        tipo, valor = self.gestor.obtener_descuento_cupon("FIJO15", fecha)
        self.assertEqual(tipo, "fijo")
        self.assertEqual(valor, 15.0)

    def test_cupon_inexistente_lanza_excepcion(self):
        """Un código de cupón inexistente debe lanzar CuponInvalidoError."""
        with self.assertRaises(CuponInvalidoError):
            self.gestor.obtener_descuento_cupon(self.faker.bothify(text="??????"), date(2025, 6, 1))

    def test_cupon_expirado_lanza_excepcion(self):
        """Un cupón expirado debe lanzar CuponInvalidoError."""
        with self.assertRaises(CuponInvalidoError):
            self.gestor.obtener_descuento_cupon("EXPIRADO", self.faker.date_between_dates(date(2021, 1, 1), date(2026, 1, 1)))

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
class TestServicioFidelizacion(FakerTestCase):
    """Pruebas para la clase ServicioFidelizacion."""

    def test_nivel_bronce(self):
        nivel = self.faker.random_element(["BRONCE", "bronce"])
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel(nivel), 0.0)

    def test_nivel_plata(self):
        nivel = self.faker.random_element(["PLATA", "plata"])
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel(nivel), 3.0)

    def test_nivel_oro(self):
        nivel = self.faker.random_element(["ORO", "oro"])
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel(nivel), 5.0)

    def test_nivel_platino(self):
        nivel = self.faker.random_element(["PLATINO", "platino"])
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel(nivel), 10.0)

    def test_nivel_minusculas(self):
        """El nivel debe funcionar sin importar mayúsculas/minúsculas."""
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel("oro"), 5.0)

    def test_nivel_desconocido(self):
        """Un nivel no registrado devuelve 0.0 de descuento."""
        self.assertEqual(ServicioFidelizacion.obtener_descuento_nivel("DIAMANTE"), 0.0)


# ============================================================
# 4. PRUEBAS PARA LA CLASE GeneradorRecibo
# ============================================================
class TestGeneradorRecibo(FakerTestCase):
    """Pruebas para la clase GeneradorRecibo."""

    def test_recibo_basico(self):
        """Genera un recibo sin descuentos opcionales."""
        cantidad = self.faker.random_int(min=1, max=3)
        subtotal = round(self.faker.pyfloat(min_value=50.0, max_value=300.0, right_digits=2), 2)
        descuento_base = self.faker.random_int(min=1, max=30)
        ahorro_base = round(subtotal * (descuento_base / 100), 2)
        precio_final = round(subtotal - ahorro_base, 2)
        desglose = {
            "cantidad": cantidad,
            "subtotal": subtotal,
            "descuento_base_pct": descuento_base,
            "ahorro_base": ahorro_base,
            "ahorro_volumen": 0.0,
            "ahorro_cupon": 0.0,
            "ahorro_fidelidad": 0.0,
            "ahorro_adicional_r5": 0.0,
            "precio_final": precio_final,
            "ahorro_total": round(subtotal - precio_final, 2),
        }
        recibo = GeneradorRecibo.generar(desglose)
        self.assertIn("RECIBO DE COMPRA", recibo)
        self.assertIn(f"TOTAL A PAGAR: ${precio_final:.2f}", recibo)
        self.assertNotIn("Cupón aplicado", recibo)
        self.assertNotIn("Beneficio fidelidad", recibo)

    def test_recibo_con_todos_los_descuentos(self):
        """Genera un recibo con todos los descuentos presentes."""
        cantidad = self.faker.random_int(min=10, max=15)
        subtotal = round(self.faker.pyfloat(min_value=500.0, max_value=1200.0, right_digits=2), 2)
        descuento_base = self.faker.random_int(min=80, max=90)
        desglose = {
            "cantidad": cantidad,
            "subtotal": subtotal,
            "descuento_base_pct": descuento_base,
            "ahorro_base": round(subtotal * (descuento_base / 100), 2),
            "ahorro_adicional_r5": round(subtotal * 0.01, 2),
            "ahorro_volumen": round(subtotal * 0.02, 2),
            "ahorro_fidelidad": round(subtotal * 0.01, 2),
            "ahorro_cupon": round(subtotal * 0.02, 2),
            "precio_final": round(subtotal * 0.2, 2),
            "ahorro_total": round(subtotal * 0.8, 2),
        }
        recibo = GeneradorRecibo.generar(desglose)
        self.assertIn("Descuento por volumen", recibo)
        self.assertIn("Cupón aplicado", recibo)
        self.assertIn("Beneficio fidelidad", recibo)
        self.assertIn("Descuento especial", recibo)


# ============================================================
# 5. PRUEBAS PARA LA CLASE CalculadoraDescuento
# ============================================================
class TestCalculadoraDescuento(FakerTestCase):
    """Pruebas para la clase CalculadoraDescuento (lógica principal)."""

    def setUp(self):
        super().setUp()
        self.calc = CalculadoraDescuento()

    # --- R1: Precio inválido ---
    def test_precio_cero_lanza_excepcion(self):
        with self.assertRaises(PrecioInvalidoError):
            self.calc.calcular(0.0, 10) # Usamos el valor exacto

    def test_precio_negativo_lanza_excepcion(self):
        with self.assertRaises(PrecioInvalidoError):
            self.calc.calcular(self.faker.pyfloat(min_value=-1000.0, max_value=-0.01, right_digits=2), 10)

    # --- R2: Descuento inválido ---
    def test_descuento_negativo_lanza_excepcion(self):
        with self.assertRaises(DescuentoInvalidoError):
            self.calc.calcular(100, self.faker.pyfloat(min_value=-100.0, max_value=-0.01, right_digits=2))

    def test_descuento_mayor_100_lanza_excepcion(self):
        with self.assertRaises(DescuentoInvalidoError):
            self.calc.calcular(100, self.faker.pyfloat(min_value=100.01, max_value=200.0, right_digits=2))

    # --- Cantidad inválida ---
    def test_cantidad_cero_lanza_excepcion(self):
        with self.assertRaises(ValueError):
            self.calc.calcular(100, 10, cantidad=self.faker.random_int(min=-3, max=0))

    def test_cantidad_negativa_lanza_excepcion(self):
        with self.assertRaises(ValueError):
            self.calc.calcular(100, 10, cantidad=self.faker.random_int(min=-10, max=-1))

    # --- R3: Cálculo de descuento base ---
    def test_descuento_base_simple(self):
        """Precio 200, descuento 10% => final 180."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=300.0, right_digits=2)
        descuento = self.faker.pyfloat(min_value=1.0, max_value=30.0, right_digits=2)
        resultado = self.calc.calcular(precio, descuento)
        self.assertEqual(resultado["precio_final"], round(precio * (1 - descuento / 100), 2))
        self.assertEqual(resultado["ahorro_base"], round(precio * (descuento / 100), 2))

    def test_sin_descuento(self):
        """Descuento 0% => precio final igual al original."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=300.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0)
        self.assertEqual(resultado["precio_final"], round(precio, 2))

    def test_descuento_total(self):
        """Descuento 100% => precio final 0."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=300.0, right_digits=2)
        resultado = self.calc.calcular(precio, 100)
        self.assertEqual(resultado["precio_final"], 0.0)

    # --- R4: Redondeo a 2 decimales ---
    def test_redondeo_a_dos_decimales(self):
        """El precio final debe estar redondeado a 2 decimales."""
        precio = self.faker.pyfloat(min_value=10.0, max_value=200.0, right_digits=4)
        descuento = self.faker.pyfloat(min_value=0.0, max_value=80.0, right_digits=4)
        resultado = self.calc.calcular(precio, descuento)
        precio = resultado["precio_final"]
        self.assertEqual(precio, round(precio, 2))

    # --- R5: Descuento adicional si >= 80% ---
    def test_descuento_adicional_con_80_porciento(self):
        """Con descuento >= 80% se aplica un 5% adicional."""
        precio = self.faker.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = self.faker.pyfloat(min_value=80.0, max_value=100.0, right_digits=2)
        resultado = self.calc.calcular(precio, descuento)
        base = precio * (1 - descuento / 100)
        self.assertEqual(resultado["ahorro_adicional_r5"], round(base * 0.05, 2))
        self.assertEqual(resultado["precio_final"], round(base * 0.95, 2))

    def test_sin_descuento_adicional_con_79_porciento(self):
        """Con descuento < 80% NO se aplica el 5% adicional."""
        precio = self.faker.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = self.faker.pyfloat(min_value=0.0, max_value=79.0, right_digits=2)
        resultado = self.calc.calcular(precio, descuento)
        self.assertEqual(resultado["ahorro_adicional_r5"], 0.0)

    # --- Descuento por volumen ---
    def test_volumen_sin_descuento_cantidad_1(self):
        """Cantidad 1: sin descuento por volumen."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 10, cantidad=1)
        self.assertEqual(resultado["ahorro_volumen"], 0.0)

    def test_volumen_sin_descuento_cantidad_4(self):
        """Cantidad 4: sin descuento por volumen."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 10, cantidad=4)
        self.assertEqual(resultado["ahorro_volumen"], 0.0)

    def test_volumen_5_unidades(self):
        """Cantidad 5: 5% de descuento por volumen."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 10, cantidad=5)
        # Subtotal=500, ahorro_base=50, precio_actual=450
        # 5% de 450 = 22.5
        precio_actual = round(precio * 5 * (1 - 0.10), 2)
        self.assertEqual(resultado["ahorro_volumen"], round(precio_actual * 0.05, 2))

    def test_volumen_9_unidades(self):
        """Cantidad 9: 5% de descuento por volumen."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0, cantidad=9)
        # Subtotal=900, ahorro_base=0, precio_actual=900
        # 5% de 900 = 45.0
        self.assertEqual(resultado["ahorro_volumen"], round(precio * 9 * 0.05, 2))

    def test_volumen_10_unidades(self):
        """Cantidad 10: 10% de descuento por volumen."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0, cantidad=10)
        # Subtotal=1000, precio_actual=1000
        # 10% de 1000 = 100
        self.assertEqual(resultado["ahorro_volumen"], round(precio * 10 * 0.10, 2))

    # --- Fidelidad ---
    def test_fidelidad_bronce_sin_descuento(self):
        """Nivel BRONCE: 0% de descuento por fidelidad."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 10, nivel_fidelidad="BRONCE")
        self.assertEqual(resultado["ahorro_fidelidad"], 0.0)

    def test_fidelidad_platino(self):
        """Nivel PLATINO: 10% de descuento por fidelidad."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0, nivel_fidelidad="PLATINO")
        # precio_actual=100, 10% = 10
        self.assertEqual(resultado["ahorro_fidelidad"], round(precio * 0.10, 2))

    # --- Cupones ---
    def test_cupon_porcentaje(self):
        """Cupón PROMO10 aplica un 10% adicional."""
        resultado = self.calc.calcular(
            self.faker.pyfloat(min_value=80.0, max_value=200.0, right_digits=2), 0, codigo_cupon="PROMO10",
            fecha_actual_simulada=self.faker.date_between_dates(date(2025, 1, 1), date(2090, 1, 1))
        )
        self.assertEqual(resultado["ahorro_cupon"], round(resultado["subtotal"] * 0.10, 2))

    def test_cupon_fijo(self):
        """Cupón FIJO15 aplica $15 de descuento fijo."""
        resultado = self.calc.calcular(
            self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2), 0, codigo_cupon="FIJO15",
            fecha_actual_simulada=self.faker.date_between_dates(date(2025, 1, 1), date(2090, 1, 1))
        )
        self.assertEqual(resultado["ahorro_cupon"], 15.0)

    def test_cupon_fijo_no_supera_precio(self):
        """Si el cupón fijo es mayor al precio actual, solo descuenta lo restante."""
        resultado = self.calc.calcular(
            self.faker.pyfloat(min_value=1.0, max_value=14.99, right_digits=2), 0, codigo_cupon="FIJO15",
            fecha_actual_simulada=self.faker.date_between_dates(date(2025, 1, 1), date(2090, 1, 1))
        )
        self.assertEqual(resultado["ahorro_cupon"], round(resultado["subtotal"], 2))
        self.assertEqual(resultado["precio_final"], 0.0)

    def test_cupon_expirado_lanza_excepcion(self):
        """Un cupón expirado lanza CuponInvalidoError."""
        with self.assertRaises(CuponInvalidoError):
            self.calc.calcular(
                100, 0, codigo_cupon="EXPIRADO",
                fecha_actual_simulada=self.faker.date_between_dates(date(2021, 1, 1), date(2026, 1, 1))
            )

    def test_cupon_inexistente_lanza_excepcion(self):
        """Un cupón inexistente lanza CuponInvalidoError."""
        with self.assertRaises(CuponInvalidoError):
            self.calc.calcular(
                100, 0, codigo_cupon=self.faker.bothify(text="??????"),
                fecha_actual_simulada=self.faker.date_between_dates(date(2025, 1, 1), date(2090, 1, 1))
            )

    # --- Precio final no negativo ---
    def test_precio_final_nunca_negativo(self):
        """El precio final nunca puede ser negativo."""
        resultado = self.calc.calcular(self.faker.pyfloat(min_value=50.0, max_value=300.0, right_digits=2), 100)
        self.assertGreaterEqual(resultado["precio_final"], 0.0)

    # --- Cálculo combinado ---
    def test_calculo_combinado_completo(self):
        """Prueba integral: descuento base + R5 + volumen + fidelidad + cupón."""
        precio = self.faker.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(
            precio=precio,
            descuento_base=80,
            cantidad=10,
            codigo_cupon="PROMO10",
            nivel_fidelidad="ORO",
            fecha_actual_simulada=self.faker.date_between_dates(date(2025, 1, 1), date(2090, 1, 1)),
        )
        subtotal = precio * 10
        base = subtotal * 0.80
        precio_actual = subtotal - base
        adicional_r5 = precio_actual * 0.05
        precio_actual -= adicional_r5
        volumen = precio_actual * 0.10
        precio_actual -= volumen
        fidelidad = precio_actual * 0.05
        precio_actual -= fidelidad
        cupon = precio_actual * 0.10
        precio_actual -= cupon
        self.assertEqual(resultado["subtotal"], round(subtotal, 2))
        self.assertEqual(resultado["ahorro_base"], round(base, 2))
        self.assertEqual(resultado["ahorro_adicional_r5"], round(adicional_r5, 2))
        self.assertEqual(resultado["ahorro_volumen"], round(volumen, 2))
        self.assertEqual(resultado["ahorro_fidelidad"], round(fidelidad, 2))
        self.assertEqual(resultado["precio_final"], round(precio_actual, 2))

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
class TestCalcularPrecioFinal(FakerTestCase):
    """Pruebas para la función heredada calcular_precio_final."""

    def test_calculo_simple(self):
        """Precio 200, descuento 10% => 180."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=300.0, right_digits=2)
        descuento = self.faker.pyfloat(min_value=0.0, max_value=30.0, right_digits=2)
        self.assertEqual(calcular_precio_final(precio, descuento), round(precio * (1 - descuento / 100), 2))

    def test_precio_cero_lanza_valueerror(self):
        """Mantiene compatibilidad: precio 0 lanza ValueError."""
        with self.assertRaises(ValueError):
            calcular_precio_final(self.faker.pyfloat(min_value=0.0, max_value=0.0), 10)

    def test_precio_negativo_lanza_valueerror(self):
        """Mantiene compatibilidad: precio negativo lanza ValueError."""
        with self.assertRaises(ValueError):
            calcular_precio_final(self.faker.pyfloat(min_value=-100.0, max_value=-0.01, right_digits=2), 10)

    def test_descuento_negativo_lanza_valueerror(self):
        """Mantiene compatibilidad: descuento negativo lanza ValueError."""
        with self.assertRaises(ValueError):
            calcular_precio_final(100, self.faker.pyfloat(min_value=-100.0, max_value=-0.01, right_digits=2))

    def test_descuento_mayor_100_lanza_valueerror(self):
        """Mantiene compatibilidad: descuento > 100 lanza ValueError."""
        with self.assertRaises(ValueError):
            calcular_precio_final(100, self.faker.pyfloat(min_value=100.01, max_value=200.0, right_digits=2))

    def test_descuento_cero(self):
        """Sin descuento devuelve el precio original."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=300.0, right_digits=2)
        self.assertEqual(calcular_precio_final(precio, 0), round(precio, 2))

    def test_descuento_100(self):
        """Descuento 100% devuelve 0."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=300.0, right_digits=2)
        self.assertEqual(calcular_precio_final(precio, 100), 0.0)

    def test_r5_aplicado_en_funcion_heredada(self):
        """Con 80% de descuento se aplica el 5% adicional (R5)."""
        precio = self.faker.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = self.faker.pyfloat(min_value=80.0, max_value=100.0, right_digits=2)
        base = precio * (1 - descuento / 100)
        self.assertEqual(calcular_precio_final(precio, descuento), round(base * 0.95, 2))


# ============================================================
# 7. PRUEBAS PARA LA CLASE MostrarResultado
# ============================================================
class TestMostrarResultado(FakerTestCase):
    """Pruebas para la clase MostrarResultado."""

    def test_mostrar_imprime_resultado(self):
        """Verifica que mostrar() imprime el resultado."""
        import io
        from contextlib import redirect_stdout

        mostrador = MostrarResultado()
        f = io.StringIO()
        with redirect_stdout(f):
            valor = self.faker.pyfloat(min_value=1.0, max_value=200.0, right_digits=2)
            mostrador.mostrar(valor)
        salida = f.getvalue()
        self.assertIn(str(valor), salida)


# ============================================================
# 8. PRUEBAS DE HERENCIA DE EXCEPCIONES
# ============================================================
class TestExcepciones(FakerTestCase):
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
