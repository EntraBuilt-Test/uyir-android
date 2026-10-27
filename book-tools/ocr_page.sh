#!/bin/bash
# usage: ocr_page.sh <pdf> <outdir> <lang> <page>
pdf="$1"; out="$2"; lang="$3"; p="$4"
f=$(printf "%s/p%04d.txt" "$out" "$p"); [ -s "$f" ] && exit 0
export TESSDATA_PREFIX=/home/claude/tsd OMP_THREAD_LIMIT=1
tmp=$(mktemp -d /tmp/claude-0/ocrXXXX)
if [ "$lang" = tam ]; then case "$pdf" in *Science*|*_Zoology_Tamil*) r=160;; *) r=200;; esac; else r=150; fi
pdftoppm -f $p -l $p -r $r -gray -png "$pdf" "$tmp/x" 2>/dev/null
img=$(ls $tmp/x*.png 2>/dev/null | head -1)
if [ -n "$img" ]; then tesseract "$img" stdout -l $lang --psm 3 2>/dev/null | sed 's/\xe2\x80\x8c//g' > "$f.tmp" && mv "$f.tmp" "$f"; fi
rm -rf "$tmp"
