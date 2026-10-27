#!/bin/bash
# Alternative to the GitHub workflow: create the signing key on your own computer (needs Java installed).
set -e
read -s -p "Choose a password for the key: " PW; echo
keytool -genkeypair -v -keystore uyir-release.jks -alias uyir -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass "$PW" -keypass "$PW" -dname "CN=Entraiot Solutions, O=Entraiot Solutions, L=Chennai, ST=Tamil Nadu, C=IN"
base64 -w0 uyir-release.jks > KEYSTORE_BASE64.txt 2>/dev/null || base64 -i uyir-release.jks -o KEYSTORE_BASE64.txt
echo "Done. Add these GitHub secrets: KEYSTORE_BASE64 (file KEYSTORE_BASE64.txt), KEYSTORE_PASSWORD, KEY_PASSWORD (your password), KEY_ALIAS = uyir"
