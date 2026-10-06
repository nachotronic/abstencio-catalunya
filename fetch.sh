set -u
mkdir -p out
for c in M20151 A20151 G20151 G20161 A20171 G20191 M20191 G20192 A20211 M20231 G20231 A20241; do
  curl -sS -m 300 -G "https://analisi.transparenciacatalunya.cat/resource/irrv-2mfc.csv" \
    --data-urlencode "\$select=territori_codi,territori_nom,districte,seccio,cens_electoral,votants" \
    --data-urlencode "\$where=id_eleccio='$c' AND id_nivell_territorial='SE'" \
    --data-urlencode "\$limit=50000" -o out/sec_$c.csv
  echo "$c $(wc -l < out/sec_$c.csv)" >> out/status.txt
done
mkdir -p cj
for d in 012023 072023 012024 072022; do
  code=$(curl -sSL -m 600 -A "Mozilla/5.0" -o cj/caj.zip -w "%{http_code}" "https://www.ine.es/prodyser/callejero/caj_esp/caj_esp_$d.zip" || echo ERR)
  echo "callejero $d $code $(stat -c %s cj/caj.zip 2>/dev/null)" >> out/status.txt
  if [ "$code" = "200" ] && unzip -tq cj/caj.zip >/dev/null 2>&1; then echo "usado $d" >> out/status.txt; break; fi
done
cd cj && unzip -o -q caj.zip && ls -la >> ../out/status.txt
for f in $(ls | grep -v caj.zip); do
  # solo Cataluña: provincias 08, 17, 25, 43 (dos primeros caracteres)
  grep -aE '^(08|17|25|43)' "$f" | gzip -9 > "../out/cat_$f.gz" || true
  head -c 600 "$f" > "../out/head_$f.txt"
done
cd ..; cat out/status.txt
