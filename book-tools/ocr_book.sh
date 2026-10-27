#!/bin/bash
# usage: ocr_book.sh <pdf> <name> <lang> [pagelist]
pdf="$1"; name="$2"; lang="$3"; pl="$4"; out=/home/claude/books/ocr/$name; mkdir -p $out
if [ -n "$pl" ]; then pages=$(cat /home/claude/books/scripts/$pl); else n=$(pdfinfo "$pdf" 2>/dev/null | awk '/^Pages/{print $2}'); pages=$(seq 1 $n); fi
echo "$pages" | xargs -P 3 -I{} /home/claude/books/scripts/ocr_page.sh "$pdf" "$out" "$lang" {}
echo "DONE $name $(ls $out/*.txt | wc -l)" >> /home/claude/books/ocr/progress.log
