import pytest
from datetime import date
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

    def test_r3_calculo_descuento_normal(self):
        assert calcular_precio_final(100, 20) == 80.0
        assert calcular_precio_final(50, 10) == 45.0

    def test_r4_redondear_dos_decimales(self):
        assert calcular_precio_final(10.12345, 10) == 9.11
        assert calcular_precio_final(19.999, 0) == 20.00

    def test_r5_descuento_adicional(self):
        # 80% sobre 100 = 20; 5% adicional sobre 20 = 19.0
        assert calcular_precio_final(100, 80) == 19.0
        # 90% sobre 100 = 10; 5% adicional sobre 10 = 9.5
        assert calcular_precio_final(100, 90) == 9.5


class TestNuevasFuncionalidades:
    """Pruebas de la nueva arquitectura OOP."""

    def test_calculadora_precio_invalido(self, calc):
        with pytest.raises(PrecioInvalidoError):
            calc.calcular(-10, 10)
            
    def test_calculadora_descuento_invalido(self, calc):
        with pytest.raises(DescuentoInvalidoError):
            calc.calcular(100, 150)

    @pytest.mark.parametrize("cantidad, descuento_esperado", [
        (1, 0.0),
        (4, 0.0),
        (5, 5.0),
        (9, 5.0),
        (10, 10.0),
        (100, 10.0)
    ])
    def test_descuento_volumen(self, calc, cantidad, descuento_esperado):
        # Precio = 10, sin descuento base (0%). Subtotal = 10 * cantidad.
        resultado = calc.calcular(10, 0, cantidad=cantidad)
        
        # El descuento esperado es un porcentaje del subtotal
        ahorro_esperado = (10 * cantidad) * (descuento_esperado / 100)
        assert resultado["ahorro_volumen"] == pytest.approx(ahorro_esperado)

    @pytest.mark.parametrize("nivel, descuento_esperado", [
        ("BRONCE", 0.0),
        ("PLATA", 3.0),
        ("ORO", 5.0),
        ("PLATINO", 10.0),
        ("INEXISTENTE", 0.0)
    ])
    def test_fidelidad(self, calc, nivel, descuento_esperado):
        # Precio = 100, descuento base = 0.
        resultado = calc.calcular(100, 0, nivel_fidelidad=nivel)
        
        ahorro_esperado = 100 * (descuento_esperado / 100)
        assert resultado["ahorro_fidelidad"] == pytest.approx(ahorro_esperado)

    def test_cupon_valido_porcentaje(self, calc):
        resultado = calc.calcular(100, 0, codigo_cupon="PROMO10", fecha_actual_simulada=date(2023, 1, 1))
        assert resultado["ahorro_cupon"] == 10.0
        assert resultado["precio_final"] == 90.0

    def test_cupon_valido_fijo(self, calc):
        resultado = calc.calcular(50, 0, codigo_cupon="FIJO15", fecha_actual_simulada=date(2023, 1, 1))
        assert resultado["ahorro_cupon"] == 15.0
        assert resultado["precio_final"] == 35.0

    def test_cupon_inexistente(self, calc):
        with pytest.raises(CuponInvalidoError, match="no existe"):
            calc.calcular(100, 0, codigo_cupon="NOEXISTE")

    def test_cupon_expirado(self, calc):
        # El cupón "EXPIRADO" vence el 2020-01-01. Simulamos fecha actual en 2023.
        with pytest.raises(CuponInvalidoError, match="ha expirado"):
            calc.calcular(100, 0, codigo_cupon="EXPIRADO", fecha_actual_simulada=date(2023, 1, 1))

    def test_generador_recibo(self, calc):
        resultado = calc.calcular(100, 10, cantidad=5, nivel_fidelidad="ORO", codigo_cupon="PROMO10", fecha_actual_simulada=date(2023,1,1))
        # Validar el texto
        recibo = GeneradorRecibo.generar(resultado)
        assert "--- RECIBO DE COMPRA ---" in recibo
        assert "Precio original (x5): $500.00" in recibo
        assert "Descuento base (10%): -$50.00" in recibo
        assert "Descuento por volumen: -$22.50" in recibo
        assert "Beneficio fidelidad: -$21.38" in recibo
        assert "Cupón aplicado: -$40.61" in recibo
        assert "TOTAL A PAGAR:" in recibo
