#!/usr/bin/env bash
# Simulacro repetible del directo (para el 18-11 o cuando haga falta), sin Cloudflare:
# Interior simulado (respuestas reales del 23J) → worker.js → resultados.json y provincia/<pp>.json.
# Avanza el escrutinio 0 % → 30 % → 100 % y comprueba en cada paso que el Worker sirve datos coherentes.
# Uso, desde la raíz del repositorio:  bash generales-2026/src/directo/ensayo/simulacro.sh
# Con FUENTE=https://…/backend-difu prueba en cambio la web real de Interior (el día del simulacro oficial).
set -euo pipefail
cd "$(dirname "$0")"
T=$(mktemp -d); trap 'kill $(jobs -p) 2>/dev/null; rm -rf "$T"' EXIT
FUENTE=${FUENTE:-http://localhost:8899/backend-difu}
if [[ $FUENTE == http://localhost:8899/* ]]; then
  echo 0 > "$T/fraccion"
  node interior_simulado.mjs muestras_23j ../../../data/simulacro.json "$T/fraccion" > "$T/interior.log" 2>&1 &
  sleep 2
fi
CADA=5000 node worker_local.mjs ../worker.js "$FUENTE" > "$T/worker.log" 2>&1 &
comprueba () {   # $1 = fracción esperada (o vacío con la web real)
  python3 - "$1" <<'PY'
import json, sys, urllib.request
g = lambda p: json.load(urllib.request.urlopen('http://localhost:8787' + p))
T = g('/resultados.json'); P = g('/provincia/08.json')
mun = T['mun']; esc = sum(1 for a in mun.values() if a[1] > 0)
assert len(mun) > 8000, f'solo {len(mun)} municipios'
assert all(c.startswith('08') for c in P['mun']) and '08019' in P['mun'], 'la provincia 08 no trae Barcelona'
b = dict(zip(P['siglas'], P['mun']['08019'][5:])); bt = dict(zip(T['siglas'], T['mun']['08019'][5:]))
assert all(bt.get(s, 0) == v for s, v in b.items()) and sum(b.values()) == sum(bt.values()), 'provincia y total no cuadran'
f = sys.argv[1]
print(f"  {T['actualizado']}: {len(mun)} municipios, {esc} con escrutinio ({esc/len(mun):.0%}); provincia 08 {len(json.dumps(P))//1024} KB, total {len(json.dumps(T))//1024} KB")
if f: assert abs(esc / len(mun) - float(f)) < 0.08 + (0.25 if float(f) == 1 else 0), f'esperaba ~{f}'
PY
}
for f in 0 0.3 1; do
  [[ -f $T/fraccion ]] && echo $f > "$T/fraccion" || f=''
  sleep 7; echo "Escrutinio simulado: ${f:-web real}"; comprueba "$f"
done
echo "Peticiones a Interior: $(curl -s localhost:8899/backend-difu/peticiones 2>/dev/null || echo '(web real)')"
tail -3 "$T/worker.log"
echo 'Simulacro OK'
