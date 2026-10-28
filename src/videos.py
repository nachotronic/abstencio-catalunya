"""Carrusel «Vídeos en X» de la portada (Nacho, 28-10-2026), entre las marcas <!--videos:portada-->, debajo del de Actualidad.

Cada tarjeta es un fotograma del vídeo (img/videos/<nombre>.jpg, 360 × 480: el tercio de arriba,
donde van los textos y las cifras; abajo queda la zona segura vacía de los Shorts) que enlaza al tuit en X.
Sin embeds de X: su widgets.js pesa más que todo el carrusel y frenaría el mapa. Mientras no se apunte
el enlace del tuit ('tuit'), la tarjeta lleva a la pestaña de vídeos del perfil.

Los vídeos (x-<nombre>.mp4) están en /mnt/project-files/videos/, nunca en el repositorio. Para añadir uno:
ponlo al principio de VIDEOS (los más nuevos delante) y lanza

    python3 src/videos.py            # fotogramas que falten + carrusel en index.html
    python3 src/movil.py             # (lo hace también src/seo.py)
"""
import html, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
VIDEOS_DIR = pathlib.Path('/mnt/project-files/videos')
PERFIL = 'https://x.com/nachotronic'

# nombre del mp4 (x-<nombre>.mp4), segundo del fotograma, antetítulo, titular, enlace del tuit
VIDEOS = [
    dict(nombre='albiol', t=4, k='Badalona', titulo='Los 50.163 votos de Albiol en Badalona, y lo que valen el 29N', tuit=''),
    dict(nombre='listas-29n', t=8, k='Listas del 29N', titulo='4.031 candidatos al Congreso: 207 con el escaño en el aire', tuit=''),
    dict(nombre='inseguridad', t=8, k='Cataluña', titulo='La inseguridad ya preocupaba en Cataluña antes de los disturbios', tuit=''),
    dict(nombre='quien-vota', t=8, k='Participación', titulo='En los barrios ricos se vota 15 puntos más que en los pobres', tuit=''),
    dict(nombre='encuestas-hoy', t=8, k='Encuestas', titulo='El PP gana en 15 de 16 encuestadoras', tuit=''),
    dict(nombre='pactos', t=4, k='Investidura', titulo='176 síes para gobernar a la primera', tuit=''),
    dict(nombre='atlas-cizur', t=8, k='Atlas de las anomalías', titulo='Cizur y Zizur Mayor: a 1,4 km y 31 puntos de distancia', tuit=''),
    dict(nombre='comunidades', t=8, k='Comunidades', titulo='Aragón ha votado lo mismo que España en las 16 generales', tuit=''),
    dict(nombre='filo', t=4, k='Escaños en el filo', titulo='32 escaños que se movían con menos de 5.000 votos', tuit=''),
    dict(nombre='corrupcion', t=8, k='Corrupción y voto', titulo='¿Castiga la corrupción en las urnas?', tuit=''),
    dict(nombre='bastiones', t=4, k='Bastiones y desiertos', titulo='Del 93 % al 0 %: dónde arrasa y dónde no existe cada partido', tuit=''),
    dict(nombre='barrios-mitad', t=8, k='Abstención', titulo='534 barrios donde no votó ni la mitad del censo', tuit=''),
    dict(nombre='vox', t=8, k='Vox', titulo='Dónde vota Vox, del 43,7 % de El Ejido a cero votos', tuit=''),
    dict(nombre='mujeres-jovenes', t=1.5, k='Jóvenes', titulo='Los chicos jóvenes votaron a Vox más del triple que las chicas', tuit=''),
    dict(nombre='republica-1933-1936', t=8, k='Segunda República', titulo='1933, 1936 y hoy: el mapa de España pueblo a pueblo', tuit=''),
    dict(nombre='espana-1977-2023', t=8, k='Historia electoral', titulo='Todas las generales, de 1977 a 2023, pueblo a pueblo', tuit=''),
    dict(nombre='dhondt-cantabria', t=4, k="Ley D'Hondt", titulo="Así se reparten los escaños: la ley D'Hondt paso a paso", tuit=''),
]


def fotograma(v):
    """img/videos/<nombre>.jpg desde el mp4, si falta."""
    dest = ROOT / 'img' / 'videos' / f'{v["nombre"]}.jpg'
    mp4 = VIDEOS_DIR / f'x-{v["nombre"]}.mp4'
    if not dest.exists() and mp4.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(v['t']), '-i', str(mp4), '-frames:v', '1',
                        '-vf', 'scale=360:-2,crop=360:480:0:0', '-q:v', '4', str(dest)], check=True)
    return dest.exists()


def franja(pre=''):
    tarjetas = ''.join(
        f'<li><a href="{html.escape(v["tuit"] or PERFIL + "/media")}" target="_blank" rel="noopener">'
        f'<span class="dv-img"><img src="{pre}img/videos/{v["nombre"]}.jpg" alt="Fotograma del vídeo «{html.escape(v["titulo"])}»" loading="lazy" width="360" height="480"><i aria-hidden="true"></i></span>'
        f'<span class="atlas-k">{html.escape(v["k"])}</span><b>{html.escape(v["titulo"])}</b></a></li>'
        for v in VIDEOS if fotograma(v))
    return ('<section class="wide del-atlas del-videos" aria-labelledby="h-del-videos"><div class="da-cab"><h2 id="h-del-videos">'
            f'<a href="{PERFIL}" target="_blank" rel="noopener">Vídeos en X</a></h2>'
            '<span class="da-nav"><button type="button" class="da-prev" aria-label="Vídeos anteriores">←</button><button type="button" class="da-next" aria-label="Más vídeos">→</button></span></div>'
            f'<ul class="carrusel">{tarjetas}'
            f'<li class="todas"><a href="{PERFIL}" target="_blank" rel="noopener"><b>Todos los vídeos en X →</b><span>@nachotronic</span></a></li></ul>'
            '<style>.del-videos .carrusel{grid-auto-columns:minmax(170px,calc((100% - 80px)/6.3))}'
            '.del-videos .dv-img{position:relative;display:block;margin-bottom:6px}'
            '.del-videos .carrusel img{aspect-ratio:3/4;height:auto;margin:0;background:#0d1220}'
            '.del-videos .dv-img i{position:absolute;right:8px;bottom:8px;width:34px;height:34px;border-radius:50%;background:rgba(0,0,0,.6)}'
            '.del-videos .dv-img i::after{content:"";position:absolute;left:13px;top:10px;border-style:solid;border-width:7px 0 7px 12px;border-color:transparent transparent transparent #fff}'
            '.del-videos a:hover .dv-img i{background:rgba(0,0,0,.8)}.del-videos .carrusel b{font-size:15px}'
            '@media (max-width:760px){.del-videos .carrusel{grid-auto-columns:46%}}</style>'
            '<script>(s=>{const u=s.querySelector(".carrusel"),m=d=>()=>u.scrollBy({left:d*u.querySelector("li").offsetWidth*1.05,behavior:"smooth"});'
            's.querySelector(".da-prev").onclick=m(-1);s.querySelector(".da-next").onclick=m(1)})(document.currentScript.parentNode)</script></section>')


def portada():
    f = ROOT / 'index.html'
    t = f.read_text(encoding='utf-8')
    if '<!--videos:portada-->' not in t:   # justo debajo del carrusel de Actualidad
        t = t.replace('<!--/actualidad:ultimas-->', '<!--/actualidad:ultimas-->\n<!--videos:portada--><!--/videos:portada-->', 1)
    t = re.sub(r'<!--videos:portada-->.*?<!--/videos:portada-->',
               lambda m: '<!--videos:portada-->' + franja() + '<!--/videos:portada-->', t, flags=re.S)
    f.write_text(t, encoding='utf-8')


if __name__ == '__main__':
    portada()
