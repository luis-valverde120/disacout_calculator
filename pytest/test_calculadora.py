import pytest
from datetime import date
from faker import Faker
from calculadora import (
    CalculadoraDescuento,
    GeneradorRecibo,
    calcular_precio_final,
    PrecioInvalidoError,
    DescuentoInvalidoError,
    CuponInvalidoError,
    CalculadoraError
)

@pytest.fixture
def calc():
    return CalculadoraDescuento()

@pytest.fixture(scope="function")
def faker_seeded():
    faker = Faker()
    faker.seed_instance(12345)
    return faker

class TestCompatibilidad:
    """Pruebas para verificar que la función antigua sigue funcionando (R1 a R5)."""
    
    @pytest.mark.parametrize("precio, descuento", [
        (0, 20),
        (-50, 20)
    ])
    def test_r2_precio_no_positivo(self, precio, descuento):
        with pytest.raises(ValueError):
            calcular_precio_final(precio, descuento)

    @pytest.mark.parametrize("precio, descuento", [
        (100, -10),
        (100, 105)
    ])
    def test_r1_descuento_fuera_de_rango(self, precio, descuento):
        with pytest.raises(ValueError):
            calcular_precio_final(precio, descuento)

    def test_r3_calculo_descuento_normal(self, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=50.0, right_digits=2)
        assert calcular_precio_final(precio, descuento) == round(precio * (1 - descuento / 100), 2)

    def test_r3_calculo_descuento_con_faker(self, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=1.0, max_value=500.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=79.0, right_digits=2)
        esperado = round(precio * (1 - descuento / 100), 2)
        assert calcular_precio_final(precio, descuento) == esperado

    def test_r4_redondear_dos_decimales(self, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=10.0, max_value=200.0, right_digits=5)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=50.0, right_digits=3)
        resultado = calcular_precio_final(precio, descuento)
        assert resultado == round(resultado, 2)

    def test_r5_descuento_adicional(self, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=80.0, max_value=100.0, right_digits=2)
        base = precio * (1 - descuento / 100)
        assert calcular_precio_final(precio, descuento) == round(base * 0.95, 2)

    def test_r5_descuento_adicional_con_faker(self, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=500.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=80.0, max_value=100.0, right_digits=2)
        base = precio * (1 - descuento / 100)
        esperado = round(base * 0.95, 2)
        assert calcular_precio_final(precio, descuento) == esperado


class TestNuevasFuncionalidades:
    """Pruebas de la nueva arquitectura OOP."""

    def test_calculadora_precio_invalido(self, calc, faker_seeded):
        with pytest.raises(PrecioInvalidoError):
            calc.calcular(faker_seeded.pyfloat(min_value=-100.0, max_value=-0.01, right_digits=2), 10)
            
    def test_calculadora_descuento_invalido(self, calc, faker_seeded):
        with pytest.raises(DescuentoInvalidoError):
            calc.calcular(100, faker_seeded.pyfloat(min_value=100.01, max_value=200.0, right_digits=2))

    @pytest.mark.parametrize("cantidad, descuento_esperado", [
        (1, 0.0),
        (4, 0.0),
        (5, 5.0),
        (9, 5.0),
        (10, 10.0),
        (100, 10.0)
    ])
    def test_descuento_volumen(self, calc, cantidad, descuento_esperado, faker_seeded):
        # Precio = 10, sin descuento base (0%). Subtotal = 10 * cantidad.
        precio = faker_seeded.pyfloat(min_value=5.0, max_value=50.0, right_digits=2)
        resultado = calc.calcular(precio, 0, cantidad=cantidad)
        
        # El descuento esperado es un porcentaje del subtotal
        ahorro_esperado = (precio * cantidad) * (descuento_esperado / 100)
        assert resultado["ahorro_volumen"] == pytest.approx(ahorro_esperado)

    def test_descuento_volumen_con_faker(self, calc, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=5.0, max_value=200.0, right_digits=2)
        cantidad = faker_seeded.random_element([1, 4, 5, 9, 10, 12])
        resultado = calc.calcular(precio, 0, cantidad=cantidad)

        if 5 <= cantidad <= 9:
            pct = 0.05
        elif cantidad >= 10:
            pct = 0.10
        else:
            pct = 0.0

        ahorro_esperado = round(precio * cantidad * pct, 2)
        assert resultado["ahorro_volumen"] == pytest.approx(ahorro_esperado)

    @pytest.mark.parametrize("nivel, descuento_esperado", [
        ("BRONCE", 0.0),
        ("PLATA", 3.0),
        ("ORO", 5.0),
        ("PLATINO", 10.0),
        ("INEXISTENTE", 0.0)
    ])
    def test_fidelidad(self, calc, nivel, descuento_esperado, faker_seeded):
        # Precio = 100, descuento base = 0.
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = calc.calcular(precio, 0, nivel_fidelidad=nivel)
        
        ahorro_esperado = precio * (descuento_esperado / 100)
        assert resultado["ahorro_fidelidad"] == pytest.approx(ahorro_esperado)

    def test_cupon_valido_porcentaje(self, calc, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = calc.calcular(precio, 0, codigo_cupon="PROMO10", fecha_actual_simulada=date(2023, 1, 1))
        assert resultado["ahorro_cupon"] == round(precio * 0.10, 2)
        assert resultado["precio_final"] == round(precio * 0.90, 2)

    def test_cupon_valido_fijo(self, calc, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = calc.calcular(precio, 0, codigo_cupon="FIJO15", fecha_actual_simulada=date(2023, 1, 1))
        assert resultado["ahorro_cupon"] == 15.0
        assert resultado["precio_final"] == round(precio - 15.0, 2)

    def test_cupon_fijo_no_supera_precio(self, calc, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=1.0, max_value=14.99, right_digits=2)
        resultado = calc.calcular(precio, 0, codigo_cupon="FIJO15", fecha_actual_simulada=date(2023, 1, 1))
        assert resultado["ahorro_cupon"] == round(precio, 2)
        assert resultado["precio_final"] == 0.0

    def test_cupon_inexistente(self, calc, faker_seeded):
        with pytest.raises(CuponInvalidoError, match="no existe"):
            calc.calcular(100, 0, codigo_cupon=faker_seeded.bothify(text="??????"))

    def test_cupon_expirado(self, calc, faker_seeded):
        # El cupón "EXPIRADO" vence el 2020-01-01. Simulamos fecha actual en 2023.
        with pytest.raises(CuponInvalidoError, match="ha expirado"):
            calc.calcular(100, 0, codigo_cupon="EXPIRADO", fecha_actual_simulada=faker_seeded.date_between_dates(date(2021, 1, 1), date(2026, 1, 1)))

    def test_generador_recibo(self, calc, faker_seeded):
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        resultado = calc.calcular(precio, 10, cantidad=5, nivel_fidelidad="ORO", codigo_cupon="PROMO10", fecha_actual_simulada=date(2023,1,1))
        # Validar el texto
        recibo = GeneradorRecibo.generar(resultado)
        assert "--- RECIBO DE COMPRA ---" in recibo
        assert f"Precio original (x5): ${resultado['subtotal']:.2f}" in recibo
        assert f"Descuento base (10%): -${resultado['ahorro_base']:.2f}" in recibo
        assert f"Descuento por volumen: -${resultado['ahorro_volumen']:.2f}" in recibo
        assert f"Beneficio fidelidad: -${resultado['ahorro_fidelidad']:.2f}" in recibo
        assert f"Cupón aplicado: -${resultado['ahorro_cupon']:.2f}" in recibo
        assert "TOTAL A PAGAR:" in recibo
