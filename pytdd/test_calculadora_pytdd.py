"""
Tests para el módulo calculadora.py usando pytest y TDD.
Prueba todas las clases y funcionalidades del sistema de descuentos.
"""

import pytest
from datetime import date
import sys
from pathlib import Path

# Agregar la ruta raíz al path para importar calculadora
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculadora import (
    CalculadoraError, PrecioInvalidoError, DescuentoInvalidoError, CuponInvalidoError,
    Validador, GestorCupones, ServicioFidelizacion, GeneradorRecibo, CalculadoraDescuento,
    calcular_precio_final, MostrarResultado
)


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
    
    def test_validar_precio_positivo(self):
        """Precio positivo debe pasar sin excepciones."""
        Validador.validar_precio(100.0)
        Validador.validar_precio(0.01)
    
    def test_validar_precio_cero_lanza_excepcion(self):
        """Precio de cero debe lanzar PrecioInvalidoError."""
        with pytest.raises(PrecioInvalidoError):
            Validador.validar_precio(0)
    
    def test_validar_precio_negativo_lanza_excepcion(self):
        """Precio negativo debe lanzar PrecioInvalidoError."""
        with pytest.raises(PrecioInvalidoError):
            Validador.validar_precio(-10.0)
    
    def test_validar_descuento_valido_0_a_100(self):
        """Descuentos entre 0 y 100 deben ser válidos."""
        Validador.validar_descuento(0)
        Validador.validar_descuento(50)
        Validador.validar_descuento(100)
    
    def test_validar_descuento_negativo_lanza_excepcion(self):
        """Descuento negativo debe lanzar DescuentoInvalidoError."""
        with pytest.raises(DescuentoInvalidoError):
            Validador.validar_descuento(-1)
    
    def test_validar_descuento_mayor_100_lanza_excepcion(self):
        """Descuento mayor a 100 debe lanzar DescuentoInvalidoError."""
        with pytest.raises(DescuentoInvalidoError):
            Validador.validar_descuento(101)


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
    
    def test_cupones_inexistentes_lanza_excepcion(self):
        """Cupón no registrado debe lanzar CuponInvalidoError."""
        gestor = GestorCupones()
        with pytest.raises(CuponInvalidoError):
            gestor.obtener_descuento_cupon("NOEXISTE")
    
    def test_cupones_expirados_lanza_excepcion(self):
        """Cupón expirado debe lanzar CuponInvalidoError."""
        gestor = GestorCupones()
        fecha_futura = date(2025, 1, 1)
        with pytest.raises(CuponInvalidoError):
            gestor.obtener_descuento_cupon("EXPIRADO", fecha_futura)
    
    def test_cupones_validos_con_fecha_anterior_a_expiracion(self):
        """Cupón debe ser válido si la fecha está antes de la expiración."""
        gestor = GestorCupones()
        fecha_valida = date(2050, 1, 1)
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
    
    def test_generar_recibo_basico(self):
        """Debe generar un recibo con información básica."""
        desglose = {
            "cantidad": 1,
            "subtotal": 100.0,
            "descuento_base_pct": 10,
            "ahorro_base": 10.0,
            "ahorro_volumen": 0.0,
            "ahorro_cupon": 0.0,
            "ahorro_fidelidad": 0.0,
            "ahorro_adicional_r5": 0.0,
            "ahorro_total": 10.0,
            "precio_final": 90.0
        }
        
        recibo = GeneradorRecibo.generar(desglose)
        assert "RECIBO DE COMPRA" in recibo
        assert "$100.00" in recibo
        assert "$90.00" in recibo
        assert "10%" in recibo
    
    def test_recibo_incluye_descuentos_aplicables(self):
        """El recibo debe incluir todos los descuentos aplicados."""
        desglose = {
            "cantidad": 5,
            "subtotal": 500.0,
            "descuento_base_pct": 20,
            "ahorro_base": 100.0,
            "ahorro_volumen": 40.0,
            "ahorro_cupon": 25.0,
            "ahorro_fidelidad": 15.0,
            "ahorro_adicional_r5": 0.0,
            "ahorro_total": 180.0,
            "precio_final": 320.0
        }
        
        recibo = GeneradorRecibo.generar(desglose)
        assert "Descuento por volumen" in recibo
        assert "Cupón aplicado" in recibo
        assert "Beneficio fidelidad" in recibo


class TestCalculadoraDescuento:
    """Pruebas para la clase principal CalculadoraDescuento."""
    
    def test_calculo_descuento_basico(self):
        """Descuento base R3 debe aplicarse correctamente."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(precio=100.0, descuento_base=10.0)
        
        assert resultado["subtotal"] == 100.0
        assert resultado["ahorro_base"] == 10.0
        assert resultado["precio_final"] == 90.0
    
    def test_precio_cero_lanza_excepcion(self):
        """Precio de cero debe lanzar excepción."""
        calc = CalculadoraDescuento()
        with pytest.raises(PrecioInvalidoError):
            calc.calcular(precio=0.0, descuento_base=10.0)
    
    def test_descuento_fuera_rango_lanza_excepcion(self):
        """Descuento fuera de 0-100 debe lanzar excepción."""
        calc = CalculadoraDescuento()
        with pytest.raises(DescuentoInvalidoError):
            calc.calcular(precio=100.0, descuento_base=150.0)
    
    def test_cantidad_invalida_lanza_excepcion(self):
        """Cantidad menor a 1 debe lanzar excepción."""
        calc = CalculadoraDescuento()
        with pytest.raises(ValueError):
            calc.calcular(precio=100.0, descuento_base=10.0, cantidad=0)
    
    def test_descuento_mayor_80_aplica_5_adicional(self):
        """R5: Si descuento >= 80%, aplicar 5% adicional."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(precio=100.0, descuento_base=80.0)
        
        # Después del 80% descuento: 100 - 80 = 20
        # Luego 5% del 20: 1.0
        assert resultado["ahorro_adicional_r5"] == 1.0
        assert resultado["precio_final"] == 19.0
    
    def test_descuento_menor_80_no_aplica_5_adicional(self):
        """R5: Si descuento < 80%, no aplicar el 5% adicional."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(precio=100.0, descuento_base=79.0)
        
        assert resultado["ahorro_adicional_r5"] == 0.0
    
    def test_cantidad_5_a_9_aplica_descuento_volumen_5(self):
        """Cantidad entre 5 y 9 debe aplicar 5% descuento por volumen."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(precio=100.0, descuento_base=10.0, cantidad=7)
        
        # Subtotal: 700, descuento base: 70, resta: 630
        # Descuento volumen 5%: 31.5
        assert resultado["cantidad"] == 7
        assert resultado["ahorro_volumen"] == pytest.approx(31.5, abs=0.01)
    
    def test_cantidad_mayor_10_aplica_descuento_volumen_10(self):
        """Cantidad >= 10 debe aplicar 10% descuento por volumen."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(precio=100.0, descuento_base=10.0, cantidad=10)
        
        # Subtotal: 1000, descuento base: 100, resta: 900
        # Descuento volumen 10%: 90
        assert resultado["cantidad"] == 10
        assert resultado["ahorro_volumen"] == pytest.approx(90.0, abs=0.01)
    
    def test_cantidad_menor_5_sin_descuento_volumen(self):
        """Cantidad menor a 5 no debe aplicar descuento por volumen."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(precio=100.0, descuento_base=10.0, cantidad=1)
        
        assert resultado["ahorro_volumen"] == 0.0
    
    def test_nivel_fidelidad_aplica_correctamente(self):
        """El nivel de fidelidad debe aplicar el descuento correspondiente."""
        calc = CalculadoraDescuento()
        
        # ORO = 5%
        resultado = calc.calcular(precio=100.0, descuento_base=10.0, nivel_fidelidad="ORO")
        # Después del descuento base: 90
        # 5% de 90: 4.5
        assert resultado["ahorro_fidelidad"] == pytest.approx(4.5, abs=0.01)
    
    def test_cupon_porcentaje(self):
        """Cupón de descuento porcentual debe aplicarse correctamente."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(
            precio=100.0,
            descuento_base=10.0,
            codigo_cupon="PROMO10"
        )
        
        # Después del descuento base: 90
        # 10% de 90: 9
        assert resultado["ahorro_cupon"] == pytest.approx(9.0, abs=0.01)
        assert resultado["precio_final"] == pytest.approx(81.0, abs=0.01)
    
    def test_cupon_fijo(self):
        """Cupón de descuento fijo debe aplicarse correctamente."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(
            precio=100.0,
            descuento_base=10.0,
            codigo_cupon="FIJO15"
        )
        
        # Después del descuento base: 90
        # Cupón fijo de 15 (no más del 90)
        assert resultado["ahorro_cupon"] == 15.0
        assert resultado["precio_final"] == 75.0
    
    def test_cupon_fijo_no_puede_exceder_precio(self):
        """Cupón fijo no puede descontar más que el precio actual."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(
            precio=10.0,
            descuento_base=50.0,
            codigo_cupon="FIJO15"  # Intenta descontar 15 de algo que vale 5
        )
        
        # Después del 50% descuento: 5
        # Cupón fijo de 15, pero solo 5 disponible
        assert resultado["ahorro_cupon"] == 5.0
        assert resultado["precio_final"] == 0.0
    
    def test_precio_no_puede_ser_negativo(self):
        """El precio final nunca debe ser negativo."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(
            precio=100.0,
            descuento_base=99.0,
            codigo_cupon="FIJO15",
            nivel_fidelidad="PLATINO"
        )
        
        assert resultado["precio_final"] >= 0.0
    
    def test_redondeo_a_dos_decimales(self):
        """R4: El precio debe redondearse a 2 decimales."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(precio=33.33, descuento_base=33.33)
        
        # Verificar que tiene máximo 2 decimales
        assert len(str(resultado["precio_final"]).split('.')[-1]) <= 2
    
    def test_multiplos_descuentos_se_aplican_en_cascada(self):
        """Varios descuentos deben aplicarse secuencialmente."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(
            precio=100.0,
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
    
    def test_calcular_precio_final_basico(self):
        """Función debe retornar precio con descuento."""
        resultado = calcular_precio_final(100.0, 10.0)
        assert resultado == 90.0
    
    def test_calcular_precio_final_precio_invalido(self):
        """Debe lanzar ValueError para precio inválido."""
        with pytest.raises(ValueError):
            calcular_precio_final(0.0, 10.0)
    
    def test_calcular_precio_final_descuento_invalido(self):
        """Debe lanzar ValueError para descuento inválido."""
        with pytest.raises(ValueError):
            calcular_precio_final(100.0, 150.0)


class TestMostrarResultado:
    """Pruebas para la clase MostrarResultado."""
    
    def test_mostrar_resultado(self, capsys):
        """MostrarResultado debe imprimir el resultado."""
        mostrador = MostrarResultado()
        mostrador.mostrar(99.99)
        
        capturado = capsys.readouterr()
        assert "99.99" in capturado.out


class TestCasosIntegracionComplejos:
    """Casos de integración complejos combinando múltiples características."""
    
    def test_cliente_platino_con_volumenes_altos_y_cupon(self):
        """Cliente PLATINO comprando 15 unidades con cupón PROMO10."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(
            precio=50.0,
            descuento_base=15.0,
            cantidad=15,
            nivel_fidelidad="PLATINO",
            codigo_cupon="PROMO10"
        )
        
        assert resultado["cantidad"] == 15
        assert resultado["subtotal"] == 750.0
        # Todos los descuentos deben aplicarse
        assert resultado["ahorro_total"] > 0
        assert resultado["precio_final"] < resultado["subtotal"]
    
    def test_descuento_muy_alto_con_multiplos_beneficios(self):
        """Descuento >= 80% con múltiples beneficios activados."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(
            precio=1000.0,
            descuento_base=85.0,
            cantidad=5,
            nivel_fidelidad="ORO"
        )
        
        # El 5% adicional debe estar presente
        assert resultado["ahorro_adicional_r5"] > 0
        # El descuento por volumen debe estar presente
        assert resultado["ahorro_volumen"] > 0
    
    def test_flujo_completo_con_todos_descuentos_maximos(self):
        """Prueba con todos los descuentos al máximo."""
        calc = CalculadoraDescuento()
        resultado = calc.calcular(
            precio=100.0,
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
