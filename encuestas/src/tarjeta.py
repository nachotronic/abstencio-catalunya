"""Tarjeta para redes de /encuestas/ (1200x630): titular del día, mediana de cada partido y promedio de escaños.

La llama construir.py en cada actualización, así que la imagen de compartir (og:image) y la descargable cambian con
las encuestas. Necesita Pillow; si no está, construir.py sigue sin rehacer la tarjeta. Las fuentes (IBM Plex Sans,
la del sitio) van en encuestas/src/fuentes para que la imagen salga igual aquí y en GitHub Actions.
"""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont

FUENTES = pathlib.Path(__file__).resolve().parent / 'fuentes'
W, H = 1200, 630
FONDO, TINTA, GRIS, REGLA = '#fbfaf8', '#1d1a1c', '#5d585b', '#e2dddf'


def fuente(peso, tam):
    return ImageFont.truetype(str(FUENTES / f'IBMPlexSans-{peso}.ttf'), tam)


def parte(d, texto, f, ancho):
    """Corta el texto en líneas que caben en `ancho` píxeles."""
    lineas, l = [], ''
    for p in texto.split():
        prueba = f'{l} {p}'.strip()
        if d.textlength(prueba, font=f) <= ancho or not l:
            l = prueba
        else:
            lineas.append(l); l = p
    return lineas + [l]


def hemiciclo(d, cx, base, R, asientos):
    """Hemiciclo de puntos como el de la página: filas concéntricas, partidos de izquierda a derecha."""
    total = sum(n for _, n, _ in asientos)
    filas, r0 = 9, R * .38
    radios = [r0 + (R - r0) * (i + .5) / filas for i in range(filas)]
    n = [round(total * r / sum(radios)) for r in radios]
    n[-1] += total - sum(n)
    pts = []
    for r, k in zip(radios, n):
        for j in range(k):
            a = math.pi * (1 - (j / (k - 1) if k > 1 else .5))
            pts.append((a, cx + r * math.cos(a), base - r * math.sin(a)))
    pts.sort(key=lambda p: -p[0])
    rad = min(R * .5 / filas, (R - r0) / filas * .42)
    i = 0
    for _, k, color in asientos:
        for _ in range(k):
            _, x, y = pts[i]; i += 1
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=color)
    d.line((cx, base - R - 4, cx, base - r0 + 4), fill=GRIS, width=2)


def tarjeta(destino, titular, medianas, asientos, pie_hemi, actualizado):
    """medianas: [(nombre, %, color)]; asientos: [(clave, escaños, color)] en orden del hemiciclo."""
    im = Image.new('RGB', (W, H), FONDO)
    d = ImageDraw.Draw(im)
    m = 56
    d.text((m, 40), 'ENCUESTAS · ELECCIONES GENERALES DEL 29N', font=fuente('Bold', 22), fill='#1d84ce')
    ft = fuente('Bold', 46)
    y = 76
    lineas = parte(d, titular, ft, W - 2 * m)
    if len(lineas) > 3:
        ft = fuente('Bold', 38); lineas = parte(d, titular, ft, W - 2 * m)
    for l in lineas[:3]:
        d.text((m, y), l, font=ft, fill=TINTA)
        y += ft.size + 10
    y += 18
    # mediana de cada partido: barras horizontales a la izquierda
    fe, fv = fuente('Regular', 24), fuente('Bold', 24)
    d.text((m, y), 'Mediana de las encuestas', font=fuente('Bold', 22), fill=GRIS)
    y0, alto, maxv, ancho_b = y + 40, 38, max(v for _, v, _ in medianas), 330
    for i, (n, v, c) in enumerate(medianas):
        yy = y0 + i * alto
        d.text((m, yy), n, font=fe, fill=TINTA)
        largo = max(4, ancho_b * v / maxv)
        d.rectangle((m + 120, yy + 6, m + 120 + largo, yy + 28), fill=c)
        d.text((m + 130 + largo, yy), f'{v:.1f}'.replace('.', ',') + ' %', font=fv, fill=TINTA)
    # promedio de escaños: hemiciclo a la derecha
    if asientos:
        cx, R = 900, 210
        base = min(H - 92, y0 + R + 10)
        d.text((cx - R, y), 'Promedio de escaños', font=fuente('Bold', 22), fill=GRIS)
        hemiciclo(d, cx, base, R, asientos)
        fp = fuente('Regular', 20)
        d.text((cx - d.textlength(pie_hemi, font=fp) / 2, base + 8), pie_hemi, font=fp, fill=TINTA)
    # firma, siempre visible aunque la imagen circule sin enlace
    d.line((m, H - 52, W - m, H - 52), fill=REGLA, width=2)
    d.text((m, H - 42), 'mapaelectoral.es/encuestas', font=fuente('Bold', 22), fill=TINTA)
    fa = fuente('Regular', 20)
    txt = f'Actualizado el {actualizado} · Cifras de las encuestadoras'
    d.text((W - m - d.textlength(txt, font=fa), H - 40), txt, font=fa, fill=GRIS)
    im.save(destino, quality=88, optimize=True)
