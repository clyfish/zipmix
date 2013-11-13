#!/bin/bash

BIN=`dirname $0`
[[ $# -ne 1 || ! -f "$1" ]] && echo "Usage: $0 zip_file" && exit 1

zip=`readlink -e "$1"`
pre_size=`stat -c"%s" "$zip"`
tmpdir=`mktemp -d`

cd "$tmpdir"
mkdir tmp
cd tmp
unzip "$zip" -x "*.jpg" "*.jpeg" "*.png" "*.gif" \
                "*.wav" "*.mp2" "*.mp3" "*.ogg" "*.aac" \
                "*.mpg" "*.mpeg" "*.mid" "*.midi" "*.smf" "*.jet" \
                "*.rtttl" "*.imy" "*.xmf" "*.mp4" "*.m4a" \
                "*.m4v" "*.3gp" "*.3gpp" "*.3g2" "*.3gpp2" \
                "*.amr" "*.awb" "*.wma" "*.wmv"
$BIN/kzip -r ../1.zip *
cd ..
$BIN/zipmix.py "$zip" 1.zip 2.zip
mv 2.zip "$zip"
rm -rf "$tmpdir"
