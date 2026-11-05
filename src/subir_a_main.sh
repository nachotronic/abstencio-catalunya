#!/usr/bin/env bash
# Sube a main el commit que acaba de hacer un workflow automático (encuestas, listas, Bing).
# Desde el 4-11-2026 main exige el check «verificar» en verde, y el push directo del bot se rechazaba
# (GH006) porque ese check solo corre en los PR. Opción elegida por Nacho el 5-11-2026: el workflow pasa
# la MISMA comprobación (src/verificar_piezas.py contra origin/main) sobre el commit exacto que va a subir;
# solo si sale bien publica el estado «verificar» = success en ese commit y sube. Si la comprobación falla,
# no se sube nada y el job queda en rojo.
# Uso: GITHUB_TOKEN=... src/subir_a_main.sh [--theirs]   (--theirs: en un choque gana lo recién generado)
set -uo pipefail
estrategia=()
[[ "${1:-}" == "--theirs" ]] && estrategia=(-X theirs)
for i in 1 2 3; do
  if git pull --rebase "${estrategia[@]}" -q origin main; then
    sha=$(git rev-parse HEAD)
    resumen=()
    [[ -n "${GITHUB_STEP_SUMMARY:-}" ]] && resumen=(--resumen "$GITHUB_STEP_SUMMARY")
    if ! python3 src/verificar_piezas.py --base origin/main "${resumen[@]}"; then
      echo "::error::verificar_piezas.py ha fallado: no se sube nada a main"; exit 1
    fi
    # el API de estados solo acepta commits que ya están en GitHub: se sube antes a una rama temporal
    temporal="bot/subida-${GITHUB_RUN_ID:-local}-$i"
    git push -q origin "HEAD:refs/heads/$temporal" || { sleep 10; continue; }
    curl -fsS -X POST -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/$GITHUB_REPOSITORY/statuses/$sha" \
      -d "{\"state\":\"success\",\"context\":\"verificar\",\"description\":\"verificar_piezas.py en el workflow $GITHUB_WORKFLOW\",\"target_url\":\"$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID\"}" >/dev/null \
      || echo "::warning::no se pudo publicar el estado «verificar»"
    if git push origin HEAD:main; then git push -q origin --delete "$temporal" || true; exit 0; fi
    git push -q origin --delete "$temporal" || true
  fi
  git rebase --abort 2>/dev/null || true
  sleep 10
done
echo "::error::No se pudo subir la actualización a main"; exit 1
