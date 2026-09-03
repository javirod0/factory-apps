#!/usr/bin/env bash
# Enlaza las skills de factory al directorio que descubre el harness.
# Symlinks, no copias: al cambiar la version de factory las skills se
# actualizan solas y no hay dos fuentes de verdad.
#
# Uso desde la raiz del repo de producto:  bash .factory/scripts/link-skills.sh

set -euo pipefail

FACTORY="${FACTORY_DIR:-.factory}"
TARGETS=("${@:-.claude/skills}")

if [ ! -d "$FACTORY/skills" ]; then
  echo "No encuentro $FACTORY/skills. Ejecutalo desde la raiz del repo de producto." >&2
  exit 1
fi

for target in "${TARGETS[@]}"; do
  mkdir -p "$target"
  for skill in "$FACTORY"/skills/*/; do
    [ -d "$skill" ] || continue
    name="$(basename "$skill")"
    link="$target/$name"
    [ -L "$link" ] && rm "$link"
    if [ -e "$link" ]; then
      echo "  saltando $link (existe y no es symlink)" >&2
      continue
    fi
    ln -s "$(cd "$skill" && pwd)" "$link"
    echo "  $link -> $skill"
  done
done

echo
echo "Listo. Reinicia el editor y comprueba en Customize > Skills"
echo "que aparece 'security-review'. Si no aparece, el enlazado fallo."
