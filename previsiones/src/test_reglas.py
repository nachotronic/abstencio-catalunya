"""Pruebas del reparto. Uso, desde la raíz:  python3 -m unittest discover previsiones/src"""
import json, pathlib, sys, unittest

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from reglas import ESCANOS_2023, ESCANOS_2026, circunscripciones_senado, dhondt, senado_limitado  # noqa: E402

SIM = json.load(open(AQUI.parents[1] / 'actualidad/src/sistema/simulador.json'))


class Congreso(unittest.TestCase):
    def test_magnitudes(self):
        self.assertEqual(sum(ESCANOS_2026.values()), 350)
        self.assertEqual(sum(ESCANOS_2023.values()), 350)
        self.assertEqual(len(ESCANOS_2026), 52)

    def test_dhondt_manual(self):
        # ejemplo de manual: 7 escaños, A 340.000, B 280.000, C 160.000, D 60.000 → 3, 3, 1, 0
        self.assertEqual(dhondt({'A': 340000, 'B': 280000, 'C': 160000, 'D': 60000}, 7, 840000),
                         {'A': 3, 'B': 3, 'C': 1, 'D': 0})

    def test_umbral_cuenta_el_blanco(self):
        # 2,9 % de válidos (blanco incluido) no entra aunque le tocaría escaño
        # 1.000 válidos, de ellos 30 en blanco: C con 29 votos (2,9 %) se queda fuera; con 30 (3 %), entra
        self.assertEqual(dhondt({'A': 480, 'B': 461, 'C': 29}, 50, 1000)['C'], 0)
        self.assertGreater(dhondt({'A': 480, 'B': 460, 'C': 30}, 50, 1000)['C'], 0)

    def test_ceuta_melilla(self):
        self.assertEqual(dhondt({'A': 10, 'B': 9}, 1, 19), {'A': 1, 'B': 0})

    def test_reproduce_2023(self):
        """Con los votos oficiales de 2023 (CERA incluido) sale el Congreso oficial."""
        tot = {}
        for p, r in SIM['elecciones']['2023_07'].items():
            v = {k: x for k, x in r['v'].items() if k != 'Otros'}
            for k, e in dhondt(v, ESCANOS_2023[p], r['validos']).items():
                tot[k] = tot.get(k, 0) + e
        oficial = {'PP': 137, 'PSOE': 121, 'Vox': 33, 'Sumar': 31, 'ERC': 7, 'Junts': 7, 'EH Bildu': 6, 'PNV': 5,
                   'BNG': 1, 'CC': 1, 'UPN': 1}
        self.assertEqual({k: v for k, v in tot.items() if v}, oficial)


class Senado(unittest.TestCase):
    def test_208_elegidos(self):
        c = circunscripciones_senado(SIM['provincias'])
        self.assertEqual(sum(x[3] for x in c), 208)
        self.assertEqual(len(c), 59)

    def test_voto_limitado(self):
        self.assertEqual(senado_limitado({'A': 40, 'B': 39, 'C': 20}, 4, 3), {'A': 3, 'B': 1, 'C': 0})
        self.assertEqual(senado_limitado({'A': 40, 'B': 39, 'C': 20}, 3, 2), {'A': 2, 'B': 1, 'C': 0})
        self.assertEqual(senado_limitado({'A': 40, 'B': 39}, 1, 1), {'A': 1, 'B': 0})
        self.assertEqual(senado_limitado({'A': 50, 'B': 20}, 2, 1), {'A': 2, 'B': 0})
        self.assertEqual(senado_limitado({'A': 50, 'B': 30}, 2, 1), {'A': 1, 'B': 1})

    def test_no_es_dhondt(self):
        # 50 / 45 / 5 en cuatro escaños: D'Hondt daría 2-2, el voto limitado da 3-1
        self.assertEqual(dhondt({'A': 50, 'B': 45, 'C': 5}, 4, 100)['A'], 2)
        self.assertEqual(senado_limitado({'A': 50, 'B': 45, 'C': 5}, 4, 3)['A'], 3)


if __name__ == '__main__':
    unittest.main()
