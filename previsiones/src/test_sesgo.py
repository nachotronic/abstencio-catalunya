import sys, pathlib, unittest
from datetime import date, timedelta

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sesgo_encuestas as S  # noqa: E402


class TestEfectoCasa(unittest.TestCase):
    def test_casa_que_siempre_da_dos_puntos_mas(self):
        filas, hoy = [], date(2026, 10, 1)
        for i in range(12):
            f = hoy - timedelta(days=7 * i)
            for casa, pp in (('a', 30), ('b', 30), ('c', 32)):
                filas.append({'url_electografica': f'{casa}{i}', 'casa': casa, 'encuestadora': casa, 'cliente': None,
                              'fecha': f, 'n': 1000, 'partido_modelo': 'PP', 'voto': pp})
        ef = S.efectos_casa(pd.DataFrame(filas), hoy)
        n = 12
        self.assertAlmostEqual(ef[('c', 'PP')], 2 * n / (n + S.K), places=6)
        self.assertAlmostEqual(ef[('a', 'PP')], -1 * n / (n + S.K), places=6)


if __name__ == '__main__':
    unittest.main()
