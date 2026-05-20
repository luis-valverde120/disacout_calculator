import unittest
from calculadora import Validacion, CalculadoraDescuento

class TestValidacion(unittest.TestCase):
    def setUp(self):
        self.validacion = Validacion()

    # R2: Precio original debe ser positivo
    def test_validar_precio_positivo(self):
        self.assertTrue(self.validacion.validar_precio(100))
        self.assertTrue(self.validacion.validar_precio(0.01))

    def test_validar_precio_no_positivo(self):
        self.assertFalse(self.validacion.validar_precio(0))
        self.assertFalse(self.validacion.validar_precio(-50))

    # R1: Descuento entre 0 y 100
    def test_validar_descuento_valido(self):
        self.assertTrue(self.validacion.validar_descuento(0))
        self.assertTrue(self.validacion.validar_descuento(50))
        self.assertTrue(self.validacion.validar_descuento(100))

    def test_validar_descuento_invalido(self):
        self.assertFalse(self.validacion.validar_descuento(-1))
        self.assertFalse(self.validacion.validar_descuento(101))

class TestCalculadoraDescuento(unittest.TestCase):
    def setUp(self):
        self.calculadora = CalculadoraDescuento()

    # R3: Calcular: precio_final = precio_original * (1 - descuento/100)
    def test_calcular_descuento(self):
        self.assertEqual(self.calculadora.calcular_descuento(100, 20), 80.0)
        self.assertEqual(self.calculadora.calcular_descuento(50, 0), 50.0)
        self.assertEqual(self.calculadora.calcular_descuento(200, 100), 0.0)

    # R5: Si el descuento es >= 80%, aplicar descuento adicional del 5% (sobre el ya descontado)
    def test_aplicar_descuento_adicional_aplica(self):
        # Descuento de 80%, precio ya descontado de 100 sería 20.
        # Adicional del 5% sobre 20: 20 * 0.95 = 19
        self.assertEqual(self.calculadora.aplicar_descuento_adicional(20, 80), 19.0)
        self.assertEqual(self.calculadora.aplicar_descuento_adicional(10, 90), 9.5)

    def test_aplicar_descuento_adicional_no_aplica(self):
        # Descuento menor a 80%, no se aplica adicional
        self.assertEqual(self.calculadora.aplicar_descuento_adicional(80, 20), 80.0)
        self.assertEqual(self.calculadora.aplicar_descuento_adicional(50, 50), 50.0)

    # R4: Redondear a 2 decimales
    def test_redondear_precio(self):
        self.assertEqual(self.calculadora.redondear_precio(19.999), 20.00)
        self.assertEqual(self.calculadora.redondear_precio(19.994), 19.99)
        self.assertEqual(self.calculadora.redondear_precio(10.12345), 10.12)

class TestFlujoCompleto(unittest.TestCase):
    def setUp(self):
        self.validacion = Validacion()
        self.calculadora = CalculadoraDescuento()

    def test_flujo_normal(self):
        precio = 100
        descuento = 20
        # Validar
        self.assertTrue(self.validacion.validar_precio(precio))
        self.assertTrue(self.validacion.validar_descuento(descuento))
        # Calcular
        pf = self.calculadora.calcular_descuento(precio, descuento)
        pf = self.calculadora.aplicar_descuento_adicional(pf, descuento)
        pf = self.calculadora.redondear_precio(pf)
        
        self.assertEqual(pf, 80.0)

    def test_flujo_con_descuento_adicional(self):
        precio = 100
        descuento = 85
        # Validar
        self.assertTrue(self.validacion.validar_precio(precio))
        self.assertTrue(self.validacion.validar_descuento(descuento))
        # Calcular
        pf = self.calculadora.calcular_descuento(precio, descuento)
        pf = self.calculadora.aplicar_descuento_adicional(pf, descuento)
        pf = self.calculadora.redondear_precio(pf)
        
        # 100 * 0.15 = 15.0
        # 15.0 * 0.95 = 14.25
        self.assertEqual(pf, 14.25)

if __name__ == '__main__':
    unittest.main()
