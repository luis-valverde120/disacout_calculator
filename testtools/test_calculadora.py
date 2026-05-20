import sys
import os
from datetime import date
import testtools
from testtools.matchers import Equals, Raises, MatchesException, Contains
from faker import Faker

# Agregamos el directorio padre al path para importar calculadora.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculadora import (
    CalculadoraDescuento,
    GeneradorRecibo,
    PrecioInvalidoError,
    DescuentoInvalidoError,
    CuponInvalidoError
)

class TestCalculadoraAvanzadaTDD(testtools.TestCase):

    def setUp(self):
        super().setUp()
        # Instanciamos la calculadora antes de cada test (fase Arrange de TDD)
        self.calc = CalculadoraDescuento()
        self.faker = Faker()
        self.faker.seed_instance(12345)

    # ==========================================
    # FASE 1: Validaciones de Entrada (R1, R2 y Cantidad)
    # ==========================================

    def test_precio_invalido_levanta_excepcion_personalizada(self):
        """R2: El precio original debe ser mayor a cero, validado por PrecioInvalidoError."""
        self.assertThat(
            lambda: self.calc.calcular(self.faker.pyfloat(min_value=0.0, max_value=0.0), 20),
            Raises(MatchesException(PrecioInvalidoError))
        )
        self.assertThat(
            lambda: self.calc.calcular(self.faker.pyfloat(min_value=-100.0, max_value=-0.01, right_digits=2), 20),
            Raises(MatchesException(PrecioInvalidoError))
        )

    def test_descuento_fuera_de_rango_levanta_excepcion_personalizada(self):
        """R1: El descuento debe estar entre 0 y 100, validado por DescuentoInvalidoError."""
        self.assertThat(
            lambda: self.calc.calcular(100, self.faker.pyfloat(min_value=-100.0, max_value=-0.01, right_digits=2)),
            Raises(MatchesException(DescuentoInvalidoError))
        )
        self.assertThat(
            lambda: self.calc.calcular(100, self.faker.pyfloat(min_value=100.01, max_value=200.0, right_digits=2)),
            Raises(MatchesException(DescuentoInvalidoError))
        )

    def test_cantidad_menor_a_uno_levanta_error(self):
        """La cantidad de productos debe ser al menos 1."""
        self.assertThat(
            lambda: self.calc.calcular(100, 10, cantidad=self.faker.random_int(min=-3, max=0)),
            Raises(MatchesException(ValueError))
        )

    # ==========================================
    # FASE 2: Cálculos Base y R5
    # ==========================================

    def test_calculo_descuento_base(self):
        """R3 y R4: Cálculo estándar y redondeo."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        descuento = self.faker.pyfloat(min_value=1.0, max_value=30.0, right_digits=2)
        resultado = self.calc.calcular(precio, descuento)
        self.assertThat(resultado["precio_final"], Equals(round(precio * (1 - descuento / 100), 2)))
        self.assertThat(resultado["ahorro_base"], Equals(round(precio * (descuento / 100), 2)))

    def test_r5_aplica_descuento_extra_con_base_alta(self):
        """R5: Si descuento_base >= 80%, aplica 5% extra al remanente."""
        # 80% de 100 = 20. Remanente = 20. Adicional 5% de 20 = 1.0. Final = 19.0
        precio = self.faker.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = self.faker.pyfloat(min_value=80.0, max_value=100.0, right_digits=2)
        resultado = self.calc.calcular(precio, descuento)
        base = precio * (1 - descuento / 100)
        self.assertThat(resultado["ahorro_adicional_r5"], Equals(round(base * 0.05, 2)))
        self.assertThat(resultado["precio_final"], Equals(round(base * 0.95, 2)))

    # ==========================================
    # FASE 3: Descuentos por Volumen
    # ==========================================

    def test_volumen_sin_descuento_hasta_4_articulos(self):
        precio = self.faker.pyfloat(min_value=5.0, max_value=50.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0, cantidad=4)
        self.assertThat(resultado["ahorro_volumen"], Equals(0.0))

    def test_volumen_5_porciento_entre_5_y_9_articulos(self):
        # 10 * 5 = 50. 5% de 50 = 2.5
        precio = self.faker.pyfloat(min_value=5.0, max_value=50.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0, cantidad=5)
        self.assertThat(resultado["ahorro_volumen"], Equals(round(precio * 5 * 0.05, 2)))

    def test_volumen_10_porciento_para_10_o_mas_articulos(self):
        # 10 * 10 = 100. 10% de 100 = 10.0
        precio = self.faker.pyfloat(min_value=5.0, max_value=50.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0, cantidad=10)
        self.assertThat(resultado["ahorro_volumen"], Equals(round(precio * 10 * 0.10, 2)))

    # ==========================================
    # FASE 4: Fidelidad de Clientes
    # ==========================================

    def test_fidelidad_niveles_aplican_descuento_correcto(self):
        """Prueba los diferentes niveles de fidelidad (PLATA = 3%, ORO = 5%, PLATINO = 10%)."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        res_plata = self.calc.calcular(precio, 0, nivel_fidelidad="PLATA")
        self.assertThat(res_plata["ahorro_fidelidad"], Equals(round(precio * 0.03, 2)))

        res_oro = self.calc.calcular(precio, 0, nivel_fidelidad="ORO")
        self.assertThat(res_oro["ahorro_fidelidad"], Equals(round(precio * 0.05, 2)))

        res_platino = self.calc.calcular(precio, 0, nivel_fidelidad="PLATINO")
        self.assertThat(res_platino["ahorro_fidelidad"], Equals(round(precio * 0.10, 2)))

    def test_fidelidad_nivel_inexistente_da_cero(self):
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        res_nulo = self.calc.calcular(precio, 0, nivel_fidelidad="INVENTADO")
        self.assertThat(res_nulo["ahorro_fidelidad"], Equals(0.0))

    # ==========================================
    # FASE 5: Cupones
    # ==========================================

    def test_cupon_porcentaje_valido(self):
        """El cupón PROMO10 resta un 10%."""
        precio = self.faker.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0, codigo_cupon="PROMO10", fecha_actual_simulada=date(2023, 1, 1))
        self.assertThat(resultado["ahorro_cupon"], Equals(round(precio * 0.10, 2)))

    def test_cupon_fijo_valido(self):
        """El cupón FIJO15 resta $15 fijos."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = self.calc.calcular(precio, 0, codigo_cupon="FIJO15", fecha_actual_simulada=date(2023, 1, 1))
        self.assertThat(resultado["ahorro_cupon"], Equals(15.0))
        self.assertThat(resultado["precio_final"], Equals(round(precio - 15.0, 2)))

    def test_cupon_inexistente_levanta_error(self):
        """Si el cupón no existe, el sistema lo rechaza explícitamente."""
        self.assertThat(
            lambda: self.calc.calcular(100, 0, codigo_cupon=self.faker.bothify(text="??????")),
            Raises(MatchesException(CuponInvalidoError))
        )

    def test_cupon_expirado_levanta_error(self):
        """Si la fecha supera la fecha del cupón, debe fallar."""
        # El cupón EXPIRADO vence en 2020-01-01
        self.assertThat(
            lambda: self.calc.calcular(100, 0, codigo_cupon="EXPIRADO", fecha_actual_simulada=self.faker.date_between_dates(date(2021, 1, 1), date(2026, 1, 1))),
            Raises(MatchesException(CuponInvalidoError))
        )

    # ==========================================
    # FASE 6: Recibo Completo
    # ==========================================

    def test_generador_recibo_incluye_todos_los_conceptos(self):
        """Verifica que el generador de texto del recibo compile correctamente la información."""
        precio = self.faker.pyfloat(min_value=50.0, max_value=150.0, right_digits=2)
        resultado = self.calc.calcular(
            precio=precio, descuento_base=10, cantidad=5, 
            nivel_fidelidad="ORO", codigo_cupon="PROMO10", 
            fecha_actual_simulada=date(2023, 1, 1)
        )
        recibo = GeneradorRecibo.generar(resultado)
        
        # Validamos usando el matcher Contains de testtools
        self.assertThat(recibo, Contains("--- RECIBO DE COMPRA ---"))
        self.assertThat(recibo, Contains(f"Precio original (x5): ${precio * 5:.2f}"))
        self.assertThat(recibo, Contains(f"Descuento base (10%): -${(precio * 5) * 0.10:.2f}"))
        self.assertThat(recibo, Contains(f"Descuento por volumen: -${resultado['ahorro_volumen']:.2f}"))
        self.assertThat(recibo, Contains(f"Beneficio fidelidad: -${resultado['ahorro_fidelidad']:.2f}"))
        self.assertThat(recibo, Contains(f"Cupón aplicado: -${resultado['ahorro_cupon']:.2f}"))
        self.assertThat(recibo, Contains("TOTAL A PAGAR:"))

if __name__ == '__main__':
    from testtools.run import main
    main()
