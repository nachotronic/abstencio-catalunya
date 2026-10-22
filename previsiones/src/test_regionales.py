import sys, pathlib, unittest
from datetime import date

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import regionales as R  # noqa: E402


class TestRegionales(unittest.TestCase):
    def test_ajusta_mueve_solo_el_territorio_encuestado(self):
        c = np.array([[.30, .20], [.30, .20], [.30, .20]])
        validos = np.array([100., 300., 600.])
        med = {('01', '02'): {'A': .45}}   # el modelo da 0,30; la encuesta, 0,45
        out = R.ajusta(c, ['01', '02', '03'], validos, med, ['A', 'B'], 1)
        np.testing.assert_allclose(out[:2, 0], .45)
        np.testing.assert_allclose(out[2], c[2])
        np.testing.assert_allclose(out[:, 1], c[:, 1])
        np.testing.assert_allclose(R.ajusta(c, ['01', '02', '03'], validos, med, ['A', 'B'], .5)[0, 0], .30 * 1.5 ** .5)
        self.assertIs(R.ajusta(c, ['01', '02', '03'], validos, med, ['A', 'B'], 0), c)

    def test_medias_ventana_y_suma_de_columnas(self):
        d = pd.DataFrame({'provs': [('31',)] * 3, 'fecha': [date(2023, 7, 10), date(2023, 7, 10), date(2023, 1, 1)],
                          'n': [1000] * 3, 'SUMAR': [10., 12., 50.], 'PODEMOS': [2., None, None], 'PP': [None] * 3})
        m = R.medias(d, date(2023, 7, 18), ['SUMAR', 'PP'], {'SUMAR': ['SUMAR', 'PODEMOS']})
        self.assertAlmostEqual(m[('31',)]['SUMAR'], .12)   # la de enero queda fuera; 10 + 2 y 12
        self.assertNotIn('PP', m[('31',)])


if __name__ == '__main__':
    unittest.main()
