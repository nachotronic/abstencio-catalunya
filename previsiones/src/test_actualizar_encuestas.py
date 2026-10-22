import pathlib, sys, unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from actualizar_encuestas import ambito, campo, muestra  # noqa: E402
from cotejar_wikipedia import celdas, fechas, numero  # noqa: E402


class Electografica(unittest.TestCase):
    def test_campo(self):
        self.assertEqual(campo('01-14/10/2026'), ('2026-10-01', '2026-10-14'))
        self.assertEqual(campo('29/09-01/10/2026'), ('2026-09-29', '2026-10-01'))
        self.assertEqual(campo('28/05–01/06/2026'), ('2026-05-28', '2026-06-01'))
        self.assertEqual(campo('07/09/2026'), ('2026-09-07', '2026-09-07'))
        self.assertEqual(campo('28/12-03/01/2027'), ('2026-12-28', '2027-01-03'))
        self.assertEqual(campo('03/2026'), ('', ''))
        self.assertEqual(campo(''), ('', ''))

    def test_muestra_y_ambito(self):
        self.assertEqual(muestra('3.007 entrevistas'), 3007)
        self.assertEqual(muestra('No publicado'), '')
        self.assertEqual(ambito('GALICIA (Congreso)'), 'GALICIA')
        self.assertEqual(ambito('GALICIA ▪ Elecciones generales ▪ Sondeo Sondaxe ▪ Junio 2018'), 'GALICIA')
        self.assertEqual(ambito('COMUNIDAD VALENCIANA (Congreso)'), 'COMUNITAT VALENCIANA')


class Wikipedia(unittest.TestCase):
    def test_fechas(self):
        self.assertEqual(fechas('15–17 Oct', 2026), ('2026-10-15', '2026-10-17'))
        self.assertEqual(fechas('28 Sep–3 Oct', 2026), ('2026-09-28', '2026-10-03'))
        self.assertEqual(fechas('30 Dec 2025–3 Jan', 2026), ('2025-12-30', '2026-01-03'))
        self.assertEqual(fechas('12 Oct', 2026), ('2026-10-12', '2026-10-12'))

    def test_celdas_y_numeros(self):
        c = celdas("| {{Party shading/PP}}| '''31.5'''<br/>{{font|size=75%|text=132/137}}\n| –\n| 3,007")
        self.assertEqual(numero(c[0][1]), 31.5)
        self.assertEqual(c[1][1], '–')
        self.assertEqual(c[2][1], '3,007')


if __name__ == '__main__':
    unittest.main()
