"""
Tests para el módulo calculadora.py usando pytest y TDD.
Prueba todas las clases y funcionalidades del sistema de descuentos.
"""

import pytest
from datetime import date
import sys
from pathlib import Path
from faker import Faker

# Agregar la ruta raíz al path para importar calculadora
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculadora import (
    CalculadoraError, PrecioInvalidoError, DescuentoInvalidoError, CuponInvalidoError,
    Validador, GestorCupones, ServicioFidelizacion, GeneradorRecibo, CalculadoraDescuento,
    calcular_precio_final, MostrarResultado
)


@pytest.fixture(scope="function")
def faker_seeded():
    faker = Faker()
    faker.seed_instance(12345)
    return faker


class TestExcepciones:
    """Pruebas para las excepciones personalizadas."""
    
    def test_precio_invalido_error_es_calculadora_error(self):
        """Verifica que PrecioInvalidoError hereda de CalculadoraError."""
        assert issubclass(PrecioInvalidoError, CalculadoraError)
    
    def test_descuento_invalido_error_es_calculadora_error(self):
        """Verifica que DescuentoInvalidoError hereda de CalculadoraError."""
        assert issubclass(DescuentoInvalidoError, CalculadoraError)
    
    def test_cupon_invalido_error_es_calculadora_error(self):
        """Verifica que CuponInvalidoError hereda de CalculadoraError."""
        assert issubclass(CuponInvalidoError, CalculadoraError)


class TestValidador:
    """Pruebas para la clase Validador."""
    
    def test_validar_precio_positivo(self, faker_seeded):
        """Precio positivo debe pasar sin excepciones."""
        Validador.validar_precio(faker_seeded.pyfloat(min_value=0.01, max_value=1000.0, right_digits=2))
        Validador.validar_precio(faker_seeded.pyfloat(min_value=0.01, max_value=1000.0, right_digits=2))
    
    def test_validar_precio_cero_lanza_excepcion(self, faker_seeded):
        """Precio de cero debe lanzar PrecioInvalidoError."""
        with pytest.raises(PrecioInvalidoError):
            Validador.validar_precio(faker_seeded.pyfloat(min_value=0.0, max_value=0.0))
    
    def test_validar_precio_negativo_lanza_excepcion(self, faker_seeded):
        """Precio negativo debe lanzar PrecioInvalidoError."""
        with pytest.raises(PrecioInvalidoError):
            Validador.validar_precio(faker_seeded.pyfloat(min_value=-1000.0, max_value=-0.01, right_digits=2))
    
    def test_validar_descuento_valido_0_a_100(self, faker_seeded):
        """Descuentos entre 0 y 100 deben ser válidos."""
        Validador.validar_descuento(faker_seeded.pyfloat(min_value=0.0, max_value=100.0, right_digits=2))
        Validador.validar_descuento(faker_seeded.pyfloat(min_value=0.0, max_value=100.0, right_digits=2))
        Validador.validar_descuento(faker_seeded.pyfloat(min_value=0.0, max_value=100.0, right_digits=2))
    
    def test_validar_descuento_negativo_lanza_excepcion(self, faker_seeded):
        """Descuento negativo debe lanzar DescuentoInvalidoError."""
        with pytest.raises(DescuentoInvalidoError):
            Validador.validar_descuento(faker_seeded.pyfloat(min_value=-100.0, max_value=-0.01, right_digits=2))
    
    def test_validar_descuento_mayor_100_lanza_excepcion(self, faker_seeded):
        """Descuento mayor a 100 debe lanzar DescuentoInvalidoError."""
        with pytest.raises(DescuentoInvalidoError):
            Validador.validar_descuento(faker_seeded.pyfloat(min_value=100.01, max_value=200.0, right_digits=2))


class TestGestorCupones:
    """Pruebas para la clase GestorCupones."""
    
    def test_obtener_cupones_existentes(self):
        """Debe retornar tipo y valor de cupones válidos."""
        gestor = GestorCupones()
        
        tipo, valor = gestor.obtener_descuento_cupon("PROMO10")
        assert tipo == "porcentaje"
        assert valor == 10.0
        
        tipo, valor = gestor.obtener_descuento_cupon("FIJO15")
        assert tipo == "fijo"
        assert valor == 15.0
    
    def test_cupones_inexistentes_lanza_excepcion(self, faker_seeded):
        """Cupón no registrado debe lanzar CuponInvalidoError."""
        gestor = GestorCupones()
        with pytest.raises(CuponInvalidoError):
            gestor.obtener_descuento_cupon(faker_seeded.bothify(text="??????"))
    
    def test_cupones_expirados_lanza_excepcion(self, faker_seeded):
        """Cupón expirado debe lanzar CuponInvalidoError."""
        gestor = GestorCupones()
        fecha_futura = faker_seeded.date_between_dates(date(2021, 1, 1), date(2026, 1, 1))
        with pytest.raises(CuponInvalidoError):
            gestor.obtener_descuento_cupon("EXPIRADO", fecha_futura)
    
    def test_cupones_validos_con_fecha_anterior_a_expiracion(self, faker_seeded):
        """Cupón debe ser válido si la fecha está antes de la expiración."""
        gestor = GestorCupones()
        fecha_valida = faker_seeded.date_between_dates(date(2030, 1, 1), date(2090, 1, 1))
        tipo, valor = gestor.obtener_descuento_cupon("PROMO10", fecha_valida)
        assert tipo == "porcentaje"
        assert valor == 10.0


class TestServicioFidelizacion:
    """Pruebas para la clase ServicioFidelizacion."""
    
    def test_obtener_descuento_bronce(self):
        """Nivel BRONCE debe retornar 0% de descuento."""
        assert ServicioFidelizacion.obtener_descuento_nivel("BRONCE") == 0.0
    
    def test_obtener_descuento_plata(self):
        """Nivel PLATA debe retornar 3% de descuento."""
        assert ServicioFidelizacion.obtener_descuento_nivel("PLATA") == 3.0
    
    def test_obtener_descuento_oro(self):
        """Nivel ORO debe retornar 5% de descuento."""
        assert ServicioFidelizacion.obtener_descuento_nivel("ORO") == 5.0
    
    def test_obtener_descuento_platino(self):
        """Nivel PLATINO debe retornar 10% de descuento."""
        assert ServicioFidelizacion.obtener_descuento_nivel("PLATINO") == 10.0
    
    def test_nivel_desconocido_retorna_cero(self):
        """Nivel no registrado debe retornar 0%."""
        assert ServicioFidelizacion.obtener_descuento_nivel("DESCONOCIDO") == 0.0
    
    def test_nivel_case_insensitive(self):
        """Los niveles deben ser case-insensitive."""
        assert ServicioFidelizacion.obtener_descuento_nivel("plata") == 3.0
        assert ServicioFidelizacion.obtener_descuento_nivel("ORO") == 5.0


class TestGeneradorRecibo:
    """Pruebas para la clase GeneradorRecibo."""
    
    def test_generar_recibo_basico(self, faker_seeded):
        """Debe generar un recibo con información básica."""
        cantidad = faker_seeded.random_int(min=1, max=3)
        subtotal = round(faker_seeded.pyfloat(min_value=50.0, max_value=300.0, right_digits=2), 2)
        descuento_base = faker_seeded.random_int(min=1, max=30)
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
            "ahorro_total": round(subtotal - precio_final, 2),
            "precio_final": precio_final
        }
        
        recibo = GeneradorRecibo.generar(desglose)
        assert "RECIBO DE COMPRA" in recibo
        assert f"Precio original (x{cantidad}): ${subtotal:.2f}" in recibo
        assert f"TOTAL A PAGAR: ${precio_final:.2f}" in recibo
        assert f"Descuento base ({descuento_base}%): -${ahorro_base:.2f}" in recibo
    
    def test_recibo_incluye_descuentos_aplicables(self, faker_seeded):
        """El recibo debe incluir todos los descuentos aplicados."""
        cantidad = faker_seeded.random_int(min=5, max=10)
        subtotal = round(faker_seeded.pyfloat(min_value=200.0, max_value=800.0, right_digits=2), 2)
        descuento_base = faker_seeded.random_int(min=10, max=30)
        desglose = {
            "cantidad": cantidad,
            "subtotal": subtotal,
            "descuento_base_pct": descuento_base,
            "ahorro_base": round(subtotal * (descuento_base / 100), 2),
            "ahorro_volumen": round(subtotal * 0.05, 2),
            "ahorro_cupon": round(subtotal * 0.04, 2),
            "ahorro_fidelidad": round(subtotal * 0.03, 2),
            "ahorro_adicional_r5": 0.0,
            "ahorro_total": round(subtotal * 0.36, 2),
            "precio_final": round(subtotal * 0.64, 2)
        }
        
        recibo = GeneradorRecibo.generar(desglose)
        assert "Descuento por volumen" in recibo
        assert "Cupón aplicado" in recibo
        assert "Beneficio fidelidad" in recibo


class TestCalculadoraDescuento:
    """Pruebas para la clase principal CalculadoraDescuento."""
    
    def test_calculo_descuento_basico(self, faker_seeded):
        """Descuento base R3 debe aplicarse correctamente."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=300.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=1.0, max_value=30.0, right_digits=2)
        resultado = calc.calcular(precio=precio, descuento_base=descuento)
        
        assert resultado["subtotal"] == round(precio, 2)
        assert resultado["ahorro_base"] == round(precio * (descuento / 100), 2)
        assert resultado["precio_final"] == round(precio - (precio * (descuento / 100)), 2)
    
    def test_precio_cero_lanza_excepcion(self, faker_seeded):
        """Precio de cero debe lanzar excepción."""
        calc = CalculadoraDescuento()
        with pytest.raises(PrecioInvalidoError):
            calc.calcular(precio=faker_seeded.pyfloat(min_value=0.0, max_value=0.0), descuento_base=10.0)
    
    def test_descuento_fuera_rango_lanza_excepcion(self, faker_seeded):
        """Descuento fuera de 0-100 debe lanzar excepción."""
        calc = CalculadoraDescuento()
        with pytest.raises(DescuentoInvalidoError):
            calc.calcular(precio=100.0, descuento_base=faker_seeded.pyfloat(min_value=100.01, max_value=200.0, right_digits=2))
    
    def test_cantidad_invalida_lanza_excepcion(self, faker_seeded):
        """Cantidad menor a 1 debe lanzar excepción."""
        calc = CalculadoraDescuento()
        with pytest.raises(ValueError):
            calc.calcular(precio=100.0, descuento_base=10.0, cantidad=faker_seeded.random_int(min=-3, max=0))
    
    def test_descuento_mayor_80_aplica_5_adicional(self, faker_seeded):
        """R5: Si descuento >= 80%, aplicar 5% adicional."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=80.0, max_value=100.0, right_digits=2)
        resultado = calc.calcular(precio=precio, descuento_base=descuento)
        
        base = precio * (1 - descuento / 100)
        esperado_adicional = round(base * 0.05, 2)
        esperado_final = round(base - (base * 0.05), 2)
        assert resultado["ahorro_adicional_r5"] == esperado_adicional
        assert resultado["precio_final"] == esperado_final
    
    def test_descuento_menor_80_no_aplica_5_adicional(self, faker_seeded):
        """R5: Si descuento < 80%, no aplicar el 5% adicional."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=79.0, right_digits=2)
        resultado = calc.calcular(precio=precio, descuento_base=descuento)
        
        assert resultado["ahorro_adicional_r5"] == 0.0
    
    def test_cantidad_5_a_9_aplica_descuento_volumen_5(self, faker_seeded):
        """Cantidad entre 5 y 9 debe aplicar 5% descuento por volumen."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        cantidad = faker_seeded.random_int(min=5, max=9)
        resultado = calc.calcular(precio=precio, descuento_base=10.0, cantidad=cantidad)
        
        precio_actual = round(precio * cantidad * (1 - 0.10), 2)
        assert resultado["cantidad"] == cantidad
        assert resultado["ahorro_volumen"] == pytest.approx(precio_actual * 0.05, abs=0.01)
    
    def test_cantidad_mayor_10_aplica_descuento_volumen_10(self, faker_seeded):
        """Cantidad >= 10 debe aplicar 10% descuento por volumen."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        cantidad = faker_seeded.random_int(min=10, max=15)
        resultado = calc.calcular(precio=precio, descuento_base=10.0, cantidad=cantidad)
        
        precio_actual = round(precio * cantidad * (1 - 0.10), 2)
        assert resultado["cantidad"] == cantidad
        assert resultado["ahorro_volumen"] == pytest.approx(precio_actual * 0.10, abs=0.01)
    
    def test_cantidad_menor_5_sin_descuento_volumen(self, faker_seeded):
        """Cantidad menor a 5 no debe aplicar descuento por volumen."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        cantidad = faker_seeded.random_int(min=1, max=4)
        resultado = calc.calcular(precio=precio, descuento_base=10.0, cantidad=cantidad)
        
        assert resultado["ahorro_volumen"] == 0.0
    
    def test_nivel_fidelidad_aplica_correctamente(self, faker_seeded):
        """El nivel de fidelidad debe aplicar el descuento correspondiente."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=20.0, right_digits=2)
        resultado = calc.calcular(precio=precio, descuento_base=descuento, nivel_fidelidad="ORO")
        base = precio * (1 - descuento / 100)
        assert resultado["ahorro_fidelidad"] == pytest.approx(base * 0.05, abs=0.01)
    
    def test_cupon_porcentaje(self, faker_seeded):
        """Cupón de descuento porcentual debe aplicarse correctamente."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=20.0, right_digits=2)
        resultado = calc.calcular(
            precio=precio,
            descuento_base=descuento,
            codigo_cupon="PROMO10"
        )
        
        base = precio * (1 - descuento / 100)
        assert resultado["ahorro_cupon"] == pytest.approx(base * 0.10, abs=0.01)
        assert resultado["precio_final"] == pytest.approx(base * 0.90, abs=0.01)
    
    def test_cupon_fijo(self, faker_seeded):
        """Cupón de descuento fijo debe aplicarse correctamente."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=20.0, right_digits=2)
        resultado = calc.calcular(
            precio=precio,
            descuento_base=descuento,
            codigo_cupon="FIJO15"
        )
        
        base = precio * (1 - descuento / 100)
        assert resultado["ahorro_cupon"] == round(min(15.0, base), 2)
        assert resultado["precio_final"] == round(base - min(15.0, base), 2)
    
    def test_cupon_fijo_no_puede_exceder_precio(self, faker_seeded):
        """Cupón fijo no puede descontar más que el precio actual."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=5.0, max_value=20.0, right_digits=2)
        resultado = calc.calcular(
            precio=precio,
            descuento_base=50.0,
            codigo_cupon="FIJO15"  # Intenta descontar 15 de algo que vale 5
        )
        
        # Después del 50% descuento: precio * 0.5
        assert resultado["ahorro_cupon"] == round(precio * 0.5, 2)
        assert resultado["precio_final"] == 0.0
    
    def test_precio_no_puede_ser_negativo(self, faker_seeded):
        """El precio final nunca debe ser negativo."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=100.0, max_value=500.0, right_digits=2)
        resultado = calc.calcular(
            precio=precio,
            descuento_base=99.0,
            codigo_cupon="FIJO15",
            nivel_fidelidad="PLATINO"
        )
        
        assert resultado["precio_final"] >= 0.0
    
    def test_redondeo_a_dos_decimales(self, faker_seeded):
        """R4: El precio debe redondearse a 2 decimales."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=10.0, max_value=200.0, right_digits=4)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=80.0, right_digits=4)
        resultado = calc.calcular(precio=precio, descuento_base=descuento)
        
        # Verificar que tiene máximo 2 decimales
        assert len(str(resultado["precio_final"]).split('.')[-1]) <= 2
    
    def test_multiplos_descuentos_se_aplican_en_cascada(self, faker_seeded):
        """Varios descuentos deben aplicarse secuencialmente."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        resultado = calc.calcular(
            precio=precio,
            descuento_base=20.0,
            cantidad=10,  # 10% descuento volumen
            nivel_fidelidad="ORO",  # 5% fidelidad
            codigo_cupon="PROMO10"  # 10% cupón
        )
        
        # Todos los descuentos deben estar presentes
        assert resultado["ahorro_base"] > 0
        assert resultado["ahorro_volumen"] > 0
        assert resultado["ahorro_fidelidad"] > 0
        assert resultado["ahorro_cupon"] > 0
        assert resultado["precio_final"] < 100.0


class TestFuncionCalcularPrecioFinal:
    """Pruebas para la función heredada calcular_precio_final."""
    
    def test_calcular_precio_final_basico(self, faker_seeded):
        """Función debe retornar precio con descuento."""
        precio = faker_seeded.pyfloat(min_value=50.0, max_value=200.0, right_digits=2)
        descuento = faker_seeded.pyfloat(min_value=0.0, max_value=30.0, right_digits=2)
        resultado = calcular_precio_final(precio, descuento)
        assert resultado == round(precio * (1 - descuento / 100), 2)
    
    def test_calcular_precio_final_precio_invalido(self, faker_seeded):
        """Debe lanzar ValueError para precio inválido."""
        with pytest.raises(ValueError):
            calcular_precio_final(faker_seeded.pyfloat(min_value=0.0, max_value=0.0), 10.0)
    
    def test_calcular_precio_final_descuento_invalido(self, faker_seeded):
        """Debe lanzar ValueError para descuento inválido."""
        with pytest.raises(ValueError):
            calcular_precio_final(100.0, faker_seeded.pyfloat(min_value=100.01, max_value=200.0, right_digits=2))


class TestMostrarResultado:
    """Pruebas para la clase MostrarResultado."""
    
    def test_mostrar_resultado(self, capsys, faker_seeded):
        """MostrarResultado debe imprimir el resultado."""
        mostrador = MostrarResultado()
        valor = faker_seeded.pyfloat(min_value=1.0, max_value=200.0, right_digits=2)
        mostrador.mostrar(valor)
        
        capturado = capsys.readouterr()
        assert str(valor) in capturado.out


class TestCasosIntegracionComplejos:
    """Casos de integración complejos combinando múltiples características."""
    
    def test_cliente_platino_con_volumenes_altos_y_cupon(self, faker_seeded):
        """Cliente PLATINO comprando 15 unidades con cupón PROMO10."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=20.0, max_value=100.0, right_digits=2)
        resultado = calc.calcular(
            precio=precio,
            descuento_base=15.0,
            cantidad=15,
            nivel_fidelidad="PLATINO",
            codigo_cupon="PROMO10"
        )
        
        assert resultado["cantidad"] == 15
        assert resultado["subtotal"] == round(precio * 15, 2)
        # Todos los descuentos deben aplicarse
        assert resultado["ahorro_total"] > 0
        assert resultado["precio_final"] < resultado["subtotal"]
    
    def test_descuento_muy_alto_con_multiplos_beneficios(self, faker_seeded):
        """Descuento >= 80% con múltiples beneficios activados."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=500.0, max_value=1500.0, right_digits=2)
        resultado = calc.calcular(
            precio=precio,
            descuento_base=85.0,
            cantidad=5,
            nivel_fidelidad="ORO"
        )
        
        # El 5% adicional debe estar presente
        assert resultado["ahorro_adicional_r5"] > 0
        # El descuento por volumen debe estar presente
        assert resultado["ahorro_volumen"] > 0
    
    def test_flujo_completo_con_todos_descuentos_maximos(self, faker_seeded):
        """Prueba con todos los descuentos al máximo."""
        calc = CalculadoraDescuento()
        precio = faker_seeded.pyfloat(min_value=80.0, max_value=200.0, right_digits=2)
        resultado = calc.calcular(
            precio=precio,
            descuento_base=90.0,
            cantidad=20,
            nivel_fidelidad="PLATINO",
            codigo_cupon="PROMO10"
        )
        
        # Verificar estructura del resultado
        assert "precio_final" in resultado
        assert "ahorro_total" in resultado
        assert resultado["precio_final"] >= 0
        assert resultado["precio_final"] <= resultado["subtotal"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
