'''
This is a test file for the discount calculator.
'''
import pytest
from calculadora import calcular_precio_final

def test_r1_descuento_fuera_de_rango():
    with pytest.raises(ValueError):
        calcular_precio_final(100, 105)
    with pytest.raises(ValueError):
        calcular_precio_final(100, -10)

def test_r2_precio_no_positivo():
    with pytest.raises(ValueError):
        calcular_precio_final(0, 20)
    with pytest.raises(ValueError):
        calcular_precio_final(-50, 20)

def test_r3_calculo_descuento_normal():
    assert calcular_precio_final(100, 20) == 80.0
    assert calcular_precio_final(50, 10) == 45.0

def test_r4_redondear_dos_decimales():
    assert calcular_precio_final(10.12345, 10) == 9.11
    assert calcular_precio_final(19.999, 0) == 20.00

def test_r5_descuento_adicional():
    assert calcular_precio_final(100, 80) == 19.0
    assert calcular_precio_final(100, 90) == 9.5
