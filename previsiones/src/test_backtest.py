import sys, pathlib, unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import backtest as B  # noqa: E402


def provincias(filas):
    d = pd.DataFrame(filas, index=['01', '02', '03']).reindex(columns=B.LISTAS).fillna(0)
    d['validos'] = 1000
    return d


class TestCentral(unittest.TestCase):
    def setUp(self):
        # una provincia con un partido regional fuerte, sin encuesta
        self.R = {'A': provincias([{'PP': 300, 'PSOE': 300, 'VOX': 100, 'SUMAR': 100, 'CS': 100},
                                   {'PP': 200, 'PSOE': 300, 'VOX': 50, 'SUMAR': 100, 'CS': 50, 'BILDU': 280},
                                   {'PP': 400, 'PSOE': 300, 'VOX': 100, 'SUMAR': 100, 'CS': 50}])}
        self.obj = {'PP': .40, 'PSOE': .30, 'VOX': .10, 'SUMAR': .08, 'CS': 0}

    def test_metas_clava_la_media_y_conserva_el_partido_sin_encuesta(self):
        c = B.central(self.R, 'A', None, self.obj, 'metas')
        nac = c.mean(0)
        for k, t in self.obj.items():
            self.assertAlmostEqual(nac[B.LISTAS.index(k)], t, places=4)
        self.assertAlmostEqual(nac[B.LISTAS.index('BILDU')], 280 / 3000, places=4)
        self.assertTrue((c.sum(1) <= 1).all())

    def test_lista_que_no_se_presenta_queda_a_cero(self):
        for metodo in ('metas', 'tope', 'aditivo'):   # «repetir» copia las generales anteriores tal cual
            c = B.central(self.R, 'A', None, self.obj, metodo)
            self.assertEqual(c[:, B.LISTAS.index('CS')].sum(), 0)


if __name__ == '__main__':
    unittest.main()
